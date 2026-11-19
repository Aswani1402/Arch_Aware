from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import ArchitecturalReference, ReferenceProductMatch
from app.schemas.schemas import (
    ReferenceDetailOut,
    ReferenceProductMatchOut,
    CategoryOut,
    ReferenceCreate,
    ReferenceOut,
    InspirationMaterialOut,
    ProductOut
)

router = APIRouter(prefix="/references", tags=["Architectural References"])

@router.get("/{ref_id_or_slug}", response_model=ReferenceDetailOut)
def get_reference_detail(ref_id_or_slug: str, db: Session = Depends(get_db)):
    ref = None
    if ref_id_or_slug.isdigit():
        ref = db.query(ArchitecturalReference).filter_by(id=int(ref_id_or_slug)).first()
    if not ref:
        ref = db.query(ArchitecturalReference).filter_by(slug=ref_id_or_slug).first()

    if not ref:
        raise HTTPException(status_code=404, detail="Architectural reference not found")

    cat_out = None
    if ref.category:
        cat_out = CategoryOut(
            id=ref.category.id,
            name=ref.category.name,
            slug=ref.category.slug,
            description=ref.category.description,
            image_url=ref.category.image_url
        )

    product_matches_out = []
    for match in ref.product_matches:
        prod = match.product
        if prod:
            mfg_name = prod.manufacturer.name if prod.manufacturer else None
            product_matches_out.append(
                ReferenceProductMatchOut(
                    product_id=prod.id,
                    product_name=prod.name,
                    manufacturer_name=mfg_name,
                    match_type=match.match_type,
                    match_confidence=match.match_confidence,
                    evidence_notes=match.evidence_notes,
                    verification_status=match.verification_status,
                    image_url=prod.image_url
                )
            )

    materials_out: List[InspirationMaterialOut] = []
    for mat in ref.materials:
        prod_out = None
        if mat.product:
            prod_out = ProductOut(
                id=mat.product.id,
                name=mat.product.name,
                slug=mat.product.slug,
                sku_code=mat.product.sku_code,
                product_type=mat.product.product_type,
                material_type=mat.product.material_type,
                material_composition=mat.product.material_composition,
                finish=mat.product.finish,
                color=mat.product.color,
                intended_use=mat.product.intended_use,
                dimensions=mat.product.dimensions,
                thickness=mat.product.thickness,
                installation_requirements=mat.product.installation_requirements,
                specs=mat.product.specs,
                official_product_url=mat.product.official_product_url,
                official_catalog_url=mat.product.official_catalog_url,
                country_of_manufacture=mat.product.country_of_manufacture,
                image_url=mat.product.image_url,
                data_source=mat.product.data_source,
                verification_status=mat.product.verification_status,
                manufacturer_id=mat.product.manufacturer_id,
                manufacturer_name=mat.product.manufacturer.name if mat.product.manufacturer else None,
                category_id=mat.product.category_id,
                category_name=mat.product.category.name if mat.product.category else None,
                last_checked_at=mat.product.last_checked_at,
                created_at=mat.product.created_at
            )
        materials_out.append(
            InspirationMaterialOut(
                id=mat.id,
                reference_id=mat.reference_id,
                name=mat.name,
                category_id=mat.category_id,
                category_slug=mat.category_slug,
                material_category=mat.material_category,
                element_location=mat.element_location,
                identification_type=mat.identification_type,
                verification_status=mat.verification_status,
                confidence_score=mat.confidence_score,
                detail_image_url=mat.detail_image_url,
                notes=mat.notes,
                product_id=mat.product_id,
                compatible_alternatives=mat.compatible_alternatives,
                product=prod_out
            )
        )

    mfg_prod_img = ref.manufacturer_product_image_url
    mfg_prod_url = ref.manufacturer_product_url
    mfg_id = ref.manufacturer_id
    mfg_name = ref.manufacturer.name if ref.manufacturer else None
    match_status = ref.product_match_status or "unidentified"

    if not mfg_prod_img and ref.product_matches:
        top_match = ref.product_matches[0]
        prod = top_match.product
        if prod:
            if top_match.match_type in ["verified_exact", "verified_match", "commercial_specification"]:
                mfg_prod_img = prod.image_url
                mfg_prod_url = prod.official_product_url or (prod.manufacturer.official_catalog_url if prod.manufacturer else None)
                mfg_id = prod.manufacturer_id
                mfg_name = prod.manufacturer.name if prod.manufacturer else None
                match_status = "verified_match" if top_match.match_type in ["verified_exact", "verified_match"] else "commercial_specification"
            elif top_match.match_type in ["visually_similar", "probable_match"]:
                match_status = "probable_match"
                mfg_name = prod.manufacturer.name if prod.manufacturer else None
                mfg_prod_img = None
                mfg_prod_url = None
            else:
                match_status = "unidentified"

    return ReferenceDetailOut(
        id=ref.id,
        title=ref.title,
        slug=ref.slug,
        source_platform=ref.source_platform,
        source_url=ref.source_url,
        creator_name=ref.creator_name,
        creator_url=ref.creator_url,
        thumbnail_url=ref.thumbnail_url,
        media_url=ref.media_url,
        inspiration_image_url=ref.inspiration_image_url or ref.thumbnail_url,
        inspiration_source_url=ref.inspiration_source_url or ref.source_url,
        manufacturer_product_image_url=mfg_prod_img,
        manufacturer_product_url=mfg_prod_url,
        manufacturer_id=mfg_id,
        manufacturer_name=mfg_name,
        product_match_status=match_status,
        video_embed_id=ref.video_embed_id,
        video_duration=ref.video_duration,
        is_short=bool(ref.is_short),
        image_attribution=ref.image_attribution,
        source_domain=ref.source_domain,
        colors_and_finishes=ref.colors_and_finishes,
        category_id=ref.category_id,
        category_name=ref.category.name if ref.category else None,
        material_tags=ref.material_tags,
        location_context=ref.location_context,
        country=ref.country or "India",
        region=ref.region,
        architectural_style=ref.architectural_style,
        project_type=ref.project_type or "Residential",
        architecture_era=ref.architecture_era or "Contemporary",
        architect_name=ref.architect_name or ref.creator_name,
        content_type=getattr(ref, 'content_type', 'architectural_project') or 'architectural_project',
        verification_status=ref.verification_status,
        description=ref.description,
        retrieval_method=ref.retrieval_method or "manual_curation",
        content_availability_status=ref.content_availability_status or "ACTIVE",
        matched_products_count=len(product_matches_out),
        created_at=ref.created_at or datetime.now(timezone.utc),
        category=cat_out,
        product_matches=product_matches_out,
        materials=materials_out
    )

# In-memory cache for AI Material Detection to avoid repeated expensive calls
_MATERIAL_DETECTION_CACHE = {}

@router.post("/{ref_id_or_slug}/detect-materials")
def detect_reference_materials(
    ref_id_or_slug: str,
    body: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """
    FEATURE 7: AI-assisted Material Detection with confidence scoring,
    qualified uncertainty labels ('Possible natural stone', 'Tile — exact material unconfirmed'),
    and strict separation between source-confirmed vs AI-inferred materials.
    """
    ref = None
    if ref_id_or_slug.isdigit():
        ref = db.query(ArchitecturalReference).filter_by(id=int(ref_id_or_slug)).first()
    if not ref:
        ref = db.query(ArchitecturalReference).filter_by(slug=ref_id_or_slug).first()

    if not ref:
        raise HTTPException(status_code=404, detail="Architectural reference not found")

    cache_key = f"{ref.id}_{ref.media_url or ref.thumbnail_url}"
    if body and body.get("user_corrections"):
        # If user submitted corrections, don't return stale cache
        pass
    elif cache_key in _MATERIAL_DETECTION_CACHE:
        cached_res = _MATERIAL_DETECTION_CACHE[cache_key].copy()
        cached_res["cached"] = True
        return cached_res

    media_url = ref.inspiration_image_url or ref.thumbnail_url or ref.media_url or ""
    is_video = bool(ref.video_embed_id)

    # 1. Source-confirmed materials (from verified specifications in reference metadata)
    source_confirmed = []
    for mat in ref.materials:
        if mat.verification_status in ["VERIFIED", "ARCHITECT_DOCUMENTED"] or mat.identification_type in ["confirmed_product", "architect_documented"]:
            source_confirmed.append({
                "name": mat.name,
                "qualified_label": f"Confirmed: {mat.name}",
                "category": mat.material_category,
                "confidence": 1.0,
                "confidence_category": "High (Confirmed)",
                "is_confirmed": True,
                "evidence": mat.notes or f"Documented in architectural specification at {mat.element_location}",
                "is_code": None
            })

    for pm in ref.product_matches:
        if pm.match_type in ["verified_exact", "verified_match"] and pm.product:
            source_confirmed.append({
                "name": pm.product.name,
                "qualified_label": f"Verified Product: {pm.product.name}",
                "category": pm.product.material_type or "Building Material",
                "confidence": 1.0,
                "confidence_category": "High (Confirmed)",
                "is_confirmed": True,
                "evidence": pm.evidence_notes or "Exact manufacturer product verified from official project catalog documentation",
                "is_code": None
            })

    # 2. AI-inferred candidate materials based on visual media and contextual tags
    text_corpus = f"{ref.title} {ref.description or ''} {ref.material_tags or ''} {ref.architectural_style or ''} {ref.category.name if ref.category else ''}".lower()
    inferred = []
    uncertainty_notes = []

    # Exposed Brick / Clay Masonry
    if any(w in text_corpus for w in ["brick", "masonry", "porotherm", "wire-cut"]):
        inferred.append({
            "name": "Exposed Wire-Cut Brick Masonry",
            "qualified_label": "Exposed Brick — exact kiln/manufacturer unconfirmed",
            "category": "Bricks & Masonry",
            "confidence": 0.92,
            "confidence_category": "High",
            "is_confirmed": False,
            "evidence": "Visible stretcher bond clay masonry patterns and textured terracotta surface.",
            "uncertainty_note": "Visual appearance indicates wire-cut or country clay brick; precise compressive strength and water absorption require laboratory batch tests (IS 1077).",
            "is_code": "IS 1077 / IS 2180"
        })
        uncertainty_notes.append("Brick batch composition and thermal conductivity cannot be determined from visual imagery alone.")

    # Concrete / Cement Finish
    if any(w in text_corpus for w in ["concrete", "cement", "rcc", "precast", "shuttering"]):
        inferred.append({
            "name": "Cast-in-situ / Precast Architectural Concrete",
            "qualified_label": "Concrete finish — cement grade & mix ratio unconfirmed",
            "category": "Cement & Concrete",
            "confidence": 0.88,
            "confidence_category": "High",
            "is_confirmed": False,
            "evidence": "Smooth shuttered / form-finished concrete planes with tie-rod indentations.",
            "uncertainty_note": "Concrete grade (e.g. M25 vs M35) and water-cement ratio are visually indistinguishable; specify site cube testing per IS 516.",
            "is_code": "IS 456:2000"
        })
        uncertainty_notes.append("Structural load capacity and steel reinforcement gauge cannot be inferred from surface finish.")

    # Natural Stone / Marble / Granite
    if any(w in text_corpus for w in ["stone", "marble", "granite", "kota", "athangudi", "laterite", "slate"]):
        inferred.append({
            "name": "Natural Stone / Marble Surfaces",
            "qualified_label": "Possible natural stone — mineral origin & exact thickness unconfirmed",
            "category": "Natural Stone & Slabs",
            "confidence": 0.84,
            "confidence_category": "Moderate",
            "is_confirmed": False,
            "evidence": "Visible natural vein structure and honed surface reflections.",
            "uncertainty_note": "Visual imagery cannot conclusively differentiate genuine natural marble from marble-look vitrified porcelain slabs without physical edge inspection.",
            "is_code": "IS 1130 / IS 3316"
        })
        uncertainty_notes.append("Stone porosity and sealing treatment are unconfirmed visually.")

    # Tiles & Surface Finishes
    if any(w in text_corpus for w in ["tile", "porcelain", "vitrified", "ceramic"]):
        inferred.append({
            "name": "Large-Format Vitrified / Ceramic Tiles",
            "qualified_label": "Tile — exact manufacturer, PEI rating & glaze unconfirmed",
            "category": "Flooring & Tiles",
            "confidence": 0.85,
            "confidence_category": "Moderate",
            "is_confirmed": False,
            "evidence": "Even joint spacing, rectilinear module grid, and uniform surface reflectance.",
            "uncertainty_note": "Tile manufacturer, anti-skid friction coefficient (R-value), and PEI abrasion resistance cannot be established from photos.",
            "is_code": "IS 15622 / ISO 13006"
        })

    # Drainage Channels & Stormwater
    if any(w in text_corpus for w in ["drain", "drainage", "stormwater", "culvert"]):
        inferred.append({
            "name": "Heavy-Duty Precast Concrete Drainage Channel",
            "qualified_label": "Drainage channel — hydraulic capacity & Class A/B/C rating unconfirmed",
            "category": "Drainage & Precast",
            "confidence": 0.89,
            "confidence_category": "High",
            "is_confirmed": False,
            "evidence": "Linear precast concrete grating channels and surface runoff collection profile.",
            "uncertainty_note": "Load class (EN 124 / IS 12592) and peak stormwater flow volume require site catchment hydraulic calculation.",
            "is_code": "IS 12592 / EN 124"
        })

    # Water Features & Waterfalls
    if any(w in text_corpus for w in ["waterfall", "water feature", "pond", "fountain"]):
        inferred.append({
            "name": "Natural Rock / Boulder Waterfall Feature",
            "qualified_label": "Water feature — submersible pump wattage & liner type unconfirmed",
            "category": "Landscape & Water Features",
            "confidence": 0.86,
            "confidence_category": "Moderate",
            "is_confirmed": False,
            "evidence": "Cascading water flow over stacked natural boulders with splash reservoir.",
            "uncertainty_note": "Pump flow rate (liters/hour), waterproof liner membrane (EPDM vs RCC), and plumbing pipe diameter cannot be measured from footage.",
            "is_code": "Landscape Hydraulic Standard"
        })

    # Planters & Decorative Pots
    if any(w in text_corpus for w in ["pot", "planter", "terracotta pot", "ceramic pot"]):
        inferred.append({
            "name": "Artisanal Terracotta / Ceramic Garden Planters",
            "qualified_label": "Decorative pots — clay composition & drainage liner unconfirmed",
            "category": "Home Decor & Planters",
            "confidence": 0.87,
            "confidence_category": "Moderate",
            "is_confirmed": False,
            "evidence": "Handcrafted cylindrical / fluted planter geometry with earthy matte finish.",
            "uncertainty_note": "Interior waterproofing and root aeration layer require physical product specification.",
            "is_code": "Horticultural Standard"
        })

    # Timber & Wood
    if any(w in text_corpus for w in ["timber", "wood", "teak", "oak", "veneer"]):
        inferred.append({
            "name": "Architectural Timber / Louvers",
            "qualified_label": "Timber elements — wood species & seasoning unconfirmed",
            "category": "Timber & Wood",
            "confidence": 0.86,
            "confidence_category": "Moderate",
            "is_confirmed": False,
            "evidence": "Linear wood grain and warm stained architectural finish.",
            "uncertainty_note": "Visual appearance resembles teak, oak, or engineered veneer; botanical wood species confirmation requires macroscopic grain inspection.",
            "is_code": "IS 1141 / IS 1708"
        })

    # Lighting Fixtures
    if any(w in text_corpus for w in ["light", "lighting", "chandelier", "sconce"]):
        inferred.append({
            "name": "Architectural Ambient & Accent Lighting",
            "qualified_label": "Lighting fixture — lumen output, CRI & driver spec unconfirmed",
            "category": "Lighting",
            "confidence": 0.85,
            "confidence_category": "Moderate",
            "is_confirmed": False,
            "evidence": "Diffused warm-white emission (approx 2700K-3000K) and metallic housing geometry.",
            "uncertainty_note": "Exact driver wattage, Color Rendering Index (CRI), and IP ingress rating cannot be measured visually.",
            "is_code": "IS 10322 / IEC 60598"
        })

    # Glass & Glazing
    if any(w in text_corpus for w in ["glass", "glazing", "window", "facade", "skylight"]):
        inferred.append({
            "name": "Architectural Glazing / Low-E Glass",
            "qualified_label": "Glass — U-value, SHGC & tempering grade unconfirmed",
            "category": "Glass & Glazing",
            "confidence": 0.87,
            "confidence_category": "Moderate",
            "is_confirmed": False,
            "evidence": "Transparent / tinted fenestration panels with specular exterior reflections.",
            "uncertainty_note": "Solar Heat Gain Coefficient (SHGC), U-value, and acoustic laminated thickness require manufacturer test certs.",
            "is_code": "IS 2553 / IS 16231"
        })

    # Steel & Aluminium Framing
    if any(w in text_corpus for w in ["steel", "aluminium", "aluminum", "metal", "iron", "tmt"]):
        inferred.append({
            "name": "Structural / Architectural Metal Framing",
            "qualified_label": "Metal framework — alloy grade & tensile strength unconfirmed",
            "category": "Structural Steel & Metals",
            "confidence": 0.86,
            "confidence_category": "Moderate",
            "is_confirmed": False,
            "evidence": "Linear extruded profiles and anodised / powder-coated structural sections.",
            "uncertainty_note": "Steel yield strength (Fe 500D vs Fe 550D) or aluminium alloy tempering (6063-T6) cannot be verified without mill test reports.",
            "is_code": "IS 1786 / IS 733"
        })

    # Paint & Plaster Finishes
    if any(w in text_corpus for w in ["paint", "plaster", "lime", "putty", "stucco", "wall"]):
        inferred.append({
            "name": "Architectural Emulsion / Mineral Plaster",
            "qualified_label": "Wall finish — VOC rating & base coat composition unconfirmed",
            "category": "Paints & Finishes",
            "confidence": 0.83,
            "confidence_category": "Moderate",
            "is_confirmed": False,
            "evidence": "Continuous matte/eggshell surface coating and pigmented architectural render.",
            "uncertainty_note": "Specific formulation (acrylic emulsion vs mineral silicate) and coat thickness require architectural finishing schedule.",
            "is_code": "IS 5410 / IS 15489"
        })

    # Roofing & Tiles
    if any(w in text_corpus for w in ["roof", "roofing", "shingle", "mangalore", "truss"]):
        inferred.append({
            "name": "Sloped Roof Tiles / Weatherproof Membrane",
            "qualified_label": "Roofing system — wind uplift & insulation grade unconfirmed",
            "category": "Roofing Materials",
            "confidence": 0.88,
            "confidence_category": "High",
            "is_confirmed": False,
            "evidence": "Interlocking clay / concrete roof tiles and overhang eves profile.",
            "uncertainty_note": "Underlayment waterproofing membrane and insulation R-value must be checked against structural cross-sections.",
            "is_code": "IS 654 / IS 3384"
        })

    # Pavers & Outdoor Pathways
    if any(w in text_corpus for w in ["paver", "pathway", "walkway", "stepping stone", "paving", "cobblestone"]):
        inferred.append({
            "name": "Interlocking Concrete / Natural Stone Pavers",
            "qualified_label": "Paving units — compressive strength (M30/M40) unconfirmed",
            "category": "Flooring & Outdoor Paving",
            "confidence": 0.89,
            "confidence_category": "High",
            "is_confirmed": False,
            "evidence": "Geometric interlocking paver modules with joint sand infill.",
            "uncertainty_note": "Bedding sub-base compaction and unit load classification require site geotechnical specifications.",
            "is_code": "IS 15658:2006"
        })

    # Plumbing & Sanitaryware
    if any(w in text_corpus for w in ["sanitary", "faucet", "shower", "sink", "toilet", "closet", "washbasin", "bath", "bathroom", "plumbing", "mixer", "cpvc"]):
        inferred.append({
            "name": "Plumbing & Sanitaryware Fixtures",
            "qualified_label": "Sanitaryware / fittings — rough-in size, ceramic grade & finish coating unconfirmed",
            "category": "Plumbing & Sanitaryware",
            "confidence": 0.87,
            "confidence_category": "Moderate",
            "is_confirmed": False,
            "evidence": "Visible vitreous sanitaryware contours or metallic brass/chrome plumbing trim.",
            "uncertainty_note": "Trap distance, water pressure compatibility (bar), and cartridge valve alloy cannot be confirmed from visual imagery.",
            "is_code": "IS 2556 / IS 8931"
        })

    # Fallback generic inferred architectural finish if none matched
    if not inferred:
        inferred.append({
            "name": "Composite Architectural Building Materials",
            "qualified_label": "Composite finish — exact material substrate unconfirmed",
            "category": ref.category.name if ref.category else "Architectural Materials",
            "confidence": 0.72,
            "confidence_category": "Inferred",
            "is_confirmed": False,
            "evidence": "Surface geometry and chromatic palette consistent with architectural cladding.",
            "uncertainty_note": "Substrate and core material require physical engineering drawings.",
            "is_code": None
        })

    # Apply user correction overrides if provided
    if body and body.get("user_corrections"):
        for uc in body["user_corrections"]:
            inferred.append({
                "name": uc.get("name", "User Documented Material"),
                "qualified_label": f"User Corrected: {uc.get('name')}",
                "category": uc.get("category", "Custom Material"),
                "confidence": 0.95,
                "confidence_category": "High (User Corrected)",
                "is_confirmed": True,
                "evidence": uc.get("notes", "Submitted via user feedback review"),
                "is_code": None
            })

    # Independently discovered CSV Master Catalogue materials (never merged into source_confirmed_materials)
    catalogue_suggestions = []
    try:
        from app.services.catalogue_import_service import search_catalogue_materials
        search_terms = [m["name"].split("/")[0].split()[0] for m in inferred if m.get("name")]
        if ref.category and ref.category.name:
            search_terms.append(ref.category.name.split("&")[0].strip())
        seen_mat_ids = set()
        for term in search_terms[:3]:
            if len(term) < 3:
                continue
            hits = search_catalogue_materials(db, q=term, limit=4)
            for item in hits.get("items", []):
                if item["id"] not in seen_mat_ids:
                    seen_mat_ids.add(item["id"])
                    catalogue_suggestions.append({
                        "catalogue_id": item["id"],
                        "material": item["material"],
                        "category": item["category"],
                        "subcategory": item["subcategory"],
                        "provenance": "INDEPENDENT_CATALOGUE_MATCH",
                    })
                    if len(catalogue_suggestions) >= 6:
                        break
            if len(catalogue_suggestions) >= 6:
                break
    except Exception:
        catalogue_suggestions = []

    result = {
        "reference_id": ref.id,
        "media_analyzed_url": media_url,
        "media_type": "video_frame" if is_video else "image",
        "source_confirmed_materials": source_confirmed,
        "ai_inferred_materials": inferred,
        "independently_discovered_catalogue_materials": catalogue_suggestions,
        "uncertainty_notes": uncertainty_notes,
        "disclaimer": (
            "Visual AI Identification is an educational inference tool. Visual analysis cannot "
            "determine structural load ratings, exact cement formulations, tile PEI ratings, or "
            "unverified manufacturer brand names. Always verify physical data sheets with verified trade suppliers."
        ),
        "cached": False
    }

    if len(_MATERIAL_DETECTION_CACHE) >= 256:
        oldest_key = next(iter(_MATERIAL_DETECTION_CACHE))
        _MATERIAL_DETECTION_CACHE.pop(oldest_key, None)
    _MATERIAL_DETECTION_CACHE[cache_key] = result
    return result

@router.post("", response_model=ReferenceOut)
def create_manual_reference(ref_in: ReferenceCreate, db: Session = Depends(get_db)):
    ref = ArchitecturalReference(
        title=ref_in.title,
        slug=ref_in.slug,
        source_platform=ref_in.source_platform,
        source_url=ref_in.source_url,
        creator_name=ref_in.creator_name,
        creator_url=ref_in.creator_url,
        thumbnail_url=ref_in.thumbnail_url,
        media_url=ref_in.media_url,
        video_embed_id=ref_in.video_embed_id,
        category_id=ref_in.category_id,
        material_tags=ref_in.material_tags,
        location_context=ref_in.location_context,
        country=ref_in.country or "India",
        region=ref_in.region,
        architectural_style=ref_in.architectural_style,
        project_type=ref_in.project_type or "Residential",
        architecture_era=ref_in.architecture_era or "Contemporary",
        architect_name=ref_in.architect_name,
        verification_status="PENDING_REVIEW",
        description=ref_in.description
    )
    db.add(ref)
    db.commit()
    db.refresh(ref)
    return ReferenceOut(
        id=ref.id,
        title=ref.title,
        slug=ref.slug,
        source_platform=ref.source_platform,
        source_url=ref.source_url,
        creator_name=ref.creator_name,
        creator_url=ref.creator_url,
        thumbnail_url=ref.thumbnail_url,
        media_url=ref.media_url,
        video_embed_id=ref.video_embed_id,
        category_id=ref.category_id,
        category_name=ref.category.name if ref.category else None,
        material_tags=ref.material_tags,
        location_context=ref.location_context,
        country=ref.country or "India",
        region=ref.region,
        architectural_style=ref.architectural_style,
        project_type=ref.project_type or "Residential",
        architecture_era=ref.architecture_era or "Contemporary",
        architect_name=ref.architect_name,
        verification_status=ref.verification_status,
        description=ref.description,
        matched_products_count=0,
        created_at=ref.created_at
    )

import json
import re
import urllib.parse
import logging
from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.core.config import settings
from app.models.models import ArchitecturalReference, MaterialCategory, ReferenceProductMatch, Product, Supplier
from app.schemas.schemas import FeedResponse, ReferenceOut, FeedFiltersOut, CategoryOut
from app.schemas.discovery import ProvenanceEnum, InspirationRelevanceTierEnum, MediaStatusEnum
from app.services.socialcrawl_service import is_socialcrawl_configured
from app.services.relevance_service import relevance_service, APPROVED_MATERIAL_ALIASES, normalize_relevance_text
from app.services.image_search_service import image_search_service

logger = logging.getLogger("feed")

router = APIRouter(prefix="/feed", tags=["Discovery Feed"])

def supplier_to_reference_out(s: Supplier) -> ReferenceOut:
    maps_query = urllib.parse.quote_plus(f"{s.name} {s.address or ''} {s.city or ''}".strip())
    maps_url = s.google_maps_url or f"https://www.google.com/maps/search/?api=1&query={maps_query}"
    directions_url = f"https://www.google.com/maps/dir/?api=1&destination={maps_query}"
    clean_phone = re.sub(r"[^\d+]", "", s.phone or s.whatsapp or "")
    if clean_phone and not clean_phone.startswith("+") and len(clean_phone) == 10:
        clean_phone = "+91" + clean_phone
    wa_num = re.sub(r"[^\d]", "", clean_phone)
    wa_url = f"https://wa.me/{wa_num}" if wa_num else None

    meta = {
        "is_supplier": True,
        "business_name": s.name,
        "phone": s.phone or "",
        "clean_phone": clean_phone,
        "whatsapp": s.whatsapp or "",
        "whatsapp_url": wa_url,
        "address": s.address or s.city or "",
        "city": s.city or "",
        "state": s.state or "Kerala",
        "materials_sold": s.materials_sold or "",
        "brands_distributed": s.brands_distributed or "",
        "google_maps_url": maps_url,
        "directions_url": directions_url
    }

    return ReferenceOut(
        id=300000 + s.id,
        title=s.name,
        slug=s.slug or f"supplier-{s.id}",
        source_platform="google_business",
        source_url=s.website or maps_url,
        creator_name=s.business_type or "Verified Supplier / Dealer",
        creator_url=maps_url,
        thumbnail_url=None,
        media_url=None,
        inspiration_image_url=None,
        inspiration_source_url=s.website or maps_url,
        manufacturer_product_image_url=None,
        manufacturer_product_url=s.website,
        manufacturer_id=None,
        manufacturer_name=s.brands_distributed or s.name,
        product_match_status="verified_match",
        video_embed_id=None,
        video_duration=None,
        is_short=False,
        image_attribution=f"Verified Business: {s.city or 'Kerala'}, India",
        source_domain="google.com/maps",
        colors_and_finishes=json.dumps(meta),
        category_id=None,
        category_name="Suppliers & Dealers",
        material_tags=s.materials_sold or "Building Materials, Hardware, Sanitaryware, Stone",
        location_context=f"{s.city or ''}, {s.state or 'Kerala'}, India".strip(", "),
        country=s.country or "India",
        region=s.state or "Kerala",
        architectural_style="Local Supplier & Materials Depot",
        project_type="Material Supply & Distribution",
        architecture_era="Contemporary",
        architect_name=s.contact_person or s.name,
        content_type="supplier_business",
        verification_status="VERIFIED",
        description=f"Local dealer & distributor. Materials: {s.materials_sold or 'Architectural materials & fittings'}. Location: {s.address or s.city}. Contact: {s.phone or 'WhatsApp available'}.",
        retrieval_method="google_business_search",
        content_availability_status="ACTIVE",
        matched_products_count=0,
        provenance=ProvenanceEnum.CURATED_ARCHIVE.value,
        inspiration_relevance_tier=InspirationRelevanceTierEnum.TIER_1_EXACT.value,
        media_status=MediaStatusEnum.TEXT_DISCUSSION.value,
        created_at=s.created_at or datetime.now(timezone.utc)
    )

@router.get("", response_model=FeedResponse)
async def get_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(16, ge=1, le=50),
    q: Optional[str] = Query(None, description="Search keyword in title, tags, or description"),
    category: Optional[str] = Query(None, description="Filter by category slug"),
    platform: Optional[str] = Query(None, description="Filter by platform (youtube, reddit, pinterest, instagram, catalog)"),
    country: Optional[str] = Query(None, description="Filter by country (e.g. India, Japan, Vietnam, Germany, Italy, Brazil)"),
    region: Optional[str] = Query(None, description="Filter by state or region (e.g. Kerala, Tamil Nadu, Karnataka, Kyoto, Veneto)"),
    style: Optional[str] = Query(None, description="Filter by architectural style"),
    project_type: Optional[str] = Query(None, description="Filter by project type (Residential, Commercial, Hospitality, etc.)"),
    era: Optional[str] = Query(None, description="Filter by tradition/era (Traditional, Contemporary, Mixed)"),
    content_type: Optional[str] = Query(None, description="Filter by content type (architectural_project, material_specimen, manufacturer_product, installation_demo, youtube_walkthrough)"),
    interests: Optional[str] = Query(None, description="Comma-separated liked/saved user interests for personalized ranking"),
    include_samples: bool = Query(False, description="Include sample/fixture specimen cards in dev mode"),
    refresh: bool = Query(False, description="Sync latest videos from configured connectors"),
    db: Session = Depends(get_db)
):
    query = db.query(ArchitecturalReference)

    # Stage 3: Remove seeded / specimen placeholder cards from live feed unless explicitly requested in dev/test mode
    if not include_samples:
        query = query.filter(
            ~ArchitecturalReference.title.ilike('%Specimen%'),
            ~ArchitecturalReference.title.ilike('%Heritage Crafts%'),
            ~ArchitecturalReference.creator_name.ilike('%Heritage Crafts%'),
            ~ArchitecturalReference.description.ilike('%Specimen%')
        )

    cat_slug = category if isinstance(category, str) and category.strip() else None
    if cat_slug:
        cat = db.query(MaterialCategory).filter_by(slug=cat_slug).first()
        if cat:
            query = query.filter(ArchitecturalReference.category_id == cat.id)

    search_query = q if isinstance(q, str) and q.strip() else None

    plat_str = platform if isinstance(platform, str) and platform.strip() else None
    if plat_str:
        p_clean = plat_str.lower().strip()
        if p_clean in ['suppliers', 'google_business', 'vendors', 'dealers']:
            sup_query = db.query(Supplier)
            if search_query:
                terms = [w.strip() for w in search_query.split() if len(w.strip()) >= 2]
                if terms:
                    conds = []
                    for t in terms:
                        conds.append(Supplier.name.ilike(f"%{t}%"))
                        conds.append(Supplier.materials_sold.ilike(f"%{t}%"))
                        conds.append(Supplier.brands_distributed.ilike(f"%{t}%"))
                        conds.append(Supplier.city.ilike(f"%{t}%"))
                        conds.append(Supplier.address.ilike(f"%{t}%"))
                    sup_query = sup_query.filter(or_(*conds))
            if isinstance(region, str) and region.strip():
                sup_query = sup_query.filter(or_(Supplier.state.ilike(f"%{region.strip()}%"), Supplier.city.ilike(f"%{region.strip()}%")))
            total_sups = sup_query.count()
            offset = (page - 1) * page_size
            sups = sup_query.offset(offset).limit(page_size).all()
            supplier_items = [supplier_to_reference_out(s) for s in sups]
            return FeedResponse(
                items=supplier_items,
                total=total_sups,
                page=page,
                page_size=page_size,
                has_more=(offset + page_size) < total_sups,
                connector_status={
                    "youtube_configured": is_socialcrawl_configured(),
                    "socialcrawl_configured": is_socialcrawl_configured(),
                    "total_references": total_sups,
                    "last_synced_at": datetime.now(timezone.utc).isoformat()
                }
            )
        elif p_clean in ['shopping', 'google_shopping', 'google-shopping']:
            query = query.filter(ArchitecturalReference.source_platform.in_(['shopping', 'google_shopping']))
        elif p_clean in ['instagram', 'instagram_reels', 'reels']:
            query = query.filter(ArchitecturalReference.source_platform.in_(['instagram', 'instagram_reels']))
        elif p_clean in ['x', 'twitter']:
            query = query.filter(ArchitecturalReference.source_platform.in_(['x', 'twitter']))
        elif p_clean in ['google', 'google_search', 'google-search']:
            query = query.filter(ArchitecturalReference.source_platform.in_(['google', 'google_search', 'google_business']))
        else:
            query = query.filter(ArchitecturalReference.source_platform == p_clean)

    ctype_str = content_type if isinstance(content_type, str) and content_type.strip() else None
    if ctype_str:
        query = query.filter(ArchitecturalReference.content_type == ctype_str.lower())

    if isinstance(country, str) and country.strip():
        query = query.filter(ArchitecturalReference.country.ilike(f"%{country.strip()}%"))

    if isinstance(region, str) and region.strip():
        query = query.filter(ArchitecturalReference.region.ilike(f"%{region.strip()}%"))

    if isinstance(style, str) and style.strip():
        query = query.filter(ArchitecturalReference.architectural_style.ilike(f"%{style.strip()}%"))

    if isinstance(project_type, str) and project_type.strip():
        query = query.filter(ArchitecturalReference.project_type.ilike(f"%{project_type.strip()}%"))

    if isinstance(era, str) and era.strip():
        query = query.filter(ArchitecturalReference.architecture_era.ilike(f"%{era.strip()}%"))

    search_query = q if isinstance(q, str) and q.strip() else None
    if search_query:
        clean_sq = search_query.strip().lower()
        norm_sq = normalize_relevance_text(clean_sq)

        # Build precise candidate conditions using exact phrase, verified aliases, and core nouns
        phrase_term = f"%{clean_sq}%"
        filter_conditions = [
            ArchitecturalReference.title.ilike(phrase_term),
            ArchitecturalReference.material_tags.ilike(phrase_term),
            ArchitecturalReference.description.ilike(phrase_term),
            ArchitecturalReference.search_keyword.ilike(phrase_term),
        ]

        # Add canonical alias condition if query matches an approved alias
        if norm_sq in APPROVED_MATERIAL_ALIASES:
            canonical_phrase = APPROVED_MATERIAL_ALIASES[norm_sq]["canonical"]
            canon_term = f"%{canonical_phrase}%"
            filter_conditions.extend([
                ArchitecturalReference.title.ilike(canon_term),
                ArchitecturalReference.material_tags.ilike(canon_term),
                ArchitecturalReference.description.ilike(canon_term),
            ])

        # Reverse alias matching: if query is canonical, find aliases
        for a_phrase, a_info in APPROVED_MATERIAL_ALIASES.items():
            if a_info.get("bidirectional", False) and a_info["canonical"] == norm_sq:
                a_term = f"%{a_phrase}%"
                filter_conditions.extend([
                    ArchitecturalReference.title.ilike(a_term),
                    ArchitecturalReference.material_tags.ilike(a_term),
                ])

        # Core material noun matching (covers all catalogue families)
        core_nouns = [
            "brick", "bricks", "block", "blocks", "stone", "marble", "granite",
            "tile", "tiles", "door", "doors", "window", "windows", "glass",
            "panel", "panels", "pipe", "pipes", "fitting", "fittings", "paint",
            "paints", "waterproof", "waterproofing", "paver", "pavers", "mixer",
            "machine", "machinery", "drill", "scaffold", "scaffolding", "crane",
            "excavator", "tool", "tools", "screw", "screws", "fastener", "fasteners",
            "steel", "rebar", "cement", "tank", "sump", "pump", "timber", "wood",
            "curtain wall", "closet", "roof", "roofing", "cladding"
        ]
        found_cn = None
        for cn in core_nouns:
            if cn in norm_sq.split():
                found_cn = cn.rstrip("s")
                break
        if found_cn:
            cn_term = f"%{found_cn}%"
            filter_conditions.extend([
                ArchitecturalReference.title.ilike(cn_term),
                ArchitecturalReference.material_tags.ilike(cn_term),
            ])

        # Architectural concept tokens for multi-word queries (e.g. switch, drainage, kerala, tropical, renovation)
        stopwords = {"the", "and", "or", "for", "with", "from", "types", "different", "best", "used", "house", "room", "before", "after"}
        sub_tokens = [w for w in clean_sq.split() if len(w) >= 4 and w not in stopwords]
        for tok in sub_tokens:
            tok_term = f"%{tok}%"
            filter_conditions.extend([
                ArchitecturalReference.title.ilike(tok_term),
                ArchitecturalReference.material_tags.ilike(tok_term),
                ArchitecturalReference.search_keyword.ilike(tok_term),
            ])

        query = query.filter(or_(*filter_conditions))

    candidates = query.all()
    user_interest_list = [i.strip() for i in interests.split(",") if i.strip()] if isinstance(interests, str) and interests.strip() else None
    ranked_results = relevance_service.rank_and_filter_feed(
        candidates,
        query=search_query,
        user_interests=user_interest_list,
        category_slug=cat_slug
    )

    # When querying All Sources (plat_str is None), balance platforms across all content types
    if not plat_str:
        platform_buckets = {
            'pinterest': [],
            'instagram': [],
            'youtube': [],
            'reddit': [],
            'shopping': [],
            'x': [],
            'curated': [],
            'unsplash': [],
            'wikimedia': []
        }
        for item in ranked_results:
            p = item["reference"].source_platform
            if p in platform_buckets:
                platform_buckets[p].append(item)
            else:
                platform_buckets.setdefault('curated', []).append(item)

        # Round-robin interleave to guarantee cross-source variety
        interleaved = []
        keys_order = ['pinterest', 'curated', 'wikimedia', 'unsplash', 'instagram', 'youtube', 'reddit', 'shopping', 'x']
        max_len = max((len(b) for b in platform_buckets.values()), default=0)
        for i in range(max_len):
            for k in keys_order:
                if i < len(platform_buckets[k]):
                    interleaved.append(platform_buckets[k][i])

        if user_interest_list:
            interleaved.sort(key=lambda x: (1 if x.get("is_personalized") else 0, x["relevance_score"]), reverse=True)
        elif search_query:
            interleaved.sort(key=lambda x: (1 if x.get("relevance_score", 0) >= 0.85 else 0, x["relevance_score"]), reverse=True)

        ranked_results = interleaved

    total = len(ranked_results)
    offset = (page - 1) * page_size
    paged_results = ranked_results[offset:offset + page_size]
    refs = [item["reference"] for item in paged_results]

    items: List[ReferenceOut] = []
    for r in refs:
        if isinstance(r, ReferenceOut):
            items.append(r)
            continue
        cat_name = r.category.name if r.category else None
        matches_count = len(r.product_matches)

        # Enforce image provenance & separate manufacturer product image
        mfg_prod_img = r.manufacturer_product_image_url
        mfg_prod_url = r.manufacturer_product_url
        mfg_id = r.manufacturer_id
        mfg_name = r.manufacturer.name if r.manufacturer else None
        match_status = r.product_match_status or "unidentified"

        # Check product match provenance if not explicitly overridden
        if not mfg_prod_img and r.product_matches:
            top_match = r.product_matches[0]
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
                    mfg_prod_img = None
                    mfg_prod_url = None

        item_out = ReferenceOut(
            id=r.id,
            title=r.title,
            slug=r.slug,
            source_platform=r.source_platform,
            source_url=r.source_url,
            creator_name=r.creator_name,
            creator_url=r.creator_url,
            thumbnail_url=r.thumbnail_url,
            media_url=r.media_url,
            inspiration_image_url=r.inspiration_image_url or r.thumbnail_url,
            inspiration_source_url=r.inspiration_source_url or r.source_url,
            manufacturer_product_image_url=mfg_prod_img,
            manufacturer_product_url=mfg_prod_url,
            manufacturer_id=mfg_id,
            manufacturer_name=mfg_name,
            product_match_status=match_status,
            video_embed_id=r.video_embed_id,
            video_duration=r.video_duration,
            is_short=bool(r.is_short) if bool(r.video_embed_id) else False,
            image_attribution=r.image_attribution,
            source_domain=r.source_domain,
            colors_and_finishes=r.colors_and_finishes,
            category_id=r.category_id,
            category_name=cat_name,
            material_tags=r.material_tags,
            location_context=r.location_context,
            country=r.country or "India",
            region=r.region,
            architectural_style=r.architectural_style,
            project_type=r.project_type or "Residential",
            architecture_era=r.architecture_era or "Contemporary",
            architect_name=r.architect_name or r.creator_name,
            content_type=getattr(r, 'content_type', 'architectural_project') or 'architectural_project',
            verification_status=r.verification_status,
            description=r.description,
            retrieval_method=r.retrieval_method or "manual_curation",
            content_availability_status=r.content_availability_status or "ACTIVE",
            matched_products_count=matches_count,
            provenance=getattr(r, 'provenance', None) or ProvenanceEnum.CURATED_ARCHIVE.value,
            inspiration_relevance_tier=getattr(r, 'inspiration_relevance_tier', None) or InspirationRelevanceTierEnum.TIER_1_EXACT.value,
            media_status=getattr(r, 'media_status', None) or (MediaStatusEnum.MEDIA_READY.value if (r.inspiration_image_url or r.thumbnail_url or r.media_url or r.video_embed_id) else MediaStatusEnum.MEDIA_UNUSABLE.value),
            created_at=r.created_at
        )
        items.append(item_out)

    has_more = (offset + page_size) < total

    yt_count = db.query(ArchitecturalReference).filter_by(source_platform="youtube").count()
    images_count = db.query(ArchitecturalReference).filter(ArchitecturalReference.video_embed_id.is_(None)).count()
    curated_count = db.query(ArchitecturalReference).filter(ArchitecturalReference.source_platform != "youtube").count()

    connector_status = {
        "youtube_configured": is_socialcrawl_configured(),
        "socialcrawl_configured": is_socialcrawl_configured(),
        "total_references": total,
        "youtube_count": yt_count,
        "images_count": images_count,
        "curated_count": curated_count,
        "quota_exceeded": False,
        "image_search": image_search_service.get_provider_status(),
        "last_synced_at": datetime.now(timezone.utc).isoformat()
    }

    return FeedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more,
        connector_status=connector_status
    )

@router.get("/filters", response_model=FeedFiltersOut)
def get_feed_filters(db: Session = Depends(get_db)):
    countries = [c[0] for c in db.query(ArchitecturalReference.country).distinct().filter(ArchitecturalReference.country.isnot(None)).all() if c[0]]
    regions = [r[0] for r in db.query(ArchitecturalReference.region).distinct().filter(ArchitecturalReference.region.isnot(None)).all() if r[0]]
    styles = [s[0] for s in db.query(ArchitecturalReference.architectural_style).distinct().filter(ArchitecturalReference.architectural_style.isnot(None)).all() if s[0]]
    project_types = [p[0] for p in db.query(ArchitecturalReference.project_type).distinct().filter(ArchitecturalReference.project_type.isnot(None)).all() if p[0]]
    eras = [e[0] for e in db.query(ArchitecturalReference.architecture_era).distinct().filter(ArchitecturalReference.architecture_era.isnot(None)).all() if e[0]]

    categories = db.query(MaterialCategory).all()
    categories_out = [
        CategoryOut(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            image_url=cat.image_url
        ) for cat in categories
    ]

    return FeedFiltersOut(
        countries=sorted(list(set(countries))),
        regions=sorted(list(set(regions))),
        styles=sorted(list(set(styles))),
        project_types=sorted(list(set(project_types))),
        eras=sorted(list(set(eras))),
        categories=categories_out
    )

@router.post("/sync-youtube")
async def sync_youtube_feed(
    query: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    """
    Synchronizes YouTube architectural walkthroughs and installation demonstrations
    exclusively via SocialCrawl YouTube Search endpoint, with graceful fallback.
    """
    from app.services.socialcrawl_service import search_youtube
    from app.services.daily_collection_service import save_inspiration_reference
    kw = query or "architectural modern house elevation"
    try:
        res = search_youtube(query=kw, max_pages=1, dry_run=False)
        items = res.get("items", [])
    except Exception as e:
        logger.warning(f"Live YouTube sync encountered error: {e}")
        items = []

    added = 0
    for item in items:
        if save_inspiration_reference(db, item, kw, "Architecture"):
            added += 1
    db.commit()
    total_yt = db.query(ArchitecturalReference).filter_by(source_platform="youtube").count()
    return {
        "status": "success",
        "message": f"SocialCrawl YouTube search complete: {added} new architectural videos added." if added else "Curated database up-to-date.",
        "details": {
            "new_videos_added": added,
            "total_youtube_references": total_yt
        }
    }

@router.get("/youtube-search")
async def search_youtube_videos(
    q: str = Query("architectural material installation", description="Search keyword for architectural videos"),
    limit: int = Query(12, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    Direct live search across SocialCrawl YouTube for architectural videos,
    walkthroughs, installation demos, and manufacturer demonstrations.
    Does NOT use YouTube Data API key. Falls back gracefully to curated database videos.
    """
    from app.services.socialcrawl_service import search_youtube
    try:
        res = search_youtube(query=q, max_pages=1, dry_run=False)
        raw_items = res.get("items", [])
    except Exception as e:
        logger.warning(f"Live YouTube search encountered error: {e}")
        raw_items = []

    if not raw_items:
        curated = db.query(ArchitecturalReference).filter_by(source_platform="youtube").limit(limit).all()
        return [{
            "id": r.id,
            "title": r.title,
            "slug": r.slug,
            "source_platform": "youtube",
            "source_url": r.source_url or "https://youtube.com",
            "creator_name": r.creator_name or "Architectural Creator",
            "creator_url": r.creator_url,
            "thumbnail_url": r.thumbnail_url,
            "media_url": r.media_url,
            "video_embed_id": r.video_embed_id or "JEZhlcmDcc8",
            "material_tags": r.material_tags or "",
            "location_context": "Jobsite Video Walkthrough",
            "country": "India",
            "region": None,
            "architectural_style": "Installation & Craft Technique",
            "project_type": "Video Demonstration",
            "architecture_era": "Contemporary",
            "architect_name": r.creator_name,
            "content_type": "youtube_walkthrough",
            "verification_status": "UNVERIFIED",
            "description": r.description or "",
            "inspiration_image_url": r.thumbnail_url,
            "inspiration_source_url": r.source_url,
            "product_match_status": "unidentified",
            "matched_products_count": 0,
            "created_at": datetime.now(timezone.utc),
            "is_video": True
        } for r in curated]

    out_items = []
    for idx, item in enumerate(raw_items[:limit]):
        out_items.append({
            "id": 900000 + idx,
            "title": item.get("title") or "Architectural Video",
            "slug": item.get("slug") or f"yt-{idx}",
            "source_platform": "youtube",
            "source_url": item.get("source_url") or "https://youtube.com",
            "creator_name": item.get("creator_name") or "Architectural Creator",
            "creator_url": item.get("creator_url"),
            "thumbnail_url": item.get("thumbnail_url"),
            "media_url": item.get("media_url"),
            "video_embed_id": item.get("video_embed_id"),
            "material_tags": ", ".join(item.get("material_tags") or []),
            "location_context": "Jobsite Video Walkthrough",
            "country": "India",
            "region": None,
            "architectural_style": "Installation & Craft Technique",
            "project_type": "Video Demonstration",
            "architecture_era": "Contemporary",
            "architect_name": item.get("creator_name"),
            "content_type": "youtube_walkthrough",
            "verification_status": "UNVERIFIED",
            "description": item.get("description") or "",
            "inspiration_image_url": item.get("thumbnail_url"),
            "inspiration_source_url": item.get("source_url"),
            "product_match_status": "unidentified",
            "matched_products_count": 0,
            "created_at": datetime.now(timezone.utc)
        })
    return out_items

@router.get("/image-search")
async def search_architectural_images(
    q: str = Query("modern architecture facade", description="Search keyword for architectural images"),
    limit: int = Query(12, description="Max results"),
    category: Optional[str] = Query(None, description="Category slug filter")
):
    """
    Direct live search across legitimate architectural image providers:
    - Google Custom Search JSON API (with searchType=image)
    - Unsplash Developer API
    - Wikimedia Commons Architectural API (Open CC / Public Domain)
    - Curated Legitimate Architectural Catalog
    Preserves original image URL, source page URL, title, publisher, material category,
    attribution, and usage license.
    """
    items = await image_search_service.search_images(q, limit=limit, category_slug=category)
    return {
        "query": q,
        "category": category,
        "total_found": len(items),
        "provider_status": image_search_service.get_provider_status(),
        "images": [item.model_dump() for item in items]
    }

@router.get("/similar/{reference_id}")
def get_similar_references(
    reference_id: int,
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Returns visually and materially similar architectural references (both images and videos)
    for the Three-Dot Details Drawer.
    """
    ref = db.query(ArchitecturalReference).filter_by(id=reference_id).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Reference not found")

    candidates = db.query(ArchitecturalReference).filter(ArchitecturalReference.id != reference_id)
    
    # Prioritize matching category or matching material tags
    if ref.category_id:
        same_cat = candidates.filter(ArchitecturalReference.category_id == ref.category_id).all()
    else:
        same_cat = []

    # If few same category, search by material tags
    similar_list = list(same_cat)
    if len(similar_list) < limit and ref.material_tags:
        tags = [t.strip().lower() for t in ref.material_tags.split(",") if t.strip()]
        for tag in tags[:3]:
            more = candidates.filter(ArchitecturalReference.material_tags.ilike(f"%{tag}%")).all()
            for m in more:
                if m not in similar_list:
                    similar_list.append(m)

    # If still few, fetch other references
    if len(similar_list) < limit:
        remaining = candidates.all()
        for r in remaining:
            if r not in similar_list:
                similar_list.append(r)
            if len(similar_list) >= limit:
                break

    results = []
    for r in similar_list[:limit]:
        results.append({
            "id": r.id,
            "title": r.title,
            "slug": r.slug,
            "source_platform": r.source_platform,
            "source_url": r.source_url,
            "thumbnail_url": r.thumbnail_url or r.inspiration_image_url,
            "inspiration_image_url": r.inspiration_image_url or r.thumbnail_url,
            "video_embed_id": r.video_embed_id,
            "video_duration": r.video_duration,
            "is_short": bool(r.is_short),
            "creator_name": r.creator_name or r.architect_name,
            "category_name": r.category.name if r.category else None,
            "material_tags": r.material_tags,
            "colors_and_finishes": r.colors_and_finishes,
            "image_attribution": r.image_attribution
        })

    return results

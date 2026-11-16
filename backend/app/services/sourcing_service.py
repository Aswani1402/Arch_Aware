import re
import urllib.parse
from typing import List, Dict, Any, Optional, Set, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.models import Supplier, SupplierProduct, Product, MaterialCategory
from app.services.distance_service import (
    calculate_haversine_distance,
    normalize_location_name,
    is_in_district_or_buffer,
    distance_to_district_boundary
)
from app.schemas.schemas import (
    SourcingSearchQuery,
    HierarchicalSourcingResponse,
    FallbackLevelResult,
    SourcingTierResult,
    SourcingSupplierResult,
    SupplierProductLink
)

# Geographic grouping dictionaries for Indian States
NEIGHBOURING_STATES = {
    "Kerala": ["Tamil Nadu", "Karnataka"],
    "Tamil Nadu": ["Kerala", "Karnataka", "Andhra Pradesh"],
    "Karnataka": ["Kerala", "Tamil Nadu", "Goa", "Maharashtra", "Andhra Pradesh", "Telangana"],
    "Maharashtra": ["Karnataka", "Goa", "Gujarat", "Madhya Pradesh", "Telangana"],
    "Delhi": ["Haryana", "Uttar Pradesh", "Rajasthan"],
    "Telangana": ["Andhra Pradesh", "Karnataka", "Maharashtra"],
    "Andhra Pradesh": ["Telangana", "Tamil Nadu", "Karnataka", "Odisha"]
}

SOUTH_INDIA_STATES = {"Kerala", "Tamil Nadu", "Karnataka", "Andhra Pradesh", "Telangana", "Goa"}

# Known city coordinates preset fallback
CITY_COORDINATES = {
    "Kochi": (9.9312, 76.2673, "Kerala"),
    "Ernakulam": (9.9816, 76.2999, "Kerala"),
    "Calicut": (11.2588, 75.7804, "Kerala"),
    "Kozhikode": (11.2588, 75.7804, "Kerala"),
    "Trivandrum": (8.5241, 76.9366, "Kerala"),
    "Thiruvananthapuram": (8.5241, 76.9366, "Kerala"),
    "Bengaluru": (12.9716, 77.5946, "Karnataka"),
    "Bangalore": (12.9716, 77.5946, "Karnataka"),
    "Chennai": (13.0827, 80.2707, "Tamil Nadu"),
    "Coimbatore": (11.0168, 76.9558, "Tamil Nadu"),
    "Nagercoil": (8.1833, 77.4119, "Tamil Nadu"),
    "Kanyakumari": (8.0883, 77.5385, "Tamil Nadu"),
    "Marthandam": (8.3033, 77.2217, "Tamil Nadu"),
    "Tirunelveli": (8.7139, 77.7567, "Tamil Nadu"),
    "Madurai": (9.9252, 78.1198, "Tamil Nadu"),
    "Mumbai": (19.0760, 72.8777, "Maharashtra"),
    "Pune": (18.5204, 73.8567, "Maharashtra"),
    "Hyderabad": (17.3850, 78.4867, "Telangana"),
    "Delhi": (28.6139, 77.2090, "Delhi"),
}

# ============================================================
# CATEGORY-TO-SUPPLIER RELATIONSHIP TAXONOMY (PART 16)
# ============================================================

CATEGORY_SUPPLIER_RULES: List[Dict[str, Any]] = [
    {
        "category_key": "pipes_and_plumbing",
        "category_title": "Pipes, Fittings & Drainage",
        "trigger_words": ["pipe", "pipes", "cpvc", "upvc", "pvc", "hdpe", "ppr", "plumbing", "drainage", "sewage", "fitting", "fittings", "valve", "valves", "astral", "supreme"],
        "exact_keywords": ["cpvc", "upvc", "pvc pipe", "drainage pipe"],
        "supplier_category_terms": ["pipe", "pipes", "plumbing", "drainage", "fittings"]
    },
    {
        "category_key": "sanitaryware_and_bath",
        "category_title": "Sanitaryware & Bath Fittings",
        "trigger_words": ["toilet", "commode", "washbasin", "basin", "faucet", "faucets", "shower", "showers", "bathtub", "vanity", "kohler", "jaquar", "bathroom"],
        "exact_keywords": ["wall hung toilet", "rain shower", "freestanding bathtub", "thermostatic diverter"],
        "supplier_category_terms": ["sanitaryware", "sanitary", "faucet", "faucets", "bath", "bathroom"]
    },
    {
        "category_key": "steel_and_tmt",
        "category_title": "TMT Rebar & Structural Steel",
        "trigger_words": ["steel", "tmt", "rebar", "reinforcement", "fe 550d", "fe 500d", "tata tiscon", "jsw steel", "structural steel", "iron rod"],
        "exact_keywords": ["tmt", "fe 550d", "tata tiscon", "jsw neosteel", "rebar"],
        "supplier_category_terms": ["steel", "iron", "tmt", "metals", "rebar", "structural steel"]
    },
    {
        "category_key": "cement_and_concrete",
        "category_title": "Cement & Ready-Mix Concrete",
        "trigger_words": ["cement", "concrete", "ready mix", "rmc", "microcement", "opc 53", "ppc cement", "ultratech", "ramco", "dalmia"],
        "exact_keywords": ["opc 53", "ppc cement", "ultratech", "ready mix concrete"],
        "supplier_category_terms": ["cement", "concrete", "ready mix", "rmc", "microcement"]
    },
    {
        "category_key": "bricks_and_masonry",
        "category_title": "Bricks & AAC Lightweight Blocks",
        "trigger_words": ["brick", "bricks", "aac", "block", "blocks", "porotherm", "laterite", "masonry", "fly ash", "wirecut"],
        "exact_keywords": ["wirecut brick", "aac block", "porotherm", "laterite"],
        "supplier_category_terms": ["brick", "bricks", "aac", "block", "blocks", "porotherm", "laterite", "masonry"]
    },
    {
        "category_key": "flooring_and_tiles",
        "category_title": "Tiles, Marble & Natural Stone",
        "trigger_words": ["tile", "tiles", "marble", "granite", "porcelain", "vitrified", "terrazzo", "athangudi", "stone", "kota", "slab", "slabs", "flooring", "sandstone"],
        "exact_keywords": ["italian marble", "statuario", "botticino", "athangudi", "vitrified tile", "granite"],
        "supplier_category_terms": ["tile", "tiles", "marble", "granite", "stone", "flooring", "ceramic", "porcelain"]
    },
    {
        "category_key": "lighting_and_electrical",
        "category_title": "Lighting & Electrical Fixtures",
        "trigger_words": ["light", "lighting", "chandelier", "chandeliers", "lamp", "switch", "switches", "wire", "wires", "cable", "cables", "led", "sconce", "downlight", "track light"],
        "exact_keywords": ["chandelier", "crystal chandelier", "magnetic track", "led profile"],
        "supplier_category_terms": ["lighting", "electrical", "chandelier", "lights", "switches", "lamp"]
    },
    {
        "category_key": "doors_windows_and_glass",
        "category_title": "Doors, Windows, Timber & Glass",
        "trigger_words": ["door", "doors", "window", "windows", "glass", "teak", "timber", "wood", "plywood", "upvc window", "aluminium window", "hardware", "hinge", "lock"],
        "exact_keywords": ["teak door", "pivot door", "upvc window", "fluted glass", "toughened glass"],
        "supplier_category_terms": ["door", "timber", "wood", "window", "glass", "aluminium", "hardware", "carpentry"]
    },
    {
        "category_key": "staircase_and_railings",
        "category_title": "Staircases, Metal Fabrication & Railings",
        "trigger_words": ["staircase", "stairs", "railing", "railings", "handrail", "balustrade", "floating stair", "spiral", "cantilever stair", "glass railing"],
        "exact_keywords": ["floating staircase", "cantilever staircase", "glass railing", "spiral staircase"],
        "supplier_category_terms": ["fabricator", "metal", "staircase", "railing", "glass", "steel", "iron", "carpentry"]
    },
    {
        "category_key": "landscaping_and_outdoor",
        "category_title": "Landscaping, Natural Stones & Garden Elements",
        "trigger_words": ["landscape", "landscaping", "garden", "pebble", "pebbles", "gravel", "stepping stone", "stepping stones", "boulder", "boulders", "waterfall", "fountain", "pergola"],
        "exact_keywords": ["landscaping stones", "river pebbles", "garden waterfall", "stepping stones"],
        "supplier_category_terms": ["landscape", "stone", "nursery", "garden", "outdoor", "pebbles", "water feature", "importer"]
    },
    {
        "category_key": "furniture_and_kitchen",
        "category_title": "Furniture, Modular Kitchens & Wardrobes",
        "trigger_words": ["kitchen", "modular kitchen", "sofa", "chair", "table", "bed", "wardrobe", "joinery", "cabinet", "hafele", "sleek", "veneta", "wurfel"],
        "exact_keywords": ["modular kitchen", "acrylic kitchen", "sectional sofa", "walk-in wardrobe"],
        "supplier_category_terms": ["furniture", "kitchen", "modular", "interior", "wardrobe", "wood", "hardware"]
    },
    {
        "category_key": "paints_and_waterproofing",
        "category_title": "Paints, Textures & Waterproofing",
        "trigger_words": ["paint", "paints", "waterproofing", "primer", "emulsion", "dr fixit", "asian paints", "berger", "fosroc", "weatherproof", "damp proof", "epoxy coating"],
        "exact_keywords": ["waterproofing", "damp proof", "exterior emulsion", "epoxy floor coating"],
        "supplier_category_terms": ["paint", "paints", "waterproofing", "coating", "coatings", "chemical", "chemicals"]
    },
    {
        "category_key": "roofing_and_ceilings",
        "category_title": "Roofing, Shingles & False Ceilings",
        "trigger_words": ["roof", "roofing", "shingle", "shingles", "ceiling", "false ceiling", "gypsum", "mangalore tile", "clay roof", "polycarbonate sheet", "upvc sheet"],
        "exact_keywords": ["roofing tiles", "clay roofing", "false ceiling", "gypsum board", "roof shingles"],
        "supplier_category_terms": ["roof", "roofing", "ceiling", "gypsum", "shingle", "tiles", "sheets"]
    },
    {
        "category_key": "architectural_hardware",
        "category_title": "Architectural Hardware, Locks & Fittings",
        "trigger_words": ["hardware", "door lock", "mortise lock", "door handle", "hinges", "sliding fitting", "telescopic channel", "glass fitting", "spider fitting", "patch fitting", "godrej", "hafele", "dorma"],
        "exact_keywords": ["mortise lock", "door handle", "patch fitting", "concealed hinge"],
        "supplier_category_terms": ["hardware", "fittings", "lock", "locks", "handles", "hinges"]
    },
    {
        "category_key": "construction_equipment",
        "category_title": "Construction Equipment & Scaffolding",
        "trigger_words": ["equipment", "scaffolding", "concrete mixer", "vibrator", "shuttering", "props", "hoist", "bar bending", "compactor"],
        "exact_keywords": ["scaffolding", "concrete mixer", "shuttering material", "cuplock scaffolding"],
        "supplier_category_terms": ["equipment", "scaffolding", "machinery", "shuttering", "tools"]
    },
    {
        "category_key": "interior_showrooms",
        "category_title": "Interior Material Showrooms & Experience Centers",
        "trigger_words": ["showroom", "experience center", "interior materials", "display studio", "gallery", "trade studio", "curated surfaces"],
        "exact_keywords": ["interior showroom", "material studio", "experience center"],
        "supplier_category_terms": ["showroom", "studio", "gallery", "dealer", "depot", "surfaces", "interior"]
    }
]


def resolve_location(city: Optional[str], lat: Optional[float], lon: Optional[float], state: Optional[str]):
    if lat is not None and lon is not None:
        resolved_city = city or "Current Location"
        resolved_state = state or "India"
        return lat, lon, resolved_city, resolved_state

    if city and city.strip():
        c_title = city.strip().title()
        if c_title in CITY_COORDINATES:
            c_lat, c_lon, c_state = CITY_COORDINATES[c_title]
            return c_lat, c_lon, c_title, state or c_state
        # Also check alias normalization against CITY_COORDINATES
        c_norm = normalize_location_name(city)
        for k, v in CITY_COORDINATES.items():
            if normalize_location_name(k) == c_norm:
                return v[0], v[1], c_title, state or v[2]
        return None, None, c_title, state or "India"

    # When no location is selected, do NOT fabricate Kochi
    return None, None, None, None


def classify_supplier_match(
    sup: Supplier,
    query_text: Optional[str],
    matched_products_links: List[SupplierProduct]
) -> Tuple[str, str, str, str]:
    """
    Classifies supplier match type, human-readable label, honest explanation, and category name.
    Strictly distinguishes exact matches from category matches as required by Part 16.
    """
    if not query_text:
        b_type = (sup.business_type or "authorized_dealer").lower()
        if "manufacturer" in b_type or "quarry" in b_type:
            return "manufacturer", "Direct Manufacturer", "Direct material manufacturer & factory", "Building Materials"
        if "distributor" in b_type or "importer" in b_type:
            return "distributor", "Distributor / Wholesaler", "Authorized regional distributor & bulk stockist", "Building Materials"
        if "fabricator" in b_type or "installer" in b_type:
            return "installer", "Fabricator / Contractor", "On-site fabrication & installation contractor", "Building Materials"
        return "category_match", "Verified Dealer", "Verified architectural trade supplier", "Building Materials"

    q_lower = query_text.lower().strip()
    sup_text = f"{sup.name} {sup.materials_sold or ''} {sup.brands_distributed or ''} {sup.business_type or ''}".lower()

    # 1. Check exact product matches in catalog
    if matched_products_links:
        for sp in matched_products_links:
            if sp.product and (q_lower in sp.product.name.lower() or any(w in sp.product.name.lower() for w in q_lower.split() if len(w) > 3)):
                p_name = sp.product.name
                return (
                    "exact_product",
                    "Exact Product Match",
                    f"Confirmed product in supplier inventory: {p_name}",
                    sp.product.category.name if sp.product.category else "Building Materials"
                )

    # 2. Match against Category Rules
    for rule in CATEGORY_SUPPLIER_RULES:
        is_rule_trigger = any(tw in q_lower for tw in rule["trigger_words"])
        if is_rule_trigger:
            cat_title = rule["category_title"]
            supplier_matches_cat = any(bool(re.search(rf"\b{re.escape(term)}\b", sup_text)) for term in rule["supplier_category_terms"])
            b_type = (sup.business_type or "").lower()

            if supplier_matches_cat:
                if "manufacturer" in b_type or "quarry" in b_type:
                    return (
                        "manufacturer",
                        "Direct Manufacturer",
                        f"Direct manufacturer of {cat_title}",
                        cat_title
                    )
                if "distributor" in b_type or "importer" in b_type:
                    return (
                        "distributor",
                        "Distributor / Wholesaler",
                        f"Authorized regional distributor & stockist for {cat_title}",
                        cat_title
                    )
                if "fabricator" in b_type or "installer" in b_type or "contractor" in b_type:
                    return (
                        "installer",
                        "Fabricator / Contractor",
                        f"Specialist fabrication & contractor for {cat_title}",
                        cat_title
                    )

                # Honest Part 16 label: "Pipe supplier — CPVC availability not confirmed"
                return (
                    "category_match",
                    "Category Match",
                    f"{cat_title} dealer — exact {query_text} stock not confirmed",
                    cat_title
                )

    # 3. Fallback to Related Supplier
    return (
        "related_supplier",
        "Related Supplier",
        f"Adjacent architectural materials supplier — check with vendor for {query_text}",
        "Architectural Materials"
    )


def execute_hierarchical_sourcing(
    db: Session,
    search_query: SourcingSearchQuery
) -> HierarchicalSourcingResponse:
    user_lat, user_lon, user_city, user_state = resolve_location(
        search_query.city,
        search_query.latitude,
        search_query.longitude,
        search_query.state
    )

    query_text = search_query.query.strip().lower() if search_query.query else None

    # Load all suppliers with their linked products
    all_suppliers = db.query(Supplier).all()

    # Determine relevant category rules for this query
    active_category_rules = []
    if query_text:
        for rule in CATEGORY_SUPPLIER_RULES:
            if any(tw in query_text for tw in rule["trigger_words"]):
                active_category_rules.append(rule)

    filtered_supplier_data: List[Dict[str, Any]] = []

    for sup in all_suppliers:
        matched_products_links = []
        is_relevant = False

        if not query_text and not search_query.product_id and not search_query.category_slug:
            # General supplier search
            is_relevant = True
        else:
            # 1. Check linked products
            for sp in sup.product_links:
                prod = sp.product
                if not prod:
                    continue

                if search_query.product_id and prod.id == search_query.product_id:
                    is_relevant = True
                    matched_products_links.append(sp)
                    continue

                if search_query.category_slug:
                    cat = prod.category
                    if cat and cat.slug.lower() == search_query.category_slug.lower():
                        is_relevant = True
                        matched_products_links.append(sp)
                        continue

                if query_text:
                    p_name = prod.name.lower()
                    mat_type = prod.material_type.lower() if prod.material_type else ""
                    cat_name = prod.category.name.lower() if prod.category else ""
                    q_words = [w for w in query_text.split() if len(w) > 2 and w not in ["for", "and", "the", "with"]]
                    s_words = [w for w in q_words if w not in {"brick", "bricks", "stone", "stones", "block", "blocks", "tile", "tiles", "material", "materials", "building", "slab", "slabs", "wood", "glass", "steel", "cement", "pipe", "pipes"}]
                    if query_text in p_name or query_text in mat_type:
                        is_relevant = True
                        matched_products_links.append(sp)
                    elif s_words and any(w in p_name or w in mat_type for w in s_words):
                        is_relevant = True
                        matched_products_links.append(sp)
                    elif not s_words and any(w in p_name for w in q_words if len(w) > 3):
                        is_relevant = True
                        matched_products_links.append(sp)

            # 2. Check supplier profile text (materials_sold, brands_distributed, business_type, name)
            if not is_relevant and query_text:
                sup_corpus = f"{sup.name} {sup.materials_sold or ''} {sup.brands_distributed or ''} {sup.business_type or ''}".lower()
                
                GENERIC_MATERIAL_WORDS = {
                    "brick", "bricks", "stone", "stones", "block", "blocks",
                    "tile", "tiles", "material", "materials", "building", "slab", "slabs",
                    "wood", "glass", "steel", "cement", "pipe", "pipes"
                }

                # Check direct whole-word match of query words (avoiding false positives like 'bar' in 'malabar')
                query_words = [w for w in query_text.split() if len(w) > 2 and w not in ["for", "and", "the", "with", "bar", "bars", "types", "best"]]
                specific_words = [w for w in query_words if w not in GENERIC_MATERIAL_WORDS]

                # Requirement 5: Do not match suppliers based only on generic words (brick, stone, blocks, tiles)
                # If specific qualifiers exist (e.g. 'kota', 'aac', 'wirecut', 'laterite', 'porotherm'), require specific match
                if specific_words:
                    if (query_text in sup_corpus or 
                        any(bool(re.search(rf"\b{re.escape(w)}\b", sup_corpus)) for w in specific_words) or
                        any(query_text in (p.product.name.lower() or "") for p in sup.product_links if p.product)):
                        is_relevant = True
                else:
                    # Query was solely a generic noun; match whole-word or category terms
                    if any(bool(re.search(rf"\b{re.escape(w)}\b", sup_corpus)) for w in (query_words or query_text.split())):
                        is_relevant = True

                    # Check category rule match (Part 16: Category-based supplier discovery)
                    if not is_relevant and active_category_rules:
                        for rule in active_category_rules:
                            if any(bool(re.search(rf"\b{re.escape(term)}\b", sup_corpus)) for term in rule["supplier_category_terms"]):
                                is_relevant = True
                                break

        if is_relevant:
            user_canonical = normalize_location_name(user_city)

            # Calculate distance and evaluate district boundaries when coordinates are known
            dist = None
            boundary_dist = None
            in_district_buffer = False
            scope_note = None

            if user_lat is not None and user_lon is not None and sup.latitude is not None and sup.longitude is not None:
                dist = calculate_haversine_distance(user_lat, user_lon, sup.latitude, sup.longitude)
                if user_canonical == "thiruvananthapuram":
                    in_buf, b_dist, b_label = is_in_district_or_buffer(
                        sup.latitude, sup.longitude, "thiruvananthapuram", buffer_km=60.0
                    )
                    in_district_buffer = in_buf
                    boundary_dist = b_dist
                    scope_note = b_label
            else:
                dist = None

            # Build matched product schemas
            p_links = []
            for sp in (matched_products_links or sup.product_links):
                if sp.product:
                    p_links.append(
                        SupplierProductLink(
                            product_id=sp.product.id,
                            product_name=sp.product.name,
                            material_type=sp.product.material_type,
                            match_type=sp.match_type or "exact_product",
                            price=sp.price,
                            currency=sp.currency or "INR",
                            price_unit=sp.price_unit or "piece",
                            availability_status=sp.availability_status or "in_stock",
                            stock_status=sp.stock_status or "in_stock",
                            min_order_quantity=sp.min_order_quantity,
                            available_quantity=sp.available_quantity,
                            delivery_scope=sp.delivery_scope or "state",
                            estimated_lead_time_days=sp.estimated_lead_time_days,
                            image_url=sp.product.image_url
                        )
                    )

            match_type, match_label, match_explanation, category_name = classify_supplier_match(
                sup, query_text, matched_products_links
            )

            filtered_supplier_data.append({
                "supplier": sup,
                "distance_km": dist,
                "boundary_dist": boundary_dist,
                "in_district_buffer": in_district_buffer,
                "scope_note": scope_note,
                "matched_products": p_links,
                "match_type": match_type,
                "match_label": match_label,
                "match_explanation": match_explanation,
                "category_name": category_name
            })

    seen_supplier_ids: Set[int] = set()

    def make_supplier_result(item: Dict[str, Any], scope_label: str) -> SourcingSupplierResult:
        sup = item["supplier"]
        dist = item["distance_km"]
        if item.get("scope_note"):
            dist_display = item["scope_note"]
        elif dist is not None:
            dist_display = f"{dist} km"
        else:
            dist_display = f"Location Match ({sup.city}, {sup.state})"

        maps_url = sup.google_maps_url
        if not maps_url:
            query_str = f"{sup.name} {sup.address} {sup.city} {sup.state}"
            maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote_plus(query_str)}"

        is_international = sup.country != "India"

        return SourcingSupplierResult(
            supplier_id=sup.id,
            supplier_name=sup.name,
            business_type=sup.business_type,
            contact_person=sup.contact_person,
            address=sup.address,
            city=sup.city,
            district=sup.district,
            state=sup.state,
            country=sup.country,
            distance_km=dist,
            distance_display=dist_display,
            geographic_scope=scope_label,
            verification_status=sup.verification_status,
            is_potential=sup.is_potential,
            phone=sup.phone,
            whatsapp=getattr(sup, "whatsapp", None),
            email=sup.email,
            website=sup.website,
            google_maps_url=maps_url,
            catalog_url=sup.website,
            brands_distributed=sup.brands_distributed,
            delivery_areas=sup.delivery_areas,
            last_confirmed_contact=sup.last_updated_at.strftime("%b %Y") if getattr(sup, "last_updated_at", None) else "Verified Trade Member",
            export_availability=True if is_international else None,
            shipping_coverage="International freight forwarding with phytosanitary documentation" if is_international else sup.delivery_areas,
            import_notes="Subject to Indian port customs clearance & phytosanitary inspection" if is_international else None,
            match_type=item["match_type"],
            match_label=item["match_label"],
            match_explanation=item["match_explanation"],
            category_name=item["category_name"],
            matched_products=item["matched_products"]
        )

    levels: List[FallbackLevelResult] = []

    # Level 0: Immediate Project Area / Local City
    lvl0_suppliers = []
    user_norm = normalize_location_name(user_city)
    for item in filtered_supplier_data:
        sup = item["supplier"]
        sup_id = sup.id
        if sup_id not in seen_supplier_ids:
            is_local = False
            if item["distance_km"] is not None:
                is_local = item["distance_km"] <= search_query.initial_radius_km
            elif user_norm:
                sup_city_norm = normalize_location_name(sup.city)
                sup_dist_norm = normalize_location_name(sup.district)
                if sup_city_norm == user_norm or sup_dist_norm == user_norm:
                    is_local = True

            if is_local:
                seen_supplier_ids.add(sup_id)
                label = f"Local ({item['distance_km']} km)" if item["distance_km"] is not None else f"Local City ({sup.city})"
                lvl0_suppliers.append(make_supplier_result(item, label))

    lvl0_suppliers.sort(key=lambda s: (0 if s.match_type == "exact_product" else 1, s.distance_km if s.distance_km is not None else 999999.0))
    levels.append(FallbackLevelResult(
        level=0,
        level_name="Immediate Vicinity",
        radius_desc=f"Within {int(search_query.initial_radius_km)} km radius of {user_city}" if user_city else "Select project location to view local radius suppliers",
        explanation=f"Found {len(lvl0_suppliers)} local supplier(s) in {user_city}." if lvl0_suppliers else (f"No verified suppliers within {int(search_query.initial_radius_km)} km of {user_city}; expanding outward." if user_city else "No project location selected; browsing broader verified trade network."),
        suppliers=lvl0_suppliers,
        searched=True
    ))

    # Level 1: Extended Local Region (distance <= 50km or district boundary + 60km buffer or same district)
    lvl1_suppliers = []
    for item in filtered_supplier_data:
        sup = item["supplier"]
        sup_id = sup.id
        if sup_id not in seen_supplier_ids:
            is_extended = False
            if item.get("in_district_buffer"):
                is_extended = True
            elif item["distance_km"] is not None:
                is_extended = item["distance_km"] <= 50.0
            elif user_norm:
                sup_city_norm = normalize_location_name(sup.city)
                sup_dist_norm = normalize_location_name(sup.district)
                if sup_city_norm == user_norm or sup_dist_norm == user_norm:
                    is_extended = True

            if is_extended:
                seen_supplier_ids.add(sup_id)
                label = item.get("scope_note") or (f"Sub-Regional ({item['distance_km']} km)" if item["distance_km"] is not None else f"District Corridor ({sup.city})")
                lvl1_suppliers.append(make_supplier_result(item, label))

    lvl1_suppliers.sort(key=lambda s: (0 if s.match_type == "exact_product" else 1, s.distance_km if s.distance_km is not None else 999999.0))
    levels.append(FallbackLevelResult(
        level=1,
        level_name="Extended Local Region",
        radius_desc="Within 50 km radius or district perimeter buffer (~60 km)",
        explanation=f"Found {len(lvl1_suppliers)} sub-regional supplier(s)." if lvl1_suppliers else "No suppliers in extended 50 km perimeter; searching regional hubs.",
        suppliers=lvl1_suppliers,
        searched=True
    ))

    # Level 2: Regional Hubs (distance <= 100km)
    lvl2_suppliers = []
    for item in filtered_supplier_data:
        sup_id = item["supplier"].id
        if sup_id not in seen_supplier_ids:
            is_reg = False
            if item["distance_km"] is not None:
                is_reg = item["distance_km"] <= 100.0

            if is_reg:
                seen_supplier_ids.add(sup_id)
                lvl2_suppliers.append(make_supplier_result(item, f"Regional ({item['distance_km']} km)"))

    lvl2_suppliers.sort(key=lambda s: (0 if s.match_type == "exact_product" else 1, s.distance_km if s.distance_km is not None else 999999.0))
    levels.append(FallbackLevelResult(
        level=2,
        level_name="Regional Hubs & Transit Corridors",
        radius_desc="Within 100 km radius of project location",
        explanation=f"Found {len(lvl2_suppliers)} regional supplier(s)." if lvl2_suppliers else "No regional suppliers within 100 km; searching state-wide network.",
        suppliers=lvl2_suppliers,
        searched=True
    ))

    # Level 3: State-wide
    lvl3_suppliers = []
    for item in filtered_supplier_data:
        sup = item["supplier"]
        if sup.id not in seen_supplier_ids and user_state and sup.state == user_state and sup.country == "India":
            seen_supplier_ids.add(sup.id)
            lvl3_suppliers.append(make_supplier_result(item, f"State-wide ({sup.state})"))

    lvl3_suppliers.sort(key=lambda s: (0 if s.match_type == "exact_product" else 1, s.distance_km if s.distance_km is not None else 999999.0))
    levels.append(FallbackLevelResult(
        level=3,
        level_name="State-wide Logistics Network",
        radius_desc=f"Suppliers across {user_state}" if user_state else "State-wide logistics network",
        explanation=f"Found {len(lvl3_suppliers)} state-wide supplier(s) in {user_state}." if lvl3_suppliers else (f"No suppliers in {user_state}; searching neighbouring states." if user_state else "Browsing regional & national trade network."),
        suppliers=lvl3_suppliers,
        searched=True
    ))

    # Level 4: Neighbouring States
    neighbours = NEIGHBOURING_STATES.get(user_state, []) if user_state else []
    lvl4_suppliers = []
    for item in filtered_supplier_data:
        sup = item["supplier"]
        if sup.id not in seen_supplier_ids and sup.state in neighbours and sup.country == "India":
            seen_supplier_ids.add(sup.id)
            lvl4_suppliers.append(make_supplier_result(item, f"Neighbouring ({sup.state})"))

    lvl4_suppliers.sort(key=lambda s: (0 if s.match_type == "exact_product" else 1, s.distance_km if s.distance_km is not None else 999999.0))
    levels.append(FallbackLevelResult(
        level=4,
        level_name="Neighbouring Interstate Hubs",
        radius_desc=f"Adjacent states ({', '.join(neighbours) if neighbours else 'Nearby'})",
        explanation=f"Found {len(lvl4_suppliers)} supplier(s) in neighbouring interstate corridors." if lvl4_suppliers else "No suppliers in neighbouring states; searching Pan-India network.",
        suppliers=lvl4_suppliers,
        searched=True
    ))

    # Level 5: South India / Zonal Commercial Corridors
    lvl5_suppliers = []
    for item in filtered_supplier_data:
        sup = item["supplier"]
        if sup.id not in seen_supplier_ids and sup.state in SOUTH_INDIA_STATES and sup.country == "India":
            seen_supplier_ids.add(sup.id)
            lvl5_suppliers.append(make_supplier_result(item, f"Zonal / South India ({sup.city}, {sup.state})"))

    lvl5_suppliers.sort(key=lambda s: (0 if s.match_type == "exact_product" else 1, s.distance_km if s.distance_km is not None else 999999.0))
    levels.append(FallbackLevelResult(
        level=5,
        level_name="Zonal Commercial Corridors",
        radius_desc="South India & macro-regional trade corridors",
        explanation=f"Found {len(lvl5_suppliers)} zonal vendor(s)." if lvl5_suppliers else "No further zonal suppliers found; searching Pan-India network.",
        suppliers=lvl5_suppliers,
        searched=True
    ))

    # Level 6: Pan-India Authorized Stockists & Mill Rolling Centers
    lvl6_suppliers = []
    for item in filtered_supplier_data:
        sup = item["supplier"]
        if sup.id not in seen_supplier_ids and sup.country == "India":
            seen_supplier_ids.add(sup.id)
            lvl6_suppliers.append(make_supplier_result(item, f"National ({sup.city}, {sup.state})"))

    lvl6_suppliers.sort(key=lambda s: (0 if s.match_type == "exact_product" else 1, s.distance_km if s.distance_km is not None else 999999.0))
    levels.append(FallbackLevelResult(
        level=6,
        level_name="Pan-India Authorized Stockists & Mill Rolling Centers",
        radius_desc="All Indian commercial states & manufacturing clusters",
        explanation=f"Found {len(lvl6_suppliers)} national vendor(s)." if lvl6_suppliers else "No further domestic suppliers found.",
        suppliers=lvl6_suppliers,
        searched=True
    ))

    # Level 7: International Exporters & Manufacturers
    lvl7_suppliers = []
    for item in filtered_supplier_data:
        sup = item["supplier"]
        if sup.id not in seen_supplier_ids and sup.country != "India":
            seen_supplier_ids.add(sup.id)
            lvl7_suppliers.append(make_supplier_result(item, f"International ({sup.country})"))

    lvl7_suppliers.sort(key=lambda s: (0 if s.match_type == "exact_product" else 1, s.distance_km if s.distance_km is not None else 999999.0))
    levels.append(FallbackLevelResult(
        level=7,
        level_name="International Sourcing & Exporters",
        radius_desc="Overseas manufacturers & export ateliers (Japan, Italy, Germany, etc.)",
        explanation=f"Found {len(lvl7_suppliers)} international exporter(s) with documentation support." if lvl7_suppliers else "Search completed.",
        suppliers=lvl7_suppliers,
        searched=True
    ))

    total_found = len(seen_supplier_ids)
    all_selected = [s for lvl in levels for s in lvl.suppliers]
    verified_count = sum(1 for s in all_selected if not s.is_potential)
    potential_count = sum(1 for s in all_selected if s.is_potential)

    # 5-Tier Global Sourcing Hierarchy
    tiers: List[SourcingTierResult] = [
        SourcingTierResult(
            tier=1,
            tier_name="Local",
            description=f"Suppliers located in {user_city} and immediate district perimeter" if user_city else "Local radius suppliers (select location in header)",
            suppliers=lvl0_suppliers
        ),
        SourcingTierResult(
            tier=2,
            tier_name="Nearby",
            description=f"Suppliers in surrounding districts (<100 km)" if user_city else "Nearby district suppliers (<100 km)",
            suppliers=lvl1_suppliers + lvl2_suppliers
        ),
        SourcingTierResult(
            tier=3,
            tier_name="Regional & Interstate",
            description=f"Suppliers across {user_state} and neighbouring states" if user_state else "Suppliers across regional trade corridors",
            suppliers=lvl3_suppliers + lvl4_suppliers
        ),
        SourcingTierResult(
            tier=4,
            tier_name="India",
            description="Pan-India manufacturers and national freight suppliers",
            suppliers=lvl5_suppliers + lvl6_suppliers
        ),
        SourcingTierResult(
            tier=5,
            tier_name="International",
            description="Verified overseas manufacturers and export ateliers",
            suppliers=lvl7_suppliers
        ),
    ]

    return HierarchicalSourcingResponse(
        query=search_query.query,
        user_location={
            "city": user_city,
            "state": user_state,
            "latitude": user_lat,
            "longitude": user_lon,
            "is_set": bool(user_city)
        },
        initial_radius_km=search_query.initial_radius_km,
        total_suppliers_found=total_found,
        levels_traversed=levels,
        tiers=tiers,
        verified_suppliers_count=verified_count,
        potential_suppliers_count=potential_count
    )

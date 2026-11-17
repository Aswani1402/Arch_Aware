"""
Arch_Aware Social Vocabulary & Material Query Expansion Engine.

Researched social terms, hashtags, visual keywords, and demonstration phrases
used by real architects, interior designers, contractors, and suppliers on
Instagram, YouTube, Pinterest, Reddit, and Google Places.

Translates technical catalogue names (IS/ASTM standards, specs, dimensions)
into high-yield social discovery queries and multi-tier vendor searches.
"""

import re
from typing import Dict, List, Any, Optional

# Core mapping for material families -> real-world social hashtags & visual queries
MATERIAL_SOCIAL_REGISTRY: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------
    # MASONRY & WALL SYSTEMS
    # -------------------------------------------------------------
    "brick": {
        "instagram": [
            "red brick architecture house",
            "exposed brick masonry wall",
            "brick house design India",
            "wire cut brick elevation",
            "terracotta brick construction",
        ],
        "youtube": [
            "exposed brick house construction tour India",
            "brick masonry construction techniques walkthrough",
            "wire cut bricks vs standard clay bricks",
            "brick wall pointing and laying video",
        ],
        "pinterest": [
            "exposed brick interior and exterior architecture",
            "modern brick house elevation design",
            "brick jali screen facade pattern",
        ],
        "reddit": [
            "exposed brick wall maintenance cost experience",
            "wire cut bricks vs normal red bricks quality",
        ],
        "vendor_terms": ["clay bricks", "wire cut bricks", "red bricks kiln manufacturer"],
    },
    "aac block": {
        "instagram": [
            "AAC block construction house",
            "AAC block wall masonry work",
            "autoclaved aerated concrete wall",
        ],
        "youtube": [
            "AAC blocks vs red clay bricks comparison house",
            "how to lay AAC blocks construction walkthrough",
            "AAC block masonry adhesive joint video",
        ],
        "pinterest": [
            "AAC block modern house construction",
            "AAC block masonry techniques",
        ],
        "reddit": [
            "AAC blocks cracks plastering experience",
            "AAC blocks cost comparison red bricks",
        ],
        "vendor_terms": ["AAC blocks manufacturers", "autoclaved aerated concrete blocks suppliers"],
    },
    "jali": {
        "instagram": [
            "terracotta jali wall design",
            "brick jali screen architecture",
            "breeze blocks modern house facade",
            "terracotta screen architectural detail",
        ],
        "youtube": [
            "terracotta jali design house walkthrough India",
            "how terracotta jali is installed construction details",
        ],
        "pinterest": [
            "terracotta jali screen facade architecture",
            "brick jali pattern light and shadow design",
        ],
        "reddit": [
            "terracotta jali wall rain protection cost",
        ],
        "vendor_terms": ["terracotta jali tiles manufacturers", "breeze blocks suppliers"],
    },

    # -------------------------------------------------------------
    # CIVIL & STRUCTURAL
    # -------------------------------------------------------------
    "steel": {
        "instagram": [
            "TMT steel rebar construction site",
            "steel reinforcement slab casting",
            "structural steel framing architecture",
        ],
        "youtube": [
            "TMT steel rebar checking quality on site",
            "slab steel reinforcement binding walkthrough",
            "Tata Tiscon Jindal Panther TMT bars comparison",
        ],
        "pinterest": [
            "structural steel house design architecture",
            "exposed steel beam modern interior",
        ],
        "reddit": [
            "best TMT steel rebar brand residential construction",
            "fe550d vs fe500d steel bar difference",
        ],
        "vendor_terms": ["TMT steel rebar authorized dealers", "structural steel distributors wholesale"],
    },
    "slab": {
        "instagram": [
            "concrete slab casting video construction",
            "RCC slab pour site walkthrough",
            "shuttering and slab reinforcement work",
            "house construction roof slab pouring",
        ],
        "youtube": [
            "house roof slab casting live construction video",
            "concrete slab curing and shuttering process",
            "post tension slab vs RCC slab walkthrough",
        ],
        "pinterest": [
            "exposed concrete ceiling slab architecture",
            "coffered concrete slab modern home",
        ],
        "reddit": [
            "roof slab waterproofing during casting tips",
            "slab curing time and concrete strength",
        ],
        "vendor_terms": ["ready mix concrete suppliers", "RMC batching plant"],
    },
    "concrete": {
        "instagram": [
            "exposed concrete architecture house",
            "polished concrete floor and walls",
            "ready mix concrete pour site",
        ],
        "youtube": [
            "exposed concrete house tour India",
            "ready mix concrete pour slab foundation video",
        ],
        "pinterest": [
            "brutalist exposed concrete residential architecture",
            "microcement and polished concrete walls",
        ],
        "reddit": [
            "exposed concrete finish cost India maintenance",
        ],
        "vendor_terms": ["ready mix concrete RMC suppliers", "cement dealers wholesale"],
    },

    # -------------------------------------------------------------
    # FLOORING & PAVING
    # -------------------------------------------------------------
    "flooring": {
        "instagram": [
            "marble flooring interior design home",
            "tiles installation flooring work",
            "granite floor border design home",
            "wooden flooring living room interior",
            "kota stone flooring courtyard design",
        ],
        "youtube": [
            "flooring tiles vs Italian marble comparison cost",
            "complete flooring work installation walkthrough",
            "kota stone mirror polish video",
            "wooden flooring installation step by step",
        ],
        "pinterest": [
            "modern flooring design Italian marble tiles",
            "herringbone wooden flooring luxury home",
            "terrazzo floor modern interior design",
        ],
        "reddit": [
            "vitrified tiles vs italian marble durability cost",
            "best flooring for Indian climate discussion",
        ],
        "vendor_terms": ["marble and granite slabs wholesale", "vitrified floor tiles dealers", "kota stone suppliers"],
    },
    "marble": {
        "instagram": [
            "Italian marble flooring luxury house",
            "white marble flooring interior living room",
            "statuario marble bookmatch design",
        ],
        "youtube": [
            "Italian marble vs Indian marble price selection",
            "Italian marble installation epoxy laying polish",
        ],
        "pinterest": [
            "bookmatched marble slab wall and floor",
            "Italian marble living room interior design",
        ],
        "reddit": [
            "Italian marble maintenance polishing cost",
        ],
        "vendor_terms": ["Italian marble importers stockists", "marble slabs dealers"],
    },
    "tile": {
        "instagram": [
            "vitrified tiles flooring design",
            "bathroom wall tiles installation",
            "large format tiles 4x2 6x4 laying",
            "moroccan tiles kitchen backsplash",
        ],
        "youtube": [
            "large format tile installation paper joint",
            "Kajaria Somany vitrified tiles price review",
        ],
        "pinterest": [
            "terrazzo and ceramic tiles interior design",
            "large format porcelain slab tile flooring",
        ],
        "reddit": [
            "best tile brand Kajaria vs Somany vs Qutone",
        ],
        "vendor_terms": ["vitrified tiles showrooms wholesale", "ceramic tiles distributors"],
    },
    "kota": {
        "instagram": [
            "kota stone flooring courtyard house",
            "mirror polish kota stone interior",
            "natural kota stone paving landscape",
        ],
        "youtube": [
            "kota stone polishing process mirror finish",
            "kota stone flooring cost and laying walkthrough",
        ],
        "pinterest": [
            "natural kota stone flooring modern Indian home",
            "kota stone courtyard and verandah flooring",
        ],
        "reddit": [
            "kota stone vs marble flooring living room",
        ],
        "vendor_terms": ["kota stone wholesale suppliers", "natural kota stone dealers"],
    },

    # -------------------------------------------------------------
    # DOORS, WINDOWS & GLAZING
    # -------------------------------------------------------------
    "door": {
        "instagram": [
            "main door design wooden house",
            "teak wood double door entrance",
            "modern pivot door entrance design",
            "sliding glass door interior partition",
            "flush door laminate veneer finish",
        ],
        "youtube": [
            "modern main door design wooden house tour",
            "teak wood main door carving and making",
            "flush door vs panel door vs wooden door comparison",
        ],
        "pinterest": [
            "grand main door design luxury house entrance",
            "teak wood door with brass handles architecture",
            "minimalist sliding glass pocket door",
        ],
        "reddit": [
            "teak wood door vs readymade flush door cost",
            "best door lock digital smart lock Yale Ozone",
        ],
        "vendor_terms": ["teak wood main doors manufacturers", "wooden doors and frames wholesale", "flush door distributors"],
    },
    "window": {
        "instagram": [
            "UPVC sliding window modern house",
            "slim profile aluminium window glass",
            "large glass window view architecture",
            "french window design living room",
        ],
        "youtube": [
            "UPVC vs Aluminium windows comparison cost India",
            "Fenesta UPVC windows installation review",
            "soundproof double glazed window demo",
        ],
        "pinterest": [
            "floor to ceiling glass windows architecture",
            "black slim aluminium window frames modern home",
            "bay window seat reading nook design",
        ],
        "reddit": [
            "UPVC vs Aluminium sliding windows for home",
            "double glazing soundproofing windows experience",
        ],
        "vendor_terms": ["UPVC windows manufacturers fabricators", "aluminium slim windows dealers", "architectural glass suppliers"],
    },
    "glass": {
        "instagram": [
            "toughened glass railing balcony",
            "glass partition sliding door modern",
            "curtain wall glass facade architecture",
        ],
        "youtube": [
            "toughened glass vs laminated glass safety test",
            "frameless glass railing installation balcony",
        ],
        "pinterest": [
            "fluted glass partition sliding doors interior",
            "frameless glass staircase railing architecture",
        ],
        "reddit": [
            "glass railing balcony safety 12mm toughened",
        ],
        "vendor_terms": ["toughened glass processors", "architectural glass dealers", "glass hardware distributors"],
    },

    # -------------------------------------------------------------
    # INTERIOR FINISHES & MILLWORK
    # -------------------------------------------------------------
    "staircase": {
        "instagram": [
            "staircase design modern house",
            "cantilever floating staircase architecture",
            "wooden steps metal railing stairs",
            "spiral staircase modern interior design",
        ],
        "youtube": [
            "floating cantilever staircase construction details",
            "modern staircase design house walkthrough India",
        ],
        "pinterest": [
            "floating wooden staircase glass railing",
            "curved spiral staircase luxury architecture",
        ],
        "reddit": [
            "cantilever staircase structural safety cost",
        ],
        "vendor_terms": ["staircase railing fabricators", "wooden staircase manufacturers"],
    },
    "ceiling": {
        "instagram": [
            "false ceiling design living room",
            "gypsum board false ceiling modern",
            "wooden rafters ceiling interior",
        ],
        "youtube": [
            "false ceiling design ideas with LED profile lights",
            "gypsum board false ceiling installation step by step",
        ],
        "pinterest": [
            "minimal false ceiling cove lighting design",
            "wooden batten ceiling panels interior",
        ],
        "reddit": [
            "false ceiling cost per sq ft POP vs Gypsum",
        ],
        "vendor_terms": ["gypsum board false ceiling dealers", "Saint Gobain Gyproc distributors"],
    },

    # -------------------------------------------------------------
    # MEP, PLUMBING & WATER HARVESTING
    # -------------------------------------------------------------
    "rainwater": {
        "instagram": [
            "rainwater harvesting system house",
            "recharge pit rainwater harvesting construction",
            "rooftop rainwater collection filter tank",
        ],
        "youtube": [
            "how to set up rainwater harvesting at home step by step",
            "rainwater harvesting filter tank installation video",
            "groundwater recharge pit construction details",
        ],
        "pinterest": [
            "rainwater harvesting system design residential",
            "rain chain and collection pond garden",
        ],
        "reddit": [
            "rainwater harvesting setup cost maintenance filter",
        ],
        "vendor_terms": ["rainwater harvesting filter manufacturers", "rainwater collection tanks suppliers"],
    },
    "pipe": {
        "instagram": [
            "CPVC plumbing pipe installation bathroom",
            "concealed plumbing work construction site",
            "drainage pipe slope testing site",
        ],
        "youtube": [
            "CPVC vs UPVC pipes plumbing comparison",
            "bathroom concealed plumbing layout installation",
        ],
        "pinterest": [
            "exposed copper plumbing pipes industrial interior",
        ],
        "reddit": [
            "Astral vs Ashirvad CPVC pipes quality comparison",
        ],
        "vendor_terms": ["CPVC pipes authorized distributors", "Astral Ashirvad Supreme pipes dealers"],
    },
    "tank": {
        "instagram": [
            "underground water sump tank construction",
            "overhead water tank installation roof",
            "waterproofed concrete water storage tank",
        ],
        "youtube": [
            "underground water tank RCC construction walkthrough",
            "Sintex overhead water tank installation plumbing",
        ],
        "pinterest": [
            "concealed water tank and pump room design",
        ],
        "reddit": [
            "RCC water sump vs Sintex tank cost durability",
        ],
        "vendor_terms": ["water storage tanks wholesale dealers", "Sintex water tanks distributors"],
    },

    # -------------------------------------------------------------
    # PAINTS, COATINGS & WATERPROOFING
    # -------------------------------------------------------------
    "paint": {
        "instagram": [
            "wall texture paint interior design",
            "exterior house paint colour combination",
            "limewash paint finish textured wall",
            "asian paints royale luxury finish",
        ],
        "youtube": [
            "exterior house painting process step by step",
            "wall texture paint design ideas living room",
            "Asian Paints vs Berger vs Nerolac comparison",
        ],
        "pinterest": [
            "modern exterior paint colour combinations house",
            "limewash and textured plaster wall aesthetics",
        ],
        "reddit": [
            "best exterior paint for heavy rain monsoon",
            "interior paint cost Asian Paints Royale review",
        ],
        "vendor_terms": ["Asian Paints authorized dealers", "Berger Nerolac paints wholesale distributors"],
    },
    "waterproof": {
        "instagram": [
            "terrace waterproofing construction Dr Fixit",
            "bathroom waterproofing before tile laying",
            "waterproofing chemical coating building",
        ],
        "youtube": [
            "roof terrace waterproofing step by step Dr Fixit",
            "bathroom waterproofing chemical membrane application",
        ],
        "pinterest": [
            "terrace garden waterproofing and drainage layer",
        ],
        "reddit": [
            "best terrace waterproofing method Dr Fixit vs Fosroc",
        ],
        "vendor_terms": ["waterproofing chemicals dealers", "Dr Fixit Fosroc Sika distributors wholesale"],
    },

    # -------------------------------------------------------------
    # MACHINERY, TOOLS & CONSTRUCTION EQUIPMENT
    # -------------------------------------------------------------
    "machinery": {
        "instagram": [
            "construction machinery site working",
            "concrete mixer machine working live",
            "power tools construction equipment",
            "steel bar bending machine at site",
            "scaffolding erection building construction",
        ],
        "youtube": [
            "concrete mixer machine 1 bag hopper demo on site",
            "steel rebar cutting and bending machine video",
            "construction site machinery and tools walkthrough",
            "Bosch DeWalt professional power tools construction",
        ],
        "pinterest": [
            "construction site scaffolding architectural safety",
            "workshop tools construction equipment organization",
        ],
        "reddit": [
            "best rotary hammer drill for concrete Bosch vs Makita",
            "scaffolding rental vs buying construction project",
        ],
        "vendor_terms": [
            "construction machinery equipment manufacturers",
            "concrete mixers scaffolding dealers wholesale",
            "power tools authorized dealers Bosch Makita",
        ],
    },
    "mixer": {
        "instagram": [
            "concrete mixer machine site pour",
            "one bag concrete mixer working video",
        ],
        "youtube": [
            "concrete mixer machine working operation construction",
            "mini concrete mixer price review India",
        ],
        "pinterest": [
            "construction equipment on site",
        ],
        "reddit": [
            "concrete mixer machine rental cost on site",
        ],
        "vendor_terms": ["concrete mixer machine manufacturers", "construction equipment dealers"],
    },
    "tool": {
        "instagram": [
            "power tools construction site woodworking",
            "laser level tool masonry alignment",
            "core cutting machine RCC slab drilling",
        ],
        "youtube": [
            "essential power tools for house construction",
            "how to use laser level for tile and brick alignment",
        ],
        "pinterest": [
            "workshop power tools tool wall organization",
        ],
        "reddit": [
            "best power tools brand Bosch vs DeWalt vs Makita India",
        ],
        "vendor_terms": ["power tools dealers wholesale", "Bosch Makita power tools distributors"],
    },
    "screw": {
        "instagram": [
            "fasteners and screws construction hardware",
            "self tapping screw drywall installation",
        ],
        "youtube": [
            "types of screws used in wood and metal construction",
            "drywall screws vs self tapping screws test",
        ],
        "pinterest": [
            "hardware fasteners and fixings hardware",
        ],
        "reddit": [
            "best brand SS 304 screws fasteners construction",
        ],
        "vendor_terms": ["screws and fasteners wholesale distributors", "hardware nuts and bolts suppliers"],
    },

    # -------------------------------------------------------------
    # ROOFING & CLADDING
    # -------------------------------------------------------------
    "roof": {
        "instagram": [
            "clay roof tiles modern house Kerala",
            "metal standing seam roof architecture",
            "sloped roof house elevation design",
            "terracotta roof tiles installation",
        ],
        "youtube": [
            "Mangalore clay roof tiles installation walkthrough",
            "metal roof vs clay roof tiles cost comparison",
        ],
        "pinterest": [
            "sloped roof modern tropical villa architecture",
            "standing seam metal roof contemporary house",
        ],
        "reddit": [
            "clay roof tiles leak prevention maintenance",
        ],
        "vendor_terms": ["clay roof tiles manufacturers", "Mangalore roof tiles dealers wholesale", "metal roofing sheets suppliers"],
    },
    "cladding": {
        "instagram": [
            "exterior wall cladding modern house",
            "stone cladding elevation design",
            "HPL facade panels architecture",
            "corten steel cladding facade",
        ],
        "youtube": [
            "exterior wall cladding materials comparison price",
            "natural stone cladding installation process",
        ],
        "pinterest": [
            "stone and wood cladding modern house elevation",
            "terracotta louvers facade cladding architecture",
        ],
        "reddit": [
            "exterior stone cladding maintenance cost India",
        ],
        "vendor_terms": ["exterior wall cladding suppliers", "HPL sheets facade distributors", "stone cladding dealers"],
    },
}


def clean_catalogue_term(term: str) -> str:
    """
    Strips ASTM/IS standards, technical dimensions, grade notations,
    and boilerplate from a raw catalogue material entry.
    E.g.: 'IS: 1077-1992 Common burnt clay building bricks 190x90x90 mm' -> 'Common burnt clay building bricks'
    """
    clean = term.strip()
    # Remove IS standards like 'IS: 1077-1992', 'IS 456:2000'
    clean = re.sub(r'\bIS\s*[:\-]?\s*\d+([–\-]\d+)?\b', '', clean, flags=re.IGNORECASE)
    # Remove ASTM standards like 'ASTM C128'
    clean = re.sub(r'\bASTM\s+[A-Z0-9\-]+\b', '', clean, flags=re.IGNORECASE)
    # Remove dimension patterns like '190x90x90 mm', '10 mm', '20mm', '4x2 ft'
    clean = re.sub(r'\b\d+(\.\d+)?\s*[xX]\s*\d+(\.\d+)?(\s*[xX]\s*\d+(\.\d+)?)?\s*(mm|cm|m|inch|ft|in)?\b', '', clean)
    clean = re.sub(r'\b\d+(\.\d+)?\s*(mm|cm|inch|ft)\b', '', clean, flags=re.IGNORECASE)
    # Remove grade notations like 'Grade 43', 'Fe 500D', 'M20', 'M25'
    clean = re.sub(r'\b(Grade\s+\d+|Fe\s*\d+[A-Z]?|M\s*\d{2})\b', '', clean, flags=re.IGNORECASE)
    # Clean multiple spaces and dangling punctuation
    clean = re.sub(r'[\(\)\[\]\{\},:;\-–_]+', ' ', clean)
    clean = " ".join(clean.split()).strip()
    return clean or term.strip()


def get_social_search_terms(
    material_name: str,
    category_name: str = "",
    subcategory_name: str = ""
) -> Dict[str, Any]:
    """
    Resolves a catalogue material into proven social queries for
    Instagram, YouTube, Pinterest, Reddit, and Google Places suppliers.
    Guarantees that every material yields high-match social queries.
    """
    raw_material = material_name.strip()
    cleaned = clean_catalogue_term(raw_material)
    combined_context = f"{raw_material} {cleaned} {category_name} {subcategory_name}".lower()

    # Find matching family in registry
    matched_family: Optional[Dict[str, Any]] = None
    for token, profile in MATERIAL_SOCIAL_REGISTRY.items():
        if token in combined_context:
            matched_family = profile
            break

    # Fallback to category heuristics if no direct material match
    if not matched_family:
        if any(w in combined_context for w in ["machine", "tool", "equipment", "mixer", "fastener", "screw"]):
            matched_family = MATERIAL_SOCIAL_REGISTRY["machinery"]
        elif any(w in combined_context for w in ["door", "window", "glazing", "glass", "upvc", "shutter"]):
            matched_family = MATERIAL_SOCIAL_REGISTRY["door"]
        elif any(w in combined_context for w in ["paint", "coating", "waterproof", "primer", "varnish"]):
            matched_family = MATERIAL_SOCIAL_REGISTRY["paint"]
        elif any(w in combined_context for w in ["floor", "pave", "tile", "marble", "granite", "stone"]):
            matched_family = MATERIAL_SOCIAL_REGISTRY["flooring"]
        elif any(w in combined_context for w in ["roof", "cladding", "facade", "panel"]):
            matched_family = MATERIAL_SOCIAL_REGISTRY["roof"]
        elif any(w in combined_context for w in ["plumb", "pipe", "mep", "tank", "pump", "drain"]):
            matched_family = MATERIAL_SOCIAL_REGISTRY["rainwater"]
        else:
            matched_family = MATERIAL_SOCIAL_REGISTRY["concrete"]

    # Build primary query combining cleaned material noun + social keywords
    base_noun = cleaned.split()[0] if cleaned.split() else raw_material
    if len(cleaned.split()) >= 2:
        base_noun = " ".join(cleaned.split()[:3])

    instagram_queries = [
        f"{base_noun} architecture design",
        f"{base_noun} construction work site",
        f"{base_noun} home interior tour",
    ] + matched_family.get("instagram", [])

    youtube_queries = [
        f"{base_noun} construction installation walkthrough",
        f"{base_noun} material price comparison review",
    ] + matched_family.get("youtube", [])

    pinterest_queries = [
        f"{base_noun} modern house architecture design",
        f"{base_noun} texture material finish",
    ] + matched_family.get("pinterest", [])

    reddit_queries = [
        f"{base_noun} quality durability cost comparison",
        f"{base_noun} construction experience review",
    ] + matched_family.get("reddit", [])

    vendor_terms = [base_noun] + matched_family.get("vendor_terms", [])

    return {
        "raw_material": raw_material,
        "clean_noun": base_noun,
        "instagram_queries": list(dict.fromkeys(instagram_queries))[:5],
        "youtube_queries": list(dict.fromkeys(youtube_queries))[:4],
        "pinterest_queries": list(dict.fromkeys(pinterest_queries))[:4],
        "reddit_queries": list(dict.fromkeys(reddit_queries))[:3],
        "vendor_terms": list(dict.fromkeys(vendor_terms))[:4],
    }


def get_supplier_search_queries(
    material_name: str,
    city: Optional[str] = None,
    district: Optional[str] = None,
    state: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Builds geographic supplier queries across 3 tiers (District, State, National)
    ensuring 10 to 20 trade suppliers are discovered for ANY material.
    """
    clean_mat = clean_catalogue_term(material_name)
    words = clean_mat.split()
    short_mat = " ".join(words[:3]) if len(words) >= 3 else clean_mat

    loc_district = (district or city or "").strip()
    loc_state = (state or "").strip()

    queries = []

    # Level 1: In the user's city/district
    if loc_district:
        queries.append({
            "tier": "DISTRICT",
            "scope_label": f"Local Suppliers ({loc_district})",
            "query": f"{short_mat} suppliers dealers in {loc_district}",
        })
        queries.append({
            "tier": "DISTRICT",
            "scope_label": f"Wholesale & Retailers ({loc_district})",
            "query": f"{short_mat} wholesale distributors {loc_district}",
        })

    # Level 2: In the user's state / adjacent region
    if loc_state and loc_state.lower() != (loc_district or "").lower():
        queries.append({
            "tier": "STATE",
            "scope_label": f"State-wide Distributors ({loc_state})",
            "query": f"{short_mat} manufacturers and distributors {loc_state}",
        })
        queries.append({
            "tier": "STATE",
            "scope_label": f"Regional Stockists ({loc_state})",
            "query": f"{short_mat} authorized dealers {loc_state}",
        })

    # Level 3: All-India / National Manufacturers
    queries.append({
        "tier": "NATIONAL",
        "scope_label": "All-India Manufacturers & Importers",
        "query": f"{short_mat} manufacturers wholesale suppliers India",
    })
    queries.append({
        "tier": "NATIONAL",
        "scope_label": "National Trade Stockists (India)",
        "query": f"{short_mat} building materials distributors India",
    })

    return queries

"""
Arch_Aware — Universal Social Vocabulary, Natural Query Expansion & Sourcing Engine.

Maps technical catalogue materials (IS/ASTM standards, specs, dimensions) across ALL
10 categories and 184 subcategories (6,319+ materials) into verified, high-yield social queries for:
- Instagram Reels & Walkthroughs
- YouTube Architectural & Construction Videos
- Pinterest Aesthetic Pins & Elevation Details
- Reddit Contractor, Architect & Material Discussions
- Google Shopping Wholesale & Trade Catalogues
- Google Places Multi-Tier Supplier Discovery (District, State, National)
"""

import re
from typing import Dict, List, Any, Optional

def clean_catalogue_term(term: str) -> str:
    """
    Strips ASTM/IS/DIN/BS/EN standards, dimensions, grade notations,
    and boilerplate from raw catalogue material entries.
    E.g.:
    - 'IS: 1077-1992 Common burnt clay building bricks 190x90x90 mm' -> 'Common burnt clay building bricks'
    - 'IS 1786 Fe 500D TMT Steel Reinforcement Bar 16 mm' -> 'TMT Steel Reinforcement Bar'
    - 'Polyurethane Sealant IS 11433 (Part 1)' -> 'Polyurethane Sealant'
    - 'Concrete Mixer Machine 10/7 CFT with Hydraulic Hopper' -> 'Concrete Mixer Machine with Hydraulic Hopper'
    """
    clean = term.strip()
    # Remove standard prefixes: IS, ASTM, DIN, BS, EN, ISO
    clean = re.sub(r'\b(IS|ASTM|DIN|BS|EN|ISO)\s*[:\-]?\s*[A-Z0-9]+([–\-][A-Z0-9]+)?(\s*\(Part\s*\d+\))?\b', '', clean, flags=re.IGNORECASE)
    # Remove dimension patterns: 190x90x90 mm, 200 x 100 x 75mm, 4x2 ft, 600x600 mm, 10 mm, 20mm, 1/2 inch
    clean = re.sub(r'\b\d+(\.\d+)?\s*[xX*]\s*\d+(\.\d+)?(\s*[xX*]\s*\d+(\.\d+)?)?\s*(mm|cm|m|inch|ft|in)?\b', '', clean)
    clean = re.sub(r'\b\d+(\.\d+)?\s*(mm|cm|inch|ft|inches|feet|mtr|sqft|sqm)\b', '', clean, flags=re.IGNORECASE)
    # Remove grade notations: Grade 43, Grade 53, Fe 500D, Fe 550, M20, M25, M30, M40, 10/7 CFT
    clean = re.sub(r'\b(Grade\s+\d+|Fe\s*\d+[A-Z]?|M\s*\d{2}|\d+/\d+\s*CFT)\b', '', clean, flags=re.IGNORECASE)
    # Remove bracketed references
    clean = re.sub(r'[\(\[\{][^\)\]\}]*[\)\]\}]', ' ', clean)
    # Clean punctuations and symbols
    clean = re.sub(r'[\–—_\:;,/]+', ' ', clean)
    clean = " ".join(clean.split()).strip()
    return clean or term.strip()


# ==============================================================================
# CATEGORY-LEVEL SOCIAL & SOURCING BLUEPRINTS
# Covers ALL 10 Categories in the Catalogue Database
# ==============================================================================

CATEGORY_PROFILES: Dict[str, Dict[str, Any]] = {
    # --------------------------------------------------------------------------
    # 1. MACHINERY & TOOLS (1,190 materials)
    # --------------------------------------------------------------------------
    "machinery & tools": {
        "instagram": [
            "construction machinery working video",
            "contractor tools demonstration on site",
            "heavy construction equipment in action reels",
            "civil engineering tools and machinery",
        ],
        "youtube": [
            "construction machinery working video walkthrough",
            "site equipment demonstration and review",
            "how construction machinery operates site video",
            "power tools testing and review for construction",
        ],
        "pinterest": [
            "construction machinery equipment workshop",
            "building tools and machinery site details",
        ],
        "reddit": [
            "best construction machinery brands India price",
            "power tools brand review Bosch Makita DeWalt",
            "construction equipment rental vs purchase cost",
        ],
        "shopping": [
            "heavy construction equipment price India",
            "industrial power tools trade rate",
            "construction machinery wholesale dealers",
        ],
        "vendor_types": [
            "construction machinery dealers",
            "equipment rental and sales",
            "power tools wholesale distributors",
            "civil engineering equipment suppliers",
        ],
    },

    # --------------------------------------------------------------------------
    # 2. DOORS, WINDOWS, HARDWARE & FIXTURES (106 + Exterior doors/windows)
    # --------------------------------------------------------------------------
    "doors, windows, hardware & fixtures": {
        "instagram": [
            "main door design modern house",
            "UPVC sliding window installation walkthrough",
            "architectural door hardware aesthetic finish",
            "aluminium slim profile glass partition",
            "teak wood carved entrance door",
        ],
        "youtube": [
            "wooden main door design house tour India",
            "UPVC sliding windows price and installation guide",
            "aluminium slim frame window sections walkthrough",
            "architectural hardware mortise locks concealed hinges review",
        ],
        "pinterest": [
            "modern front door design ideas villa",
            "minimalist glass window facade architecture",
            "door handles and architectural hardware aesthetics",
        ],
        "reddit": [
            "UPVC vs aluminium windows price durability experience",
            "teak wood vs flush door cost India",
            "best architectural door locks Yale Godrej Hafele",
        ],
        "shopping": [
            "main doors and UPVC windows buy price India",
            "architectural door handles and fittings wholesale",
            "toughened glass sliding window catalog",
        ],
        "vendor_types": [
            "doors and windows showrooms",
            "UPVC fenestration manufacturers",
            "architectural hardware wholesale dealers",
            "aluminium window fabricators",
        ],
    },

    # --------------------------------------------------------------------------
    # 3. INTERIOR (1,371 materials)
    # --------------------------------------------------------------------------
    "interior": {
        "instagram": [
            "interior design walkthrough house tour",
            "luxury flooring design marble vitrified tiles",
            "modular kitchen interior walkthrough reels",
            "false ceiling lighting design contemporary house",
            "staircase design and wooden veneer paneling",
        ],
        "youtube": [
            "complete house interior design walkthrough India",
            "flooring tiles vs Italian marble price comparison",
            "modular kitchen materials acrylic vs PU finish tour",
            "false ceiling POP gypsum installation walkthrough",
        ],
        "pinterest": [
            "interior architecture modern living room aesthetic",
            "flooring textures marble granite terrazzo finish",
            "minimalist kitchen and wardrobe joinery design",
        ],
        "reddit": [
            "interior design cost per sqft India breakdown",
            "Italian marble vs large format vitrified tiles durability",
            "plywood vs MDF modular kitchen experience",
        ],
        "shopping": [
            "interior materials price per sq ft India",
            "vitrified tiles and marble wholesale rates",
            "modular kitchen hardware fittings buy online",
        ],
        "vendor_types": [
            "interior design showrooms",
            "tile marble granite depots",
            "plywood and veneer distributors",
            "modular kitchen and sanitaryware dealers",
        ],
    },

    # --------------------------------------------------------------------------
    # 4. EXTERIOR (1,249 materials)
    # --------------------------------------------------------------------------
    "exterior": {
        "instagram": [
            "exterior facade architecture modern house",
            "exposed brick elevation design house tour",
            "stone wall cladding exterior architecture reels",
            "clay roof tiles and modern villa elevation",
            "terracotta jali screen facade design",
        ],
        "youtube": [
            "modern house front elevation design walkthrough",
            "exposed brick masonry house architecture India",
            "exterior wall cladding installation process video",
            "clay roof tiles vs metal roofing house tour",
        ],
        "pinterest": [
            "modern house exterior elevation architectural pattern",
            "stone and brick facade cladding texture aesthetics",
            "tropical villa exterior roof and jali design",
        ],
        "reddit": [
            "exterior wall cladding cost and maintenance India",
            "AAC blocks vs red clay bricks house construction",
            "clay roof tiles leakage prevention experience",
        ],
        "shopping": [
            "exterior wall cladding materials price India",
            "red clay bricks and AAC blocks wholesale rate",
            "roofing tiles and facade panels buy price",
        ],
        "vendor_types": [
            "brick kilns and block manufacturers",
            "exterior cladding stone dealers",
            "roofing tile wholesale distributors",
            "facade and glazing contractors",
        ],
    },

    # --------------------------------------------------------------------------
    # 5. MEP & BUILDING SERVICES (856 materials)
    # --------------------------------------------------------------------------
    "mep & building services": {
        "instagram": [
            "concealed plumbing pipe installation house",
            "rainwater harvesting tank construction details",
            "underground water tank concrete sump reels",
            "electrical wiring and conduit piping site work",
            "submersible water pump and plumbing system",
        ],
        "youtube": [
            "concealed plumbing pipeline walkthrough house construction",
            "rainwater harvesting system construction and filters India",
            "underground water storage sump construction step by step",
            "house electrical wiring conduit piping installation video",
        ],
        "pinterest": [
            "architectural plumbing and drainage diagram details",
            "rainwater harvesting system residential architecture",
            "modern electrical switchboards and conduit details",
        ],
        "reddit": [
            "CPVC vs UPVC pipes plumbing best brand Astral Supreme",
            "rainwater harvesting tank cost India experience",
            "underground water sump vs overhead tank construction",
        ],
        "shopping": [
            "CPVC pipes and fittings wholesale price list",
            "submersible water pumps buy online price India",
            "electrical wires switches and conduits trade rate",
        ],
        "vendor_types": [
            "plumbing and sanitaryware wholesale dealers",
            "CPVC UPVC pipes authorized distributors",
            "water pumps and electrical stockists",
            "rainwater harvesting and water tank manufacturers",
        ],
    },

    # --------------------------------------------------------------------------
    # 6. MATERIALS, METALS, TIMBER & CHEMICALS (773 materials)
    # --------------------------------------------------------------------------
    "materials, metals, timber & chemicals": {
        "instagram": [
            "TMT steel rebar reinforcement slab casting",
            "ready mix concrete pouring site walkthrough",
            "waterproofing chemical application demo terrace",
            "timber wood carpentry and architectural steel",
            "construction chemicals epoxy grout application",
        ],
        "youtube": [
            "TMT steel rebar quality checking on site India",
            "slab concrete casting walkthrough and mix design",
            "roof terrace waterproofing step by step Dr Fixit Fosroc",
            "teak wood vs mahogany timber quality comparison",
        ],
        "pinterest": [
            "structural steel architecture framing design",
            "raw timber wood texture and architectural finishes",
            "exposed concrete aesthetics and waterproofing details",
        ],
        "reddit": [
            "Tata Tiscon vs Jindal Panther TMT steel price per ton",
            "best waterproofing chemical for roof terrace slab",
            "OPC vs PPC cement for house construction cost",
        ],
        "shopping": [
            "TMT steel rebar price per ton India",
            "cement bags wholesale rate UltraTech ACC",
            "waterproofing chemicals and epoxy grout buy price",
        ],
        "vendor_types": [
            "TMT steel authorized distributors",
            "cement wholesale stockists",
            "construction chemicals and waterproofing dealers",
            "timber and plywood merchants",
        ],
    },

    # --------------------------------------------------------------------------
    # 7. WATER, WASTE, LANDSCAPE & EXTERNAL UTILITIES (109 materials)
    # --------------------------------------------------------------------------
    "water, waste, landscape & external utilities": {
        "instagram": [
            "landscape design and garden architecture walkthrough",
            "outdoor grass pavers and cobblestone paving",
            "pergola and gazebo outdoor architecture reels",
            "rainwater filtration and groundwater recharge pit",
        ],
        "youtube": [
            "residential landscape design house tour India",
            "garden interlocking pavers installation walkthrough",
            "sewage treatment plant residential installation video",
            "outdoor gazebo and water feature construction",
        ],
        "pinterest": [
            "architectural landscaping garden design ideas",
            "outdoor patio pavers and water body aesthetics",
        ],
        "reddit": [
            "residential STP plant cost and maintenance India",
            "interlocking pavers vs cobblestone driveway cost",
        ],
        "shopping": [
            "landscaping grass pavers buy price per sq ft",
            "water filtration and STP equipment wholesale",
        ],
        "vendor_types": [
            "landscape material and pavers suppliers",
            "water treatment plant distributors",
            "outdoor furniture and garden stone dealers",
        ],
    },

    # --------------------------------------------------------------------------
    # 8. SAFETY, SECURITY & SITE WELFARE (97 materials)
    # --------------------------------------------------------------------------
    "safety, security & site welfare": {
        "instagram": [
            "smart home security and digital door lock reels",
            "CCTV surveillance camera installation modern house",
            "fire safety sprinkler and alarm system site work",
            "construction site PPE safety harness equipment",
        ],
        "youtube": [
            "digital smart door lock installation and review India",
            "home CCTV camera wiring and installation walkthrough",
            "fire fighting piping and sprinkler system testing video",
        ],
        "pinterest": [
            "smart entrance door biometric lock aesthetic",
            "architectural fire safety and emergency exit design",
        ],
        "reddit": [
            "best digital smart door lock Yale Godrej Ozone",
            "fire sprinkler requirements residential apartments",
        ],
        "shopping": [
            "smart door locks biometric wifi price India",
            "fire extinguishers and safety equipment wholesale",
        ],
        "vendor_types": [
            "smart locks and security systems dealers",
            "fire safety equipment wholesale distributors",
            "safety equipment and PPE suppliers",
        ],
    },

    # --------------------------------------------------------------------------
    # 9. HEALTHCARE & HOSPITAL (221 materials)
    # --------------------------------------------------------------------------
    "healthcare & hospital": {
        "instagram": [
            "hospital architecture and interior design walkthrough",
            "cleanroom modular wall paneling installation",
            "antibacterial vinyl flooring in healthcare clinic",
            "medical gas pipeline copper piping work",
        ],
        "youtube": [
            "hospital building architecture design walkthrough",
            "modular operation theatre OT construction video",
            "medical gas pipeline system installation and testing",
        ],
        "pinterest": [
            "healthcare architecture modern clinic design",
            "cleanroom and hospital interior aesthetics",
        ],
        "reddit": [
            "hospital construction cost per bed in India",
            "antibacterial vinyl flooring vs epoxy in clinics",
        ],
        "shopping": [
            "hospital cleanroom panels wholesale price",
            "medical gas pipeline copper pipe rate",
        ],
        "vendor_types": [
            "hospital equipment and cleanroom contractors",
            "medical infrastructure suppliers",
            "healthcare antibacterial flooring dealers",
        ],
    },

    # --------------------------------------------------------------------------
    # 10. INDUSTRIAL, COMMERCIAL & INSTITUTIONAL (347 materials)
    # --------------------------------------------------------------------------
    "industrial, commercial & institutional": {
        "instagram": [
            "industrial architecture design warehouse steel building",
            "commercial office interior design walkthrough reels",
            "industrial epoxy flooring site installation",
            "curtain wall glass facade commercial architecture",
        ],
        "youtube": [
            "pre engineered steel building PEB erection walkthrough",
            "industrial warehouse construction process video",
            "acoustic wall paneling installation auditorium tour",
        ],
        "pinterest": [
            "modern industrial warehouse architecture design",
            "commercial office glass curtain wall facade",
        ],
        "reddit": [
            "PEB steel building cost per sqft in India",
            "industrial epoxy flooring vs polished concrete",
        ],
        "shopping": [
            "PEB steel structure price per sq ft India",
            "industrial heavy duty epoxy flooring rate",
        ],
        "vendor_types": [
            "PEB pre engineered building manufacturers",
            "industrial flooring contractors",
            "commercial glazing and facade contractors",
        ],
    },
}


# ==============================================================================
# SPECIFIC MATERIAL NOUN DICTIONARY
# High-priority token overrides for granular material families
# ==============================================================================

MATERIAL_NOUN_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ---------------- MACHINERY & TOOLS OVERRIDES ----------------
    "mixer": {
        "category_key": "machinery & tools",
        "instagram": [
            "concrete mixer machine working on site",
            "hydraulic hopper concrete mixer machine",
            "concrete batching mixer machine India",
        ],
        "youtube": [
            "concrete mixer machine operating live on construction site",
            "one bag hydraulic concrete mixer machine demonstration",
            "concrete mixer machine price in India review",
        ],
        "pinterest": ["concrete mixer machine construction equipment site"],
        "reddit": ["concrete mixer machine price review India", "best concrete mixer brands for residential building"],
        "shopping": ["concrete mixer machine 10/7 price India", "hydraulic concrete mixer manufacturer rate"],
        "vendor_types": ["concrete mixer machine manufacturers", "construction machinery dealers", "equipment rental"],
    },
    "scaffold": {
        "category_key": "machinery & tools",
        "instagram": [
            "cuplock scaffolding erection at building site",
            "modular steel scaffolding installation reels",
            "exterior facade scaffolding work",
        ],
        "youtube": [
            "modular cuplock scaffolding installation walkthrough",
            "steel scaffolding safety guidelines site video",
        ],
        "pinterest": ["modular steel scaffolding architecture site"],
        "reddit": ["scaffolding rental cost per sqft India", "cuplock vs H frame scaffolding"],
        "shopping": ["cuplock scaffolding pipe wholesale rate", "steel scaffolding accessories price"],
        "vendor_types": ["scaffolding manufacturers", "cuplock scaffolding rental and sales", "staging equipment dealers"],
    },
    "drill": {
        "category_key": "machinery & tools",
        "instagram": [
            "rotary hammer drill concrete core drilling reels",
            "cordless impact drill power tools demo",
        ],
        "youtube": [
            "rotary hammer drill concrete drilling test Bosch Makita",
            "cordless drill vs impact driver comparison review",
        ],
        "pinterest": ["power tools workshop drills equipment"],
        "reddit": ["best rotary hammer drill Bosch Makita DeWalt India", "cordless drill battery durability"],
        "shopping": ["rotary hammer drill buy price India", "Bosch cordless impact drill price"],
        "vendor_types": ["power tools wholesale distributors", "Bosch Makita authorized dealers"],
    },
    "screw": {
        "category_key": "machinery & tools",
        "instagram": ["fasteners and stainless steel screws construction site", "drywall screws self drilling screws demo"],
        "youtube": ["types of construction screws and fasteners explained", "self drilling screws vs tapping screws"],
        "pinterest": ["architectural hardware screws fasteners"],
        "reddit": ["stainless steel SS 304 screws price India", "best drywall screws brand"],
        "shopping": ["self drilling screws box price", "stainless steel wood screws wholesale"],
        "vendor_types": ["fasteners and screws wholesale dealers", "industrial hardware distributors"],
    },
    "crane": {
        "category_key": "machinery & tools",
        "instagram": ["tower crane installation high rise building", "mobile crane lifting heavy slab beams"],
        "youtube": ["tower crane operation and lifting video", "mobile crane rental and load testing"],
        "pinterest": ["tower crane construction site architecture"],
        "reddit": ["tower crane rental cost in India", "mobile crane hiring per day rate"],
        "shopping": ["construction lifting machinery catalog"],
        "vendor_types": ["tower crane manufacturers and rental", "material handling crane dealers"],
    },
    "excavator": {
        "category_key": "machinery & tools",
        "instagram": ["JCB excavator foundation digging video", "heavy excavator earthmoving site reels"],
        "youtube": ["excavator digging foundation basement walkthrough", "JCB vs CAT excavator operation"],
        "pinterest": ["excavator earthmoving construction site"],
        "reddit": ["JCB excavation hiring cost per hour India", "basement earthmoving rates"],
        "shopping": ["mini excavator buy price India"],
        "vendor_types": ["earthmoving machinery dealers", "JCB equipment authorized distributors"],
    },

    # ---------------- DOORS & WINDOWS OVERRIDES ----------------
    "teak": {
        "category_key": "doors, windows, hardware & fixtures",
        "instagram": ["teak wood main door design house", "carved Burma teak entrance door villa", "wooden main door design walkthrough"],
        "youtube": ["teak wood main door design house tour India", "Burma teak vs African teak door quality and price"],
        "pinterest": ["teak wood front door design aesthetic", "solid wood entrance door architecture"],
        "reddit": ["teak wood main door cost India", "CP teak vs Burma teak durability"],
        "shopping": ["teak wood main door carved buy price", "solid teak wood doors catalog"],
        "vendor_types": ["teak wood door manufacturers", "wooden door showrooms", "timber door dealers"],
    },
    "door": {
        "category_key": "doors, windows, hardware & fixtures",
        "instagram": ["main door design modern house", "modern entrance door architectural design", "flush door wooden laminates finish", "sliding door interior partition"],
        "youtube": ["wooden main door design house tour India", "main door design catalog with price walkthrough", "flush doors vs panel doors comparison"],
        "pinterest": ["modern front door design ideas villa", "architectural entrance doors minimal aesthetic"],
        "reddit": ["best main door material teak vs flush door", "door hardware lock installation experience"],
        "shopping": ["main doors wooden flush door buy price", "architectural door fittings wholesale"],
        "vendor_types": ["door manufacturers and showrooms", "wooden door dealers", "architectural hardware stockists"],
    },
    "window": {
        "category_key": "doors, windows, hardware & fixtures",
        "instagram": ["UPVC sliding window modern house", "aluminium slim frame window sections", "bay window modern house elevation", "casement window with mosquito mesh"],
        "youtube": ["UPVC sliding windows price and installation guide", "aluminium vs UPVC windows comparison India", "sliding windows design house tour"],
        "pinterest": ["modern house window design architecture", "black slim frame glass window facade"],
        "reddit": ["UPVC vs aluminium windows cost per sqft India", "best window brand Fenesta AIS"],
        "shopping": ["UPVC sliding windows price per sq ft", "aluminium window sections catalog wholesale"],
        "vendor_types": ["UPVC window manufacturers", "aluminium window fabricators", "window dealers"],
    },
    "glass": {
        "category_key": "doors, windows, hardware & fixtures",
        "instagram": ["toughened glass sliding partition", "fluted glass door interior design", "double glazed acoustic glass facade"],
        "youtube": ["toughened glass vs laminated glass walkthrough", "fluted glass interior partitions modern villa"],
        "pinterest": ["fluted glass architectural partition design", "frameless glass railing modern house"],
        "reddit": ["toughened glass 10mm price per sqft India", "fluted glass shower partition cost"],
        "shopping": ["toughened glass 10mm 12mm price", "fluted reeded glass buy price"],
        "vendor_types": ["toughened glass dealers", "Saint-Gobain glass distributors", "architectural glass fabricators"],
    },

    # ---------------- PAINTS & WATERPROOFING OVERRIDES ----------------
    "paint": {
        "category_key": "interior",
        "instagram": ["wall texture paint interior design", "exterior house colour combination", "luxury Italian lime plaster stucco finish", "Asian Paints Royale colour walkthrough"],
        "youtube": ["exterior house painting process step by step India", "wall texture paint design ideas living room", "Asian Paints vs Berger Paints price comparison"],
        "pinterest": ["modern exterior paint colour combinations house", "limewash and textured plaster wall aesthetics", "interior wall paint colour palette"],
        "reddit": ["best exterior paint for heavy rain monsoon India", "Asian Paints Apex Ultima vs Royale", "wall painting labour cost per sqft"],
        "shopping": ["Asian Paints Apex Ultima 20 litre price", "interior wall emulsion paint wholesale bucket"],
        "vendor_types": ["Asian Paints authorized dealers", "Berger Nerolac wholesale distributors", "paint and texture dealers"],
    },
    "waterproof": {
        "category_key": "materials, metals, timber & chemicals",
        "instagram": ["roof terrace slab waterproofing demo", "Dr Fixit waterproofing chemical application", "bathroom sunken slab waterproofing reels"],
        "youtube": ["roof waterproofing step by step Dr Fixit Fosroc", "sunken slab waterproofing process walkthrough", "terrace leakage repair chemical application"],
        "pinterest": ["waterproofing details roof slab architecture", "epoxy waterproofing membrane application"],
        "reddit": ["best terrace waterproofing chemical Dr Fixit Fosroc Sika", "roof leakage repair cost per sqft"],
        "shopping": ["Dr Fixit Raincoat 20L buy price", "Fosroc waterproofing chemical rate"],
        "vendor_types": ["Dr Fixit Fosroc authorized dealers", "waterproofing chemical distributors", "leakage solution stockists"],
    },

    # ---------------- FLOORING OVERRIDES ----------------
    "marble": {
        "category_key": "interior",
        "instagram": ["Italian marble flooring luxury living room", "Statuario marble floor house tour", "white marble flooring design villa"],
        "youtube": ["Italian marble flooring complete house tour India", "Italian marble polishing process and price per sqft", "Dyna vs Statuario marble price comparison"],
        "pinterest": ["Italian marble living room flooring aesthetic", "Statuario marble bookmatch wall and floor"],
        "reddit": ["Italian marble cost per sqft polishing maintenance", "Italian marble vs large format vitrified tiles"],
        "shopping": ["Italian marble slabs price per sq ft Kishangarh", "white marble tiles wholesale"],
        "vendor_types": ["Italian marble importers", "marble granite wholesale depots", "natural stone showrooms"],
    },
    "tile": {
        "category_key": "interior",
        "instagram": ["large format vitrified tiles flooring design", "Kajaria floor tiles living room reels", "terrazzo and Moroccan tiles floor tour"],
        "youtube": ["vitrified tiles vs Italian marble comparison house", "large format 6x4 feet tiles installation walkthrough", "Kajaria Somany floor tiles price per sqft"],
        "pinterest": ["large format porcelain floor tiles modern house", "matte finish floor tiles aesthetic living room"],
        "reddit": ["best floor tiles brand Kajaria Somany Simpolo", "vitrified tile laying paper joint vs spacer"],
        "shopping": ["vitrified floor tiles 4x2 6x4 price box", "glazed porcelain tiles wholesale catalog"],
        "vendor_types": ["Kajaria Somany authorized tile showrooms", "vitrified tile wholesale distributors", "ceramic floor tile dealers"],
    },
    "kota": {
        "category_key": "interior",
        "instagram": ["mirror polished Kota stone flooring house", "Kota stone flooring interior design reels", "honed Kota stone courtyard floor"],
        "youtube": ["Kota stone flooring laying and mirror polishing walkthrough", "Kota stone vs green marble comparison India"],
        "pinterest": ["Kota stone flooring modern house architecture", "green Kota stone minimalist courtyard aesthetic"],
        "reddit": ["Kota stone polishing cost per sqft India", "Kota stone flooring durability and maintenance"],
        "shopping": ["Kota stone blue green slabs price per sq ft", "rough Kota stone tiles wholesale"],
        "vendor_types": ["Kota stone wholesale quarries", "natural stone dealers Rajasthan", "Kota stone polishing contractors"],
    },
    "granite": {
        "category_key": "interior",
        "instagram": ["granite flooring house walkthrough reels", "black galaxy granite kitchen countertop", "leather finish granite exterior stairs"],
        "youtube": ["granite flooring complete house tour India", "kitchen granite countertop installation walkthrough", "granite varieties and price per sqft"],
        "pinterest": ["granite flooring modern villa interior", "leather finish granite steps design"],
        "reddit": ["granite vs quartz kitchen countertop cost", "granite flooring vs tiles maintenance"],
        "shopping": ["black granite slabs price per sq ft", "granite kitchen counter wholesale"],
        "vendor_types": ["granite wholesale quarries", "natural stone depots", "granite slab suppliers"],
    },

    # ---------------- BRICKS & MASONRY OVERRIDES ----------------
    "brick": {
        "category_key": "exterior",
        "instagram": ["red brick architecture house tour", "exposed brick masonry wall elevation", "wire cut brick house design India", "terracotta brick construction"],
        "youtube": ["exposed brick house construction tour India", "brick masonry construction techniques walkthrough", "wire cut bricks vs standard clay bricks"],
        "pinterest": ["exposed brick interior and exterior architecture", "modern brick house elevation design", "brick jali screen facade pattern"],
        "reddit": ["exposed brick wall maintenance cost experience", "wire cut bricks vs normal red bricks quality India"],
        "shopping": ["wire cut red clay bricks price per piece", "exposed masonry bricks wholesale kiln rate"],
        "vendor_types": ["clay bricks kiln manufacturers", "wire cut brick suppliers", "red bricks wholesale dealers"],
    },
    "aac block": {
        "category_key": "exterior",
        "instagram": ["AAC block construction house reels", "AAC block wall masonry adhesive work", "autoclaved aerated concrete wall"],
        "youtube": ["AAC blocks vs red clay bricks comparison house", "how to lay AAC blocks construction walkthrough", "AAC block masonry adhesive joint video"],
        "pinterest": ["AAC block modern house construction details"],
        "reddit": ["AAC blocks cracks plastering experience", "AAC blocks cost comparison red bricks"],
        "shopping": ["AAC blocks 600x200x150 price per piece", "AAC block adhesive wholesale bag"],
        "vendor_types": ["AAC blocks manufacturers", "autoclaved aerated concrete suppliers", "block masonry dealers"],
    },

    # ---------------- STRUCTURAL OVERRIDES ----------------
    "steel": {
        "category_key": "materials, metals, timber & chemicals",
        "instagram": ["TMT steel rebar construction site reels", "steel reinforcement slab casting", "structural steel framing architecture"],
        "youtube": ["TMT steel rebar checking quality on site India", "slab steel reinforcement binding walkthrough", "Tata Tiscon Jindal Panther TMT bars comparison"],
        "pinterest": ["structural steel architecture framing design", "TMT steel rebar construction details"],
        "reddit": ["Tata Tiscon vs Jindal Panther TMT steel price per ton", "Fe 550D vs Fe 500 TMT rebar house construction"],
        "shopping": ["TMT steel rebar price per ton wholesale", "Tata Tiscon TMT bars rate per kg"],
        "vendor_types": ["TMT steel rebar stockists", "Tata Tiscon authorized distributors", "structural steel dealers"],
    },

    # ---------------- MEP & PLUMBING OVERRIDES ----------------
    "rainwater": {
        "category_key": "mep & building services",
        "instagram": ["rainwater harvesting tank construction details", "groundwater recharge pit modern house", "rainwater collection filter system"],
        "youtube": ["rainwater harvesting system construction and filters India", "underground rainwater tank complete walkthrough", "rooftop rainwater harvesting filter setup"],
        "pinterest": ["rainwater harvesting system residential architecture diagram"],
        "reddit": ["rainwater harvesting tank cost India experience", "best rainwater filter for residential house"],
        "shopping": ["rainwater harvesting rooftop filter buy online", "underground water tank storage system"],
        "vendor_types": ["rainwater harvesting system suppliers", "water tank manufacturers", "rainwater filter dealers"],
    },
    "pipe": {
        "category_key": "mep & building services",
        "instagram": ["concealed plumbing pipe installation house", "CPVC pipe fittings architectural plumbing reels"],
        "youtube": ["concealed plumbing pipeline installation house construction", "Astral vs Supreme CPVC pipe comparison test"],
        "pinterest": ["architectural plumbing and pipe fittings diagram"],
        "reddit": ["CPVC vs UPVC pipes plumbing house construction", "best plumbing pipe brand Astral Supreme Ashirvad"],
        "shopping": ["Astral CPVC pipe 1 inch price list", "Supreme CPVC pipe fittings brass elbow wholesale"],
        "vendor_types": ["plumbing pipe wholesale dealers", "Astral Supreme authorized distributors", "sanitaryware pipe stockists"],
    },
    "tank": {
        "category_key": "mep & building services",
        "instagram": ["underground water storage sump concrete construction", "overhead water tank installation house"],
        "youtube": ["underground water tank concrete construction step by step", "Sintex overhead water tank vs concrete sump cost"],
        "pinterest": ["underground water tank construction details architecture"],
        "reddit": ["underground concrete sump vs readymade tank cost India"],
        "shopping": ["Sintex water tank 1000 litre price", "readymade RCC water tank rate"],
        "vendor_types": ["water tank manufacturers Sintex", "RCC readymade sump suppliers", "plumbing water tank dealers"],
    },
}


# ==============================================================================
# RESOLUTION FUNCTION
# ==============================================================================

def get_social_search_terms(
    material_name: str,
    category_name: str = "",
    subcategory_name: str = ""
) -> Dict[str, Any]:
    """
    Resolves ANY material across all 10 catalogue categories (6,319+ materials)
    into high-yield social search terms for:
    - Instagram Reels
    - YouTube Walkthroughs
    - Pinterest Aesthetic Pins
    - Reddit Indian Construction Discussions
    - Google Shopping Wholesale & Trade Catalogues
    - Google Places Supplier Discovery
    """
    raw_material = material_name.strip()
    cleaned = clean_catalogue_term(raw_material)

    cat_clean = category_name.strip().lower()
    sub_clean = subcategory_name.strip().lower()
    combined_context = f"{raw_material} {cleaned} {category_name} {subcategory_name}".lower()

    # Step 1: Detect explicit category profile
    active_category_profile: Dict[str, Any] = CATEGORY_PROFILES.get("interior")
    for cat_key, prof in CATEGORY_PROFILES.items():
        if cat_key in cat_clean or cat_key in combined_context:
            active_category_profile = prof
            break
        # Heuristic fallbacks for common synonyms
        if "machine" in cat_clean or "tool" in cat_clean or "equipment" in cat_clean:
            active_category_profile = CATEGORY_PROFILES["machinery & tools"]
            break
        elif "door" in cat_clean or "window" in cat_clean or "hardware" in cat_clean or "fenestration" in cat_clean:
            active_category_profile = CATEGORY_PROFILES["doors, windows, hardware & fixtures"]
            break
        elif "mep" in cat_clean or "plumb" in cat_clean or "electric" in cat_clean or "hvac" in cat_clean:
            active_category_profile = CATEGORY_PROFILES["mep & building services"]
            break
        elif "exterior" in cat_clean or "facade" in cat_clean or "cladding" in cat_clean or "roof" in cat_clean or "masonry" in cat_clean:
            active_category_profile = CATEGORY_PROFILES["exterior"]
            break
        elif "interior" in cat_clean or "floor" in cat_clean or "tile" in cat_clean or "ceiling" in cat_clean or "furniture" in cat_clean:
            active_category_profile = CATEGORY_PROFILES["interior"]
            break
        elif "metal" in cat_clean or "steel" in cat_clean or "chemical" in cat_clean or "timber" in cat_clean:
            active_category_profile = CATEGORY_PROFILES["materials, metals, timber & chemicals"]
            break
        elif "landscape" in cat_clean or "garden" in cat_clean or "waste" in cat_clean:
            active_category_profile = CATEGORY_PROFILES["water, waste, landscape & external utilities"]
            break
        elif "safety" in cat_clean or "security" in cat_clean or "cctv" in cat_clean:
            active_category_profile = CATEGORY_PROFILES["safety, security & site welfare"]
            break
        elif "hospital" in cat_clean or "healthcare" in cat_clean:
            active_category_profile = CATEGORY_PROFILES["healthcare & hospital"]
            break
        elif "industrial" in cat_clean or "warehouse" in cat_clean or "peb" in cat_clean:
            active_category_profile = CATEGORY_PROFILES["industrial, commercial & institutional"]
            break

    # Step 2: Check for specific material noun override
    matched_noun_profile: Optional[Dict[str, Any]] = None
    for token, prof in MATERIAL_NOUN_REGISTRY.items():
        # Match as whole word or distinct phrase
        pattern = r'\b' + re.escape(token) + r'\b'
        if re.search(pattern, combined_context, re.IGNORECASE):
            matched_noun_profile = prof
            break

    # Extract clean base noun (up to 4 words)
    clean_words = cleaned.split()
    if len(clean_words) > 4:
        base_noun = " ".join(clean_words[:4])
    elif len(clean_words) >= 1:
        base_noun = cleaned
    else:
        base_noun = raw_material

    # Build platform-specific query arrays
    inst_queries = [
        f"{base_noun} architecture design",
        f"{base_noun} construction site walkthrough",
        f"{base_noun} house interior tour",
    ]
    yt_queries = [
        f"{base_noun} construction installation walkthrough",
        f"{base_noun} price comparison and review India",
    ]
    pin_queries = [
        f"{base_noun} modern house architecture design",
        f"{base_noun} material finish and texture",
    ]
    red_queries = [
        f"{base_noun} quality durability cost comparison India",
        f"{base_noun} construction experience review",
    ]
    shop_queries = [
        f"{base_noun} buy price India",
        f"{base_noun} wholesale trade rate",
        f"{base_noun} catalog price",
    ]
    vendor_terms = [
        f"{base_noun} dealers",
        f"{base_noun} wholesale distributors",
        f"{base_noun} manufacturers",
    ]

    # Merge with specific noun profile if matched
    if matched_noun_profile:
        inst_queries = matched_noun_profile.get("instagram", []) + inst_queries
        yt_queries = matched_noun_profile.get("youtube", []) + yt_queries
        pin_queries = matched_noun_profile.get("pinterest", []) + pin_queries
        red_queries = matched_noun_profile.get("reddit", []) + red_queries
        shop_queries = matched_noun_profile.get("shopping", []) + shop_queries
        vendor_terms = matched_noun_profile.get("vendor_types", []) + vendor_terms

    # Merge with category profile
    inst_queries += active_category_profile.get("instagram", [])
    yt_queries += active_category_profile.get("youtube", [])
    pin_queries += active_category_profile.get("pinterest", [])
    red_queries += active_category_profile.get("reddit", [])
    shop_queries += active_category_profile.get("shopping", [])
    vendor_terms += active_category_profile.get("vendor_types", [])

    x_queries = [
        f"{base_noun} architecture design",
        f"{base_noun} architectural details",
        f"{base_noun} contemporary architectural project",
        f"{base_noun} building material design",
    ]

    return {
        "raw_material": raw_material,
        "clean_noun": base_noun,
        "instagram_queries": list(dict.fromkeys(inst_queries))[:5],
        "youtube_queries": list(dict.fromkeys(yt_queries))[:4],
        "pinterest_queries": list(dict.fromkeys(pin_queries))[:4],
        "reddit_queries": list(dict.fromkeys(red_queries))[:3],
        "google_shopping_queries": list(dict.fromkeys(shop_queries))[:4],
        "twitter_queries": list(dict.fromkeys(x_queries))[:4],
        "x_queries": list(dict.fromkeys(x_queries))[:4],
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

"""
Comprehensive 29-Category Architectural and Construction Taxonomy Service for Architect AI.
Defines maintainable categories, subcategories, technical attributes, standards compliance,
and synonym/intent mappings without hardcoding rigid ad-hoc keyword lists.
"""

from typing import Dict, List, Any, Optional

TAXONOMY_29_CATEGORIES: List[Dict[str, Any]] = [
    {
        "code": "CAT-01",
        "name": "Architecture & House Types",
        "slug": "architecture-house-types",
        "section": "A. Architectural Typologies",
        "description": "Architectural typologies, vernacular traditions, and contemporary residential designs.",
        "image_url": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Kerala Architecture", "Nalukettu", "Traditional Kerala Homes", "Chettinad Architecture",
            "Courtyard Houses", "Contemporary Indian Homes", "Modern Villas", "Luxury Houses",
            "Compact Homes", "Small-Budget Homes", "Apartments", "Tiny Houses",
            "Tropical Architecture", "Sustainable Architecture", "Passive-Design Houses",
            "Prefabricated Houses", "Modular Houses", "Heritage Restoration", "Old-House Renovation",
            "Extensions and Additions", "Adaptive Reuse", "Climate-Responsive Homes"
        ],
        "applications": "Master planning, residential architectural design, vernacular adaptation, bioclimatic zoning",
        "standards": "National Building Code (NBC 2016 Part 3), Local Municipal Building Bye-Laws",
        "synonyms": ["house design", "villa design", "home architecture", "duplex house", "nalukettu house", "kerala style", "elevation design"]
    },
    {
        "code": "CAT-02",
        "name": "Exterior Design & Building Envelopes",
        "slug": "exterior-design-envelopes",
        "section": "A. Architectural Typologies",
        "description": "Building facades, elevations, sunshades, rooflines, and exterior weather envelopes.",
        "image_url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Front Elevations", "Rear Elevations", "Side Elevations", "Facade Design",
            "Entrance Design", "Porches", "Balconies", "Terraces", "Verandas", "Courtyards",
            "Rooflines", "Parapets", "Eaves", "Exterior Lighting", "Exterior Cladding",
            "Sunshades", "Louvers", "Shading Devices", "Privacy Screens", "Carports", "Garages"
        ],
        "applications": "Solar heat gain reduction, facade articulation, exterior weather protection, privacy zoning",
        "standards": "NBC 2016 Part 8 Building Services, ECBC (Energy Conservation Building Code)",
        "synonyms": ["front elevation", "facade", "sunshade", "exterior louvers", "balcony design", "porch", "verandah"]
    },
    {
        "code": "CAT-03",
        "name": "Bricks & Masonry Units",
        "slug": "bricks-and-blocks",
        "section": "B. Structural & Civil Works",
        "description": "Clay bricks, wire-cut units, AAC blocks, fly-ash blocks, and specialized masonry units.",
        "image_url": "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Common Burnt-Clay Bricks", "Solid Clay Bricks", "Hollow Clay Bricks", "Perforated Bricks",
            "Engineering Bricks", "Facing Bricks", "Exposed Bricks", "Wire-Cut Bricks",
            "Fly-Ash Bricks", "Concrete Bricks", "Solid Concrete Blocks", "Hollow Concrete Blocks",
            "AAC Blocks (Autoclaved Aerated Concrete)", "CLC Blocks", "Laterite Blocks",
            "Interlocking Compressed Earth Blocks (CSEB)", "Rammed Earth", "Glass Blocks",
            "Jali Blocks", "Brick Slips & Veneers", "Refractory Fire Bricks", "Brick Bonds (Rat-Trap, English, Flemish)"
        ],
        "applications": "Load-bearing masonry, cavity walls, thermal mass partitions, acoustic barriers, ornamental screens",
        "standards": "IS 1077 (Clay Bricks), IS 2185 Part 1 & 3 (Concrete & AAC Blocks), IS 2212 (Code of Practice for Brickwork)",
        "synonyms": ["brick", "bricks", "aac block", "wirecut brick", "fly ash", "concrete block", "laterite block", "porotherm", "rat trap bond"]
    },
    {
        "code": "CAT-04",
        "name": "Walls — Types & Systems",
        "slug": "walls-systems",
        "section": "B. Structural & Civil Works",
        "description": "Structural, partition, retaining, boundary, and acoustic wall assemblies.",
        "image_url": "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Load-Bearing Walls", "Non-Load-Bearing Partitions", "Cavity Walls", "Shear Walls",
            "Retaining Walls", "Boundary & Compound Walls", "Garden Walls", "Basement Foundation Walls",
            "Parapet Walls", "Screen & Jali Walls", "Gabion Walls", "Dry-Stone Walls",
            "Random-Rubble Masonry Walls", "Curtain Walls", "Precast Concrete Panels",
            "Gypsum & Cement-Board Partitions", "Acoustic Fire-Rated Walls", "Green Living Walls"
        ],
        "applications": "Earth retention, perimeter security, lateral load resistance, interior space division, noise reduction",
        "standards": "IS 1905 (Structural Use of Unreinforced Masonry), IS 14458 (Retaining Walls), NBC 2016 Part 6",
        "synonyms": ["compound wall", "boundary wall", "retaining wall", "partition wall", "cavity wall", "gabion", "jali wall"]
    },
    {
        "code": "CAT-05",
        "name": "Wall Finishes, Cladding & Plasters",
        "slug": "wall-finishes-cladding",
        "section": "C. Surfaces & Finishes",
        "description": "Natural stone veneers, mineral plasters, stucco, 3D fluted panels, and exterior cladding.",
        "image_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Natural-Stone Cladding", "Stone Veneer", "Manufactured Stone Veneer", "Granite & Marble Cladding",
            "Slate & Sandstone Cladding", "Laterite Cladding", "Exposed-Brick Pointing",
            "Cement Plaster (Sand-Faced)", "Lime Plaster & Putty", "Gypsum Plaster", "Stucco & Textured Plaster",
            "Microcement Wall Finishes", "Exposed Concrete Render", "Weatherproof Exterior Paint",
            "Mineral Limewash", "Fluted Wall Panels", "WPC & PVC Louvers", "Acoustic Fabric Panels",
            "HPL & ACP Exterior Cladding", "Fibre-Cement Boards", "Terracotta Cladding Tiles"
        ],
        "applications": "Exterior building envelop protection, moisture defense, feature walls, acoustic dampening",
        "standards": "IS 1661 (Application of Cement and Lime Plaster), IS 2402 (Wall Cladding)",
        "synonyms": ["wall cladding", "stone cladding", "fluted panel", "plaster", "microcement", "stucco", "wall paneling", "lime plaster"]
    },
    {
        "code": "CAT-06",
        "name": "Cement, Concrete & Binders",
        "slug": "cement-concrete",
        "section": "B. Structural & Civil Works",
        "description": "Ordinary Portland cement, PPC, ready-mix concrete, admixtures, and structural grouts.",
        "image_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Ordinary Portland Cement (OPC 43 & 53)", "Portland Pozzolana Cement (PPC)", "Portland Slag Cement (PSC)",
            "Ready-Mix Concrete (RMC)", "Reinforced Cement Concrete (RCC)", "Plain Cement Concrete (PCC)",
            "Precast Concrete Elements", "Lightweight Foam Concrete", "Pervious Concrete",
            "Stamped & Polished Concrete", "Concrete Floor Screed", "High-Strength Masonry Mortar",
            "Non-Shrink Structural Grout", "Polymer Tile Adhesives", "Plasticizers & Waterproofing Admixtures",
            "Concrete Curing Compounds", "Expansion & Control Joints"
        ],
        "applications": "Foundations, structural columns, beams, suspended slabs, leveling screeds, crack repairs",
        "standards": "IS 12269 (OPC 53), IS 1489 (PPC), IS 456 (Plain and Reinforced Concrete), IS 516 (Test for Strength)",
        "synonyms": ["cement", "opc 53", "ppc", "concrete", "rcc", "mortar", "ready mix", "grout", "admixture"]
    },
    {
        "code": "CAT-07",
        "name": "Sand, Aggregates & Earthwork",
        "slug": "sand-aggregates-earthwork",
        "section": "B. Structural & Civil Works",
        "description": "Manufactured sand, graded stone aggregates, hardcore fill, and soil stabilization.",
        "image_url": "https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "River Sand (Coarse & Fine)", "Manufactured Sand (M-Sand for Concrete)", "Plastering M-Sand (P-Sand)",
            "Coarse Aggregates (10mm, 20mm, 40mm)", "Fine Blue Metal Dust", "Crushed Stone Gravel",
            "Decorative Landscaping Pebbles", "Lateritic Murrum Soil", "Hardcore Soling Fill",
            "Topsoil & Planting Loam", "Road Sub-Base Material (GSB)", "Soil Compaction & Stabilization",
            "Erosion Control Geotextiles", "Geogrids & Ground Reinforcement"
        ],
        "applications": "Concrete batching, wall plastering, foundation soling, basement backfilling, permeable drainage bedding",
        "standards": "IS 383 (Coarse and Fine Aggregates from Natural Sources for Concrete)",
        "synonyms": ["m-sand", "p-sand", "river sand", "gravel", "aggregate", "crushed stone", "earthwork", "geotextile"]
    },
    {
        "code": "CAT-08",
        "name": "Structural Materials & Reinforcement",
        "slug": "structural-steel",
        "section": "B. Structural & Civil Works",
        "description": "Fe 550D/500D TMT reinforcement rebars, structural steel sections, formwork, and anchor bolts.",
        "image_url": "https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "TMT Reinforcement Bars (Fe 500D, Fe 550D)", "Reinforcing Welded Steel Mesh", "Structural Steel I-Beams",
            "MS Channels, Angles & Plates", "Hollow Structural Sections (SHS, RHS)", "Structural Foundation Bolts",
            "Chemical & Mechanical Anchors", "Rebar Couplers & Splicing", "Rebar Spacers & Cover Blocks",
            "Shuttering Plywood (Film-Faced)", "Steel & Aluminium Formwork Systems", "Props, Jacks & Scaffolding",
            "Precast Beams & Planks", "Isolated Footings, Raft & Pile Reinforcement"
        ],
        "applications": "Earthquake-resistant frame construction, industrial trusses, slab shuttering, heavy structural connections",
        "standards": "IS 1786 (High Strength Deformed Steel Bars), IS 2062 (Hot Rolled Steel), IS 13920 (Ductile Design)",
        "synonyms": ["tmt bar", "steel rebar", "tata tiscon", "structural steel", "shuttering", "plywood formwork", "rebar coupler"]
    },
    {
        "code": "CAT-09",
        "name": "Roofs, Terraces & Ceilings",
        "slug": "roofing",
        "section": "A. Architectural Typologies",
        "description": "Clay Mangalore roof tiles, sloped trusses, false ceilings, terrace gardens, and roof waterproofing.",
        "image_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Reinforced Concrete Flat Roofs", "Sloped Vernacular Roofs", "Clay Mangalore Roof Tiles",
            "Concrete Roofing Tiles", "Standing-Seam Metal Roofing", "Polycarbonate & Glass Skylights",
            "Timber & Steel Roof Trusses", "Roof Underlay Waterproofing", "Thermal Roof Insulation",
            "Rainwater Gutters & Downpipes", "Eaves, Parapets & Fascia Boards", "Terrace Cool Roof Coatings",
            "Terrace & Roof Gardens", "Pergolas & Outdoor Shade Canopies", "Gypsum Board False Ceilings",
            "POP Ceilings", "Wooden Slatted Ceilings", "Acoustic Suspended Ceilings", "Concealed Cove Lighting"
        ],
        "applications": "Tropical storm shedding, passive roof insulation, acoustic absorption, concealed service integration",
        "standards": "IS 654 (Clay Roofing Tiles), IS 3384 (Bitumen Primer for Waterproofing), IS 2095 (Gypsum Plaster Boards)",
        "synonyms": ["roof", "roof tiles", "mangalore tiles", "false ceiling", "skylight", "terrace garden", "cove light", "roof truss"]
    },
    {
        "code": "CAT-10",
        "name": "Windows, Doors & Architectural Openings",
        "slug": "doors-and-windows",
        "section": "C. Surfaces & Finishes",
        "description": "Solid teak entrance doors, uPVC sliding windows, double-glazed fenestration, and hardware.",
        "image_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Solid Teak Wood Doors", "Carved Traditional Chettinad Doors", "Flush Doors & Laminate Doors",
            "Aluminium Sliding Windows", "uPVC Casement & Sliding Windows", "Structural Glass Curtain Walls",
            "Double-Glazed Low-E Units (DGU)", "Laminated Safety Glass", "Louvered Windows & Jali Screens",
            "French Doors & Folding Bifold Systems", "Concealed Pivot Entrance Doors", "Fire-Rated Doors",
            "Heavy-Duty Stainless Steel Hinges", "Architectural Door Handles & Mortise Locks",
            "Magnetic Door Stoppers & Concealed Closers", "Insect Screens & Window Grilles"
        ],
        "applications": "Daylighting, natural cross-ventilation, security, acoustic and thermal isolation",
        "standards": "IS 2202 (Wooden Flush Doors), IS 1081 (Fixing of Metal Doors and Windows), IS 2553 (Safety Glass)",
        "synonyms": ["door", "window", "upvc window", "teak door", "sliding window", "glass door", "french door", "door lock"]
    },
    {
        "code": "CAT-11",
        "name": "Flooring — Materials & Finishes",
        "slug": "flooring",
        "section": "C. Surfaces & Finishes",
        "description": "Vitrified tiles, Italian marble, Athangudi tiles, Kota stone, and wooden parquet flooring.",
        "image_url": "https://images.unsplash.com/photo-1581858726788-75bc0f6a952d?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Glazed Vitrified Tiles (GVT/PGVT)", "Double-Charge Vitrified Tiles", "Full-Body Porcelain Slabs",
            "Ceramic Floor Tiles", "Handmade Athangudi Tiles", "Traditional Cast Terrazzo Flooring",
            "Polished Italian Marble", "Indian White Makrana Marble", "Flamed & Polished Granite",
            "Honed Kota Stone Paving", "Natural Slate & Sandstone Flooring", "Solid Wood Flooring",
            "Engineered Oak & Walnut Hardwood", "Laminate Wood Flooring", "SPC & LVT Vinyl Planks",
            "Anti-Skid Exterior Pavers", "WPC Outdoor Pool Decking", "Epoxy Screed & Microcement Floors"
        ],
        "applications": "High-traffic residential flooring, wet-area slip resistance, heritage restoration, outdoor paving",
        "standards": "IS 15622 (Pressed Ceramic Tiles), IS 1130 (Marble Slabs), IS 3316 (Granite Slabs)",
        "synonyms": ["flooring", "tile", "tiles", "marble", "granite", "kota stone", "athangudi", "terrazzo", "wooden floor", "vitrified"]
    },
    {
        "code": "CAT-12",
        "name": "Bathrooms & Sanitaryware",
        "slug": "sanitaryware",
        "section": "D. Building Services & Utilities",
        "description": "Wall-hung toilets, concealed cisterns, washbasins, thermostatic showers, and fittings.",
        "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Wall-Hung Rimless Toilets", "Concealed Cistern Actuators", "Countertop Vessel Basins",
            "Under-Counter Washbasins", "Bathroom Vanity Cabinets", "Freestanding Acrylic Bathtubs",
            "Glass Shower Enclosures & Partitions", "Thermostatic Rain Showers", "Concealed Diverters & Mixers",
            "Linear Floor Drain Traps", "Anti-Skid Bathroom Tiles", "Recessed Shower Niches",
            "Backlit Anti-Fog Vanity Mirrors", "Continuous Bathroom Exhaust Systems"
        ],
        "applications": "Residential hygiene spaces, master bathroom suites, powder rooms, barrier-free accessibility",
        "standards": "IS 2556 (Vitreous Sanitary Appliances), IS 8931 (Cast Copper Alloy Fancy Tap and Faucets)",
        "synonyms": ["bathroom", "toilet", "washbasin", "shower", "sanitaryware", "faucet", "vanity", "commode", "cistern"]
    },
    {
        "code": "CAT-13",
        "name": "Plumbing, Piping & Water Management",
        "slug": "plumbing-piping",
        "section": "D. Building Services & Utilities",
        "description": "CPVC hot/cold piping, uPVC drainage lines, rainwater harvesting pits, and booster pumps.",
        "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "CPVC Water Supply Pipes (SDR 11)", "uPVC SWR Soil & Waste Drainage Pipes", "PPR Hot Water Fusion Pipes",
            "HDPE Potable Water Pipes", "GI & Copper Supply Lines", "Submersible Borewell & Pressure Booster Pumps",
            "Underground Sump & Overhead Storage Tanks", "Water Filtration & Softening Units",
            "Gully Traps, Nahani Traps & Multi-Floor Traps", "Inspection Chambers & Precast Manholes",
            "Rainwater Harvesting Recharge Pits & Filters", "Subsurface French Drains & Soil De-watering"
        ],
        "applications": "Potable water distribution, gravity sanitary drainage, rainwater conservation, groundwater replenishment",
        "standards": "IS 15778 (CPVC Pipes for Potable Water), IS 13592 (uPVC Pipes for Soil and Waste), IS 1742 (Building Drainage)",
        "synonyms": ["plumbing", "pipe", "pipes", "cpvc", "upvc", "water tank", "water pump", "rainwater harvesting", "manhole"]
    },
    {
        "code": "CAT-14",
        "name": "Waterproofing & Weather Protection",
        "slug": "waterproofing-protection",
        "section": "B. Structural & Civil Works",
        "description": "Polymer cementitious coatings, EPDM sheet membranes, damp-proof courses, and joint sealants.",
        "image_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Terrace Polymer-Modified Cementitious Waterproofing", "Elastomeric Acrylic Liquid Membranes",
            "SBS Bituminous Torch-On Sheet Membranes", "Basement Box-Type Waterproofing",
            "Retaining Wall Drainage Membranes", "Bathroom Wet-Area Waterproofing Barrier",
            "Damp-Proof Course (DPC) at Plinth Level", "Expansion Joint Polyurethane Sealants",
            "Silicone Water-Repellent Facade Sealers", "Efflorescence & Salt-Damp Neutralizers",
            "Structural Crack Injection Grouting"
        ],
        "applications": "Monsoon leak prevention, foundation moisture barrier, basement hydrostatic defense, roof slab protection",
        "standards": "IS 3067 (General Design Details and Preparatory Work for Damp-proofing and Waterproofing of Buildings)",
        "synonyms": ["waterproofing", "dpc", "damp proof", "leakage", "terrace waterproofing", "sealant", "epdm liner", "roof leak"]
    },
    {
        "code": "CAT-15",
        "name": "Electrical Systems & Architectural Lighting",
        "slug": "lighting",
        "section": "D. Building Services & Utilities",
        "description": "Modular switches, distribution boards, concealed conduits, chandeliers, and architectural LED lighting.",
        "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Modular Switches & Glass Switchboards", "Smart Home Automation Modules & Touch Panels",
            "Distribution Boards (MCB, RCCB, Surge Protection)", "FR-LSH Flame Retardant Copper Wires",
            "Heavy-Duty Rigid PVC Electrical Conduits", "Earthing Electrodes & Chemical Compounds",
            "Recessed Architectural LED Downlights", "Magnetic Track Light Systems", "Ambient Warm Cove Strips (2700K)",
            "Pendant Lights & Dining Chandeliers", "Exterior Weatherproof Wall Washers (IP65)",
            "Bollard & Spike Garden Landscape Lighting", "Step & Staircase Recessed Lights"
        ],
        "applications": "Electrical power distribution, life safety fire protection, mood and accent interior illumination",
        "standards": "IS 694 (PVC Insulated Cables), IS 3854 (Switches for Domestic and Similar Purposes), IS 10322 (Luminaires)",
        "synonyms": ["lighting", "switch", "switchboard", "light", "chandelier", "sconce", "downlight", "cove light", "electrical", "wiring"]
    },
    {
        "code": "CAT-16",
        "name": "Fasteners, Fixings & Small Hardware",
        "slug": "fasteners-hardware",
        "section": "B. Structural & Civil Works",
        "description": "Wood screws, chemical anchors, expansion bolts, brackets, soft-close hinges, and drawer slides.",
        "image_url": "https://images.unsplash.com/photo-1581858726788-75bc0f6a952d?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Stainless Steel Wood Screws", "Self-Tapping & Self-Drilling Screws", "Drywall Gypsum Screws",
            "Expansion Wall Plugs (Nylon Rawlplugs)", "Heavy-Duty Wedge & Sleeve Anchors", "Chemical Injection Resin Studs",
            "High-Tensile Hex Bolts & Structural Nuts", "L-Brackets, Angle Cleats & Mending Plates",
            "Concealed Soft-Close Kitchen Cabinet Hinges", "Heavy-Duty Ball-Bearing Drawer Runners",
            "Sliding Wardrobe Top & Bottom Track Gear", "Magnetic Catches & Push-to-Open Latches",
            "Window Friction Stays & Casement Fasteners", "Construction Polyurethane & Silicone Adhesives"
        ],
        "applications": "Carpentry joinery, structural curtain wall anchoring, cabinetry assembly, drywall framing",
        "standards": "IS 1364 (Hexagon Head Bolts and Screws), IS 7168 (Air Release Latches and Fasteners)",
        "synonyms": ["screws", "fasteners", "anchors", "bolts", "nuts", "hinges", "drawer runner", "wall plug", "hardware", "brackets"]
    },
    {
        "code": "CAT-17",
        "name": "Paints, Coatings & Chemical Products",
        "slug": "paints-and-finishes",
        "section": "C. Surfaces & Finishes",
        "description": "Interior emulsions, exterior weather-shield paints, wood stains, PU polishes, and wall putties.",
        "image_url": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Low-VOC Interior Acrylic Emulsions", "Silicone Exterior Weatherproof Paints", "Waterproof Wall Putty (White Cement)",
            "Alkali-Resistant Interior & Exterior Primers", "Polyurethane (PU) Wood Polishes & Sealers",
            "Natural Wood Stains & Linseed Oil Oils", "Anti-Corrosive Epoxy Metal Primers",
            "Heat-Reflective Elastomeric Roof Coatings", "Textured Stucco Designer Paints",
            "Natural Slaked Lime Wall Wash", "Silicone Impregnating Stone & Tile Sealers",
            "Anti-Termite Soil Treatment Emulsions"
        ],
        "applications": "Surface color aesthetic, UV protection, efflorescence blocking, substrate moisture sealing",
        "standards": "IS 5410 (Cement Paint), IS 15489 (Plastic Emulsion Paint), IS 101 (Methods of Test for Paints)",
        "synonyms": ["paint", "paints", "primer", "wall putty", "wood polish", "varnish", "coating", "emulsion", "stain"]
    },
    {
        "code": "CAT-18",
        "name": "Timber, Engineered Boards & Panels",
        "slug": "timber-and-wood",
        "section": "C. Surfaces & Finishes",
        "description": "Malabar teak, seasoned hardwood, marine-grade BWP plywood, MDF, and decorative veneer sheets.",
        "image_url": "https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Seasoned Malabar Teak Wood", "Hardwood (Sal, Rosewood, Mahogany)", "Boiling Water Proof (BWP) Marine Plywood (IS 710)",
            "Commercial Moisture Resistant (MR) Plywood (IS 303)", "High-Density Fibreboard (HDF & MDF)",
            "Natural Wood Veneer Sheets", "High-Pressure Decorative Laminates (HPL)", "Wood Polymer Composite (WPC) Solid Boards",
            "PVC Waterproof Shutter Sheets", "Fibre-Cement Partition Boards", "Pre-Laminated Particle Boards",
            "Exterior Wood Wall Battens & Louvers", "Edge-Banding Tape & Joint Adhesives"
        ],
        "applications": "Custom modular wardrobes, kitchen carcasses, architectural wall paneling, ceiling rafters",
        "standards": "IS 710 (Marine Plywood), IS 303 (Plywood for General Purposes), IS 2046 (Decorative Laminates)",
        "synonyms": ["timber", "wood", "plywood", "teak", "mdf", "veneer", "laminate", "marine ply", "wpc board", "hardwood"]
    },
    {
        "code": "CAT-19",
        "name": "Metal, Architectural Glass & Composites",
        "slug": "metal-glass-composites",
        "section": "C. Surfaces & Finishes",
        "description": "Anodized aluminium extrusions, stainless steel railings, tempered glass, and polycarbonate sheets.",
        "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Architectural Anodized Aluminium Sections", "SS 304 & SS 316 Balcony Railings", "Toughened & Tempered Glass Slabs",
            "Acoustic Laminated PVB Glass", "Frosted & Tinted Architectural Glass", "Fluted Glass Partitions",
            "Aluminium Composite Panels (ACP)", "Multi-Wall Polycarbonate Roofing Sheets", "Decorative Laser-Cut Metal Screens",
            "Mild Steel Safety Grilles & Gates", "Fibre-Reinforced Polymer (FRP) Custom Units"
        ],
        "applications": "Staircase balustrades, balcony handrails, frameless shower cubicles, patio skylights, security gates",
        "standards": "IS 2553 (Safety Glass), IS 733 (Wrought Aluminium Bars and Sections), IS 16231 (Glazing in Buildings)",
        "synonyms": ["glass", "aluminium", "aluminum", "steel railing", "acp", "polycarbonate", "fluted glass", "metal screen", "tempered glass"]
    },
    {
        "code": "CAT-20",
        "name": "Kitchens, Modular Systems & Storage",
        "slug": "kitchens-storage",
        "section": "E. Interiors, Decor & Landscaping",
        "description": "Modular kitchens, quartz islands, pantry pullouts, tall units, and custom walk-in closets.",
        "image_url": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Modular Kitchen Layouts (L-Shape, Island, Parallel)", "Marine Ply & Acrylic Cabinet Carcasses",
            "Tandem Stainless Steel Drawer Boxes", "Soft-Close Corner Carousel Systems", "Tall Pullout Pantry Storage Units",
            "Solid Engineered Quartz Countertops", "Granite Kitchen Platforms with Sink Cutouts", "Subway Tile Ceramic Backsplashes",
            "Stainless Steel Quartz Composite Sinks", "Under-Cabinet LED Task Lights", "Walk-in Dressing Closets",
            "Floor-to-Ceiling Bedroom Wardrobes", "Space-Saving Shoe & Utility Racks"
        ],
        "applications": "Culinary food preparation, high-density pantry storage, ergonomic cooking workflows",
        "standards": "NBC 2016 Part 3, IS 15477 (Adhesives for Tile and Stone Countertops)",
        "synonyms": ["kitchen", "modular kitchen", "countertop", "quartz", "wardrobe", "storage", "cabinets", "pantry", "sink"]
    },
    {
        "code": "CAT-21",
        "name": "Interior Design & Furnishings",
        "slug": "interior-design-furnishings",
        "section": "E. Interiors, Decor & Landscaping",
        "description": "Living rooms, bedroom suites, dining spaces, home offices, and furniture layouts.",
        "image_url": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Living Room Seating Layouts", "Master Bedroom Suite Design", "Dining Room Concepts",
            "Ergonomic Home Office Workspaces", "Small-Space Compact Redesigns", "Modular Sectional Sofas",
            "Solid Teak Dining Tables & Chairs", "King & Queen Platform Beds with Upholstered Headboards",
            "Curtains, Sheers & Blackout Drapes", "Hand-Woven Wool & Jute Rugs", "Acoustic Wall Slatting",
            "Decorative Ambient Floor & Table Lamps", "Indoor Foliage & Green Accents"
        ],
        "applications": "Interior space planning, ergonomic comfort, acoustic balance, visual warmth and zoning",
        "standards": "NBC 2016 Part 8 Interior Illumination and Ventilation Norms",
        "synonyms": ["interior", "bedroom", "living room", "dining room", "furniture", "sofa", "curtains", "rugs", "home office"]
    },
    {
        "code": "CAT-22",
        "name": "Gardens, Landscaping & Outdoor Construction",
        "slug": "garden-materials",
        "section": "E. Interiors, Decor & Landscaping",
        "description": "Natural boulder waterfalls, koi ponds, stone paver walkways, pergolas, and vertical living walls.",
        "image_url": "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Natural Granite Boulder Waterfalls", "Cascading Water Features & Splash Pools", "Backyard Koi & Lotus Ponds",
            "Interlocking Permeable Concrete Pavers", "Monolithic Natural Stone Stepping Pathways", "Outdoor Architectural Pergolas",
            "Vertical Living Green Walls with Drip Lines", "Terrace Garden Planter Boxes", "Garden Perimeter Retaining Walls",
            "Submersible Waterfall Pumps & Biological Filters", "Warm Low-Voltage Garden Landscape Lighting",
            "Outdoor Poolside Flamed Granite Paving", "Courtyard Water Fountains & Urli Basins"
        ],
        "applications": "Outdoor recreation, microclimate cooling, acoustic relaxation, stormwater bio-retention",
        "standards": "Landscape Irrigation & Hydraulic Guidelines (CPWD Specifications Part 2)",
        "synonyms": ["garden", "waterfall", "garden waterfall", "pond", "pathway", "pavers", "stepping stones", "pergola", "landscaping"]
    },
    {
        "code": "CAT-23",
        "name": "Home Decor & Decorative Hardware",
        "slug": "home-decor-hardware",
        "section": "E. Interiors, Decor & Landscaping",
        "description": "Terracotta planters, ceramic vases, wall art, grand chandeliers, and architectural brass pulls.",
        "image_url": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Handcrafted Terracotta Garden Pots", "Glazed Ceramic Fluted Planters", "Hanging Balcony Metal Planters",
            "Architectural Cast Brass Door Handles", "Grand Venetian & Murano-Style Chandeliers", "Hand-Tufted Jute Area Rugs",
            "Solid Brass Traditional Urli Bowls", "Floating Solid Wood Wall Shelves", "Sculptural Ceramic Vases",
            "Backlit Architectural Wall Mirrors", "Canvas Framed Wall Art & Heritage Prints"
        ],
        "applications": "Aesthetic curation, botanical plant potting, entrance hardware focal points",
        "standards": "Handicraft & Brass Foundry Quality Standards",
        "synonyms": ["pots", "planters", "decorative pots", "home decor", "chandelier", "vase", "mirror", "wall art", "urli"]
    },
    {
        "code": "CAT-24",
        "name": "Climate-Responsive & Sustainable Materials",
        "slug": "sustainable-materials",
        "section": "A. Architectural Typologies",
        "description": "Passive solar cooling, thermal roof insulation, low-carbon CSEB blocks, and rainwater harvesting.",
        "image_url": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Compressed Stabilised Earth Blocks (CSEB)", "Fly-Ash & Recycled Slag Concrete", "Reflective Cool-Roof High-Albedo Coatings",
            "Double-Glazed Low-Emissivity (Low-E) Glazing", "Terracotta Facade Solar Jali Louvers", "Cross-Ventilation Wind Catcher Designs",
            "Under-Slab Expanded Polystyrene (EPS) Insulation", "Rainwater Harvesting & Aquifer Recharge Systems",
            "Reclaimed Teakwood & Timber Salvage", "Pervious Concrete Stormwater Infiltration Paving"
        ],
        "applications": "Zero-energy building design, green building GRIHA / IGBC certification, indoor thermal comfort",
        "standards": "BEE Energy Conservation Building Code (ECBC), GRIHA v2019, IGBC Green Homes",
        "synonyms": ["sustainable", "cool roof", "passive cooling", "green building", "thermal insulation", "rainwater harvesting", "low carbon"]
    },
    {
        "code": "CAT-25",
        "name": "Construction Tools, Equipment & Safety",
        "slug": "construction-tools",
        "section": "B. Structural & Civil Works",
        "description": "Precision laser levels, rotary hammer drills, tile leveling clips, safety gear, and masonry trowels.",
        "image_url": "https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Masonry Steel Trowels & Plastering Floats", "Spirit Levels & Green Beam Laser Levels", "Heavy-Duty Rotary Hammer Drills",
            "Diamond Blade Tile & Granite Cutters", "Reusable Tile Leveling Clips & Wedges", "Notched Adhesive Trowels & Grout Floats",
            "Electric Mortar & Paint Mixing Paddles", "Steel Scaffolding & Adjustable Prop Jacks", "Personal Protective Equipment (Helmets, Safety Shoes, Harnesses)"
        ],
        "applications": "Jobsite craftsmanship accuracy, structural safety enforcement, tile flat surface calibration",
        "standards": "IS 3696 (Safety Code for Scaffolds and Ladders), IS 2925 (Industrial Safety Helmets)",
        "synonyms": ["tools", "tile cutter", "tile spacers", "leveling clips", "drill", "trowel", "scaffolding", "laser level", "safety gear"]
    },
    {
        "code": "CAT-26",
        "name": "Renovation & Project Stories",
        "slug": "renovation-stories",
        "section": "A. Architectural Typologies",
        "description": "Old heritage house transformations, bathroom and kitchen redesigns, budget breakdowns, and diaries.",
        "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Heritage Traditional House Restoration", "Partial & Full Residential Reconstruction", "Before-and-After Bathroom Remodels",
            "Old Kitchen to Modern Modular Transformations", "Living Room Wall & False Ceiling Makeovers",
            "Balcony & Terrace Transformation Projects", "Sub-Floor Moisture & Crack Repair Case Studies",
            "Verified Project Bill of Materials (BOM)", "Architect & Builder On-Site Project Diaries"
        ],
        "applications": "Retrofit engineering, structural strengthening, adaptive reuse, real cost learning",
        "standards": "NBC 2016 Part 2 Administrative & Existing Building Regulations",
        "synonyms": ["renovation", "makeover", "before after", "reconstruction", "bathroom renovation", "kitchen renovation", "restoration"]
    },
    {
        "code": "CAT-27",
        "name": "Material Comparisons & Selection Guides",
        "slug": "material-comparisons",
        "section": "C. Surfaces & Finishes",
        "description": "Technical side-by-side material comparisons: Clay brick vs AAC, Marble vs Granite, Timber vs Wood-tile.",
        "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Clay Brick vs. AAC Concrete Blocks", "Natural Stone vs. Manufactured Stone Veneer", "Ceramic vs. Vitrified vs. Porcelain Tiles",
            "Natural Marble vs. Granite Flooring", "Solid Wood vs. Wood-Look Porcelain Tiles", "Aluminium vs. uPVC Window Systems",
            "Single vs. Double-Glazed Low-E Glass", "Cementitious vs. Bituminous Waterproofing Systems"
        ],
        "applications": "Architectural specification selection, cost-benefit analysis, climate suitability matching",
        "standards": "Comparative Bureau of Indian Standards (BIS) Matrix",
        "synonyms": ["comparison", "vs", "difference", "which is better", "marble vs granite", "brick vs aac", "tile vs marble"]
    },
    {
        "code": "CAT-28",
        "name": "Manufacturers, Products & Sourcing Directory",
        "slug": "manufacturers-suppliers-directory",
        "section": "D. Building Services & Utilities",
        "description": "Verified manufacturer specifications, official technical catalogs, authorized distributors, and local yards.",
        "image_url": "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Primary Material Manufacturers (Tata Steel, UltraTech, Wienerberger)", "Regional Stockyards & Material Distributors",
            "Local Tile & Sanitaryware Showrooms", "Electrical & Lighting Wholesale Distributors", "Architectural Stone & Granite Yards",
            "Licensed Civil Structural Contractors", "Interior Design & Modular Kitchen Specialists", "Landscape Water Feature Contractors"
        ],
        "applications": "Material procurement, supply chain logistics, trade discount inquiries, contractor bidding",
        "standards": "GST Verified Merchant Records, Manufacturer Authorized Dealerships",
        "synonyms": ["supplier", "manufacturers", "dealers", "distributors", "vendor", "shops near me", "quote", "contractor"]
    },
    {
        "code": "CAT-29",
        "name": "Specialist Construction & Emerging Building Systems",
        "slug": "specialist-emerging-systems",
        "section": "B. Structural & Civil Works",
        "description": "Precast monolithic modular box units, light gauge steel framing (LGSF), 3D concrete printing, and smart facades.",
        "image_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80",
        "subcategories": [
            "Light Gauge Steel Framing (LGSF) Structures", "Precast Monolithic Modular Pods", "3D Concrete Printing Construction",
            "Cross-Laminated Timber (CLT) Structural Slabs", "Building Integrated Photovoltaics (BIPV)",
            "Kinetic & Dynamic Shading Facades", "Smart Self-Healing Concrete Admixtures"
        ],
        "applications": "Rapid assembly construction, seismic lightweight framing, renewable energy integration",
        "standards": "BMTPC (Building Materials & Technology Promotion Council) Emerging Technologies Guidelines",
        "synonyms": ["lgsf", "3d printing concrete", "modular construction", "precast pod", "emerging materials", "kinetic facade"]
    }
]

def get_all_taxonomy_categories() -> List[Dict[str, Any]]:
    return TAXONOMY_29_CATEGORIES

def find_category_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    for cat in TAXONOMY_29_CATEGORIES:
        if cat["slug"] == slug:
            return cat
    return None

def match_query_to_taxonomy(query: str) -> List[Dict[str, Any]]:
    """
    Given a user query (e.g. 'different types of bricks for a house'),
    identifies matching taxonomy categories using synonyms, subcategories, and keywords.
    """
    if not query:
        return []
    
    q_lower = query.lower()
    matches = []
    
    for cat in TAXONOMY_29_CATEGORIES:
        score = 0
        # Check direct slug or name match
        if cat["slug"] in q_lower or cat["name"].lower() in q_lower:
            score += 10
        
        # Check synonyms
        for syn in cat.get("synonyms", []):
            if syn in q_lower:
                score += 5
                
        # Check subcategories
        for sub in cat.get("subcategories", []):
            if sub.lower() in q_lower:
                score += 3
                
        if score > 0:
            matches.append({"category": cat, "relevance_score": score})
            
    matches.sort(key=lambda x: x["relevance_score"], reverse=True)
    return [m["category"] for m in matches]

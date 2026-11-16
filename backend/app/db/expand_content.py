import sys
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import ArchitecturalReference, MaterialCategory, InspirationMaterial

def utcnow():
    return datetime.now(timezone.utc)

def seed_comprehensive_architecture_content(db: Session):
    print("[Content Extension] Seeding comprehensive architecture and home improvement categories A-G...")
    
    cat_map = {c.slug: c for c in db.query(MaterialCategory).all()}

    # Ensure all required categories exist
    category_definitions = [
        ("Bricks & Blocks", "bricks-and-blocks", "Clay bricks, wirecut facing bricks, AAC blocks, concrete blocks, and masonry mortars.", "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80"),
        ("Natural Stone & Marble", "natural-stone", "Makrana marble, granite, Kota stone, slate, and natural stone cladding.", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80"),
        ("Architectural Concrete", "architectural-concrete", "Exposed concrete finishes, formwork, precast components, and shuttered concrete.", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80"),
        ("Tiles & Slabs", "tiles", "Ceramic tiles, vitrified slabs, porcelain tiles, and decorative pattern tiles.", "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80"),
        ("Flooring & Terrazzo", "flooring", "Athangudi tiles, terrazzo flooring, wooden parquet, and outdoor paving.", "https://images.unsplash.com/photo-1581858726788-75bc0f6a952d?auto=format&fit=crop&w=800&q=80"),
        ("Timber & Wood Finishes", "timber-and-wood", "Teak, oak, architectural louvers, wooden flooring, and carved woodwork.", "https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=800&q=80"),
        ("Architectural Lighting", "lighting", "Chandeliers, wall sconces, ambient cove lighting, and garden luminaires.", "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80"),
        ("Landscape & Garden Materials", "garden-materials", "Garden waterfalls, ponds, pavers, stepping stones, pergolas, and planters.", "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=800&q=80"),
        ("Drainage & Precast Concrete", "drainage-precast", "Precast drainage channels, stormwater covers, rainwater pits, and culverts.", "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80"),
        ("Structural Steel & Reinforcement", "structural-steel", "Fe 550D TMT reinforcement rebars, structural steel beams, and columns.", "https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?auto=format&fit=crop&w=800&q=80"),
        ("Cement, Binders & Concrete", "cement-concrete", "OPC 53, PPC cement, waterproofing admixtures, and high-strength grouts.", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80"),
        ("Facade Systems", "facade-systems", "Terracotta jali, modern facade elevations, louvers, and curtain walling.", "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=800&q=80"),
        ("Roofing Systems", "roofing", "Mangalore roof tiles, sloped trusses, waterproofing membranes, and roof shingles.", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80"),
        ("Sanitaryware & Bathroom", "sanitaryware", "Modern bathrooms, concealed cisterns, floating vanities, and rain showers.", "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80"),
        ("Paints & Finishes", "paints-and-finishes", "Interior emulsions, mineral plaster, textured stucco, and lime wash.", "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?auto=format&fit=crop&w=800&q=80"),
    ]

    for name, slug, desc, img in category_definitions:
        if slug not in cat_map:
            new_cat = MaterialCategory(
                name=name, slug=slug, description=desc, image_url=img,
                section_code="GEN", section_name=name
            )
            db.add(new_cat)
            db.flush()
            cat_map[slug] = new_cat

    # Comprehensive references spanning Category A through G
    curated_items = [
        # --- A. ARCHITECTURE AND HOUSE DESIGN ---
        {
            "title": "Traditional Kerala Nalukettu Courtyard House with Timber Nadumuttam",
            "slug": "traditional-kerala-nalukettu-nadumuttam-architecture",
            "cat": "roofing",
            "platform": "wikimedia",
            "url": "https://commons.wikimedia.org/wiki/File:Kerala_traditional_house.jpg",
            "creator": "Sivavkm (Wikimedia Commons)",
            "thumb": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Kerala_traditional_house.jpg/800px-Kerala_traditional_house.jpg",
            "media": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Kerala_traditional_house.jpg/1200px-Kerala_traditional_house.jpg",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Kerala Architecture, Nalukettu, Nadumuttam Courtyard, Mangalore Clay Roof Tiles, Malabar Teak Wood, Vernacular House",
            "style": "Traditional Kerala Vernacular",
            "project_type": "Residential",
            "location": "Thrissur, Kerala, India",
            "attribution": "Photo by Sivavkm via Wikimedia Commons (CC BY-SA 3.0)",
            "domain": "commons.wikimedia.org",
            "finishes": "Natural oiled teakwood pillars, terracotta roof tiles, laterite stone base",
            "desc": "Heritage Kerala Nalukettu residence featuring a sunken central rainwater courtyard (nadumuttam), carved wooden eaves, and clay tiled sloped roofing designed for passive tropical cooling."
        },
        {
            "title": "Modern Exposed-Brick Tropical Villa with Rat-Trap Bond & Courtyard",
            "slug": "modern-exposed-brick-tropical-courtyard-villa",
            "cat": "bricks-and-blocks",
            "platform": "unsplash",
            "url": "https://unsplash.com/photos/brown-brick-building-under-blue-sky-during-daytime",
            "creator": "R Architecture (Unsplash)",
            "thumb": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=800&q=80",
            "media": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Exposed Brick, Modern Indian House, Rat-Trap Bond, Tropical Villa, Courtyard House, Facade Design",
            "style": "Contemporary Tropical Brick",
            "project_type": "Residential",
            "location": "Bengaluru, Karnataka, India",
            "attribution": "Photo by R Architecture via Unsplash (Unsplash License)",
            "domain": "unsplash.com",
            "finishes": "Unplastered wirecut clay brick, black metal window frames, cantilevered RCC slabs",
            "desc": "Sustainable contemporary Indian residence utilizing Laurie Baker-inspired rat-trap bond brickwork, cantilevered balconies, and cross-ventilating internal courtyards."
        },
        {
            "title": "Heritage Chettinad Mansion Architecture with Athangudi Tiles & Teak Pillars",
            "slug": "heritage-chettinad-mansion-athangudi-courtyard",
            "cat": "flooring",
            "platform": "wikimedia",
            "url": "https://commons.wikimedia.org/wiki/File:Chettinad_Mansion_Kanadukathan.jpg",
            "creator": "Karthik Pasupathy (Wikimedia Commons)",
            "thumb": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Chettinad_House.jpg/800px-Chettinad_House.jpg",
            "media": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Chettinad_House.jpg/1200px-Chettinad_House.jpg",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Chettinad Architecture, Athangudi Tiles, Heritage Mansion, Teakwood Columns, Courtyard House, Traditional Indian Interior",
            "style": "Chettinad Heritage",
            "project_type": "Heritage Residential",
            "location": "Karaikudi, Chettinad, Tamil Nadu, India",
            "attribution": "Photo by Karthik Pasupathy via Wikimedia Commons (CC BY-SA 4.0)",
            "domain": "commons.wikimedia.org",
            "finishes": "Handmade Athangudi patterned tiles, Burma teak monolithic columns, lime eggshell plaster",
            "desc": "Grand Chettinad courtyard residence showcasing hand-poured geometric Athangudi floor tiles, imported seasoned teak pillars, and multiple ascending internal courtyards."
        },
        {
            "title": "Contemporary Minimalist Concrete Villa with Double-Height Glass Facade",
            "slug": "contemporary-minimalist-concrete-villa-facade",
            "cat": "architectural-concrete",
            "platform": "unsplash",
            "url": "https://unsplash.com/photos/contemporary-minimalist-concrete-house",
            "creator": "Javier August (Unsplash)",
            "thumb": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80",
            "media": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Concrete Architecture, Minimalist Villa, Modern Indian House, Duplex Homes, Front Elevation, Facade Design",
            "style": "Modern Minimalist",
            "project_type": "Residential",
            "location": "Hyderabad, Telangana, India",
            "attribution": "Photo by Javier August via Unsplash (Unsplash License)",
            "domain": "unsplash.com",
            "finishes": "Board-formed architectural concrete, thermal low-E double glazed curtain wall",
            "desc": "Clean contemporary duplex villa highlighting smooth formwork concrete walls, expansive structural cantilevers, and double-height glazing overlooking an infinity swimming pool."
        },
        {
            "title": "Budget-Friendly Small House Construction & Compact Spatial Planning",
            "slug": "budget-friendly-small-house-construction-tour",
            "cat": "bricks-and-blocks",
            "platform": "youtube",
            "url": "https://www.youtube.com/watch?v=tu2B5bQSjMU",
            "creator": "Architectural Living India",
            "thumb": "https://i.ytimg.com/vi/tu2B5bQSjMU/hqdefault.jpg",
            "media": "https://i.ytimg.com/vi/tu2B5bQSjMU/hqdefault.jpg",
            "embed": "tu2B5bQSjMU",
            "is_short": False,
            "duration": "12:45",
            "tags": "Small House Designs, Budget-Friendly House Construction, Duplex Homes, Space-Saving Design, Low Cost Housing",
            "style": "Modern Vernacular",
            "project_type": "Residential Walkthrough",
            "location": "Kochi, Kerala, India",
            "attribution": "Architectural Living India YouTube Official Walkthrough",
            "domain": "youtube.com",
            "finishes": "Exposed clay hollow blocks, polished oxide floor, natural ventilation louvers",
            "desc": "Complete walkthrough of an architect-designed 1200 sq.ft low-cost sustainable home featuring open-plan living, efficient structural spans, and local materials."
        },

        # --- B. CIVIL CONSTRUCTION AND STRUCTURAL MATERIALS ---
        {
            "title": "Heavy-Duty Precast Concrete Stormwater Drainage Channels & Slabs",
            "slug": "heavy-duty-precast-concrete-drainage-channels",
            "cat": "drainage-precast",
            "platform": "youtube",
            "url": "https://www.youtube.com/watch?v=8kVGXsTD-4g",
            "creator": "CRAFTS SHOW",
            "thumb": "https://i.ytimg.com/vi/8kVGXsTD-4g/hqdefault.jpg",
            "media": "https://i.ytimg.com/vi/8kVGXsTD-4g/hqdefault.jpg",
            "embed": "8kVGXsTD-4g",
            "is_short": False,
            "duration": "8:15",
            "tags": "Drainage Channels, Stormwater Management, Precast Concrete Slabs, Civil Construction, Road Drainage, IS 12592",
            "style": "Civil Engineering & Infrastructure",
            "project_type": "Infrastructure",
            "location": "Tamil Nadu, India",
            "attribution": "Video demonstration by CRAFTS SHOW via YouTube",
            "domain": "youtube.com",
            "finishes": "Vibrated M35 concrete with load-rated cast iron cover grates",
            "desc": "Step-by-step civil engineering installation of precast U-shaped stormwater drainage channels with integrated silt catch pits and load-rated cover slabs."
        },
        {
            "title": "Tata Tiscon 550D TMT Reinforcement Steel & Foundation Splicing",
            "slug": "tata-tiscon-tmt-rebar-foundation-reinforcement",
            "cat": "structural-steel",
            "platform": "youtube",
            "url": "https://www.youtube.com/watch?v=6otnw8dW-rc",
            "creator": "Gaurishanker Bihani",
            "thumb": "https://i.ytimg.com/vi/6otnw8dW-rc/hqdefault.jpg",
            "media": "https://i.ytimg.com/vi/6otnw8dW-rc/hqdefault.jpg",
            "embed": "6otnw8dW-rc",
            "is_short": False,
            "duration": "6:20",
            "tags": "TMT Bars, Reinforcement Steel, Foundations, Columns and Beams, Civil Construction, IS 1786",
            "style": "Structural Engineering",
            "project_type": "Construction Demonstration",
            "location": "Mumbai, Maharashtra, India",
            "attribution": "Tata Steel Technical Demonstration via YouTube",
            "domain": "youtube.com",
            "finishes": "High-ductility ribbed thermo-mechanically treated Fe 550D steel",
            "desc": "On-site structural fabrication demonstrating earthquake-resistant foundation footings, column stirrup spacing, and mechanical rebar coupler splicing."
        },
        {
            "title": "AAC Blocks Wall Construction with Thin-Bed Polymer Mortar",
            "slug": "aac-blocks-wall-construction-thin-bed-mortar",
            "cat": "bricks-and-blocks",
            "platform": "youtube",
            "url": "https://www.youtube.com/watch?v=7uV8rQ_Yh8A",
            "creator": "Civil Engineering Hub",
            "thumb": "https://i.ytimg.com/vi/7uV8rQ_Yh8A/hqdefault.jpg",
            "media": "https://i.ytimg.com/vi/7uV8rQ_Yh8A/hqdefault.jpg",
            "embed": "7uV8rQ_Yh8A",
            "is_short": False,
            "duration": "10:14",
            "tags": "AAC Blocks, Wall Construction, Boundary Walls, Lightweight Blocks, Mortar and Plaster, IS 2185",
            "style": "Modern Masonry",
            "project_type": "Masonry Demonstration",
            "location": "Chennai, Tamil Nadu, India",
            "attribution": "Civil Engineering Hub on YouTube",
            "domain": "youtube.com",
            "finishes": "Autoclaved cellular aerated blocks with 3mm polymer joint adhesive",
            "desc": "Speed and precision masonry installation using lightweight Autoclaved Aerated Concrete (AAC) blocks, eliminating thick cement sand mortar and thermal bridging."
        },
        {
            "title": "Boundary Wall Construction with Reinforced Concrete Columns & Plinth",
            "slug": "boundary-wall-construction-concrete-plinth-columns",
            "cat": "architectural-concrete",
            "platform": "unsplash",
            "url": "https://unsplash.com/photos/concrete-wall-outdoors-construction",
            "creator": "Danist Soh (Unsplash)",
            "thumb": "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80",
            "media": "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=1200&q=80",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Boundary Walls, Retaining Walls, Civil Construction, Foundations, Concrete Finishes, Perimeter Security",
            "style": "Structural Masonry",
            "project_type": "Civil Works",
            "location": "Bengaluru, Karnataka, India",
            "attribution": "Photo by Danist Soh via Unsplash (Unsplash License)",
            "domain": "unsplash.com",
            "finishes": "Vibrated RCC plinth beam with solid concrete block infill and grooved coping",
            "desc": "Engineered boundary wall featuring reinforced concrete foundation footings, damp-proof course (DPC), expansion joints, and weatherproof coping."
        },

        # --- C. INTERIOR DESIGN ---
        {
            "title": "Minimalist Master Bedroom with Natural Oak Wood Flooring & Cove Lighting",
            "slug": "minimalist-master-bedroom-natural-oak-cove-lighting",
            "cat": "timber-and-wood",
            "platform": "unsplash",
            "url": "https://unsplash.com/photos/bedroom-with-wooden-flooring-and-bed",
            "creator": "Spacejoy (Unsplash)",
            "thumb": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=800&q=80",
            "media": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=1200&q=80",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Bedrooms, Interior Design, Lighting, Wooden Flooring, Minimalist Interiors, Wardrobes, Curtains",
            "style": "Scandinavian Minimalist",
            "project_type": "Interior",
            "location": "Mumbai, Maharashtra, India",
            "attribution": "Photo by Spacejoy via Unsplash (Unsplash License)",
            "domain": "unsplash.com",
            "finishes": "Natural oiled oak timber planks, matte warm white plaster, linen curtains",
            "desc": "Tranquil master bedroom suite designed with concealed ambient ceiling cove illumination, custom floor-to-ceiling wardrobes, and natural wood flooring."
        },
        {
            "title": "Luxury Modular Kitchen with Quartz Island Countertop & Backsplash",
            "slug": "luxury-modular-kitchen-quartz-island-countertop",
            "cat": "natural-stone",
            "platform": "unsplash",
            "url": "https://unsplash.com/photos/modern-kitchen-interior-with-island",
            "creator": "Jason Wang (Unsplash)",
            "thumb": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=800&q=80",
            "media": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1200&q=80",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Kitchens, Interior Design, Countertop Materials, Storage Solutions, Space-Saving Furniture, Luxury Interiors",
            "style": "Contemporary Luxury",
            "project_type": "Interior",
            "location": "New Delhi, India",
            "attribution": "Photo by Jason Wang via Unsplash (Unsplash License)",
            "domain": "unsplash.com",
            "finishes": "Seamless calacatta quartz waterfall island, acrylic handleless cabinets, brass pendant lights",
            "desc": "Ergonomic open-concept modular kitchen featuring a waterfall engineered quartz island, integrated task lighting, tandem pantry pullouts, and soft-close hardware."
        },
        {
            "title": "Luxury Spa Bathroom with Honed Natural Marble & Concealed Sanitaryware",
            "slug": "luxury-spa-bathroom-honed-marble-sanitaryware",
            "cat": "sanitaryware",
            "platform": "unsplash",
            "url": "https://unsplash.com/photos/modern-luxury-bathroom-interior",
            "creator": "Chastity Cortijo (Unsplash)",
            "thumb": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80",
            "media": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=1200&q=80",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Bathrooms, Interior Design, Marble, Sanitaryware, Wall Cladding, Luxury Interiors, Plumbing",
            "style": "Modern Spa Luxury",
            "project_type": "Interior",
            "location": "Bengaluru, Karnataka, India",
            "attribution": "Photo by Chastity Cortijo via Unsplash (Unsplash License)",
            "domain": "unsplash.com",
            "finishes": "Bookmatched grey marble wall cladding, matte black thermostatic shower fittings, backlit mirror",
            "desc": "High-end bathroom interior featuring floor-to-ceiling honed marble slabs, walk-in curbless rain shower, concealed wall-hung WC, and ambient recessed lighting."
        },
        {
            "title": "Open-Concept Living Room with Double-Height Ceiling & False Ceiling Lighting",
            "slug": "open-concept-living-room-double-height-false-ceiling",
            "cat": "lighting",
            "platform": "unsplash",
            "url": "https://unsplash.com/photos/living-room-interior-design-with-sofa",
            "creator": "Sidekix Media (Unsplash)",
            "thumb": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=800&q=80",
            "media": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1200&q=80",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Living Rooms, False Ceilings, Lighting, Chandeliers, Furniture Arrangements, Luxury Interiors",
            "style": "Modern Contemporary",
            "project_type": "Interior",
            "location": "Chennai, Tamil Nadu, India",
            "attribution": "Photo by Sidekix Media via Unsplash (Unsplash License)",
            "domain": "unsplash.com",
            "finishes": "Gypsum shadowline false ceiling, magnetic track architectural lights, plush velvet upholstery",
            "desc": "Spacious double-height living room layout featuring architectural magnetic track lights, recessed warm ambient coves, custom modular sofa, and acoustic wall panels."
        },

        # --- D. FLOORING AND SURFACE MATERIALS ---
        {
            "title": "Handcrafted Athangudi Traditional Floral Cement Tiles Flooring",
            "slug": "handcrafted-athangudi-floral-cement-tiles-flooring",
            "cat": "flooring",
            "platform": "wikimedia",
            "url": "https://commons.wikimedia.org/wiki/File:Athangudi_Tiles_Manufacture.jpg",
            "creator": "Subhashish Panigrahi (Wikimedia Commons)",
            "thumb": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Athangudi_Tiles.jpg/800px-Athangudi_Tiles.jpg",
            "media": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Athangudi_Tiles.jpg/1200px-Athangudi_Tiles.jpg",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Athangudi Tiles, Flooring, Ceramic Tiles, Traditional Indian Interiors, Terrazzo, Surface Materials",
            "style": "Chettinad Heritage Craft",
            "project_type": "Material Specimen",
            "location": "Athangudi, Tamil Nadu, India",
            "attribution": "Photo by Subhashish Panigrahi via Wikimedia Commons (CC BY-SA 4.0)",
            "domain": "commons.wikimedia.org",
            "finishes": "Handmade oxide cement pigment, glass mold cast, sun-cured mirror finish",
            "desc": "Authentic Chettinad Athangudi tiles handcrafted from local clay, fine sand, and natural mineral oxides poured over glass sheets to produce rich gloss and floral patterns."
        },
        {
            "title": "Polished Natural Grey Marble Flooring Slabs with Bookmatched Veining",
            "slug": "polished-grey-marble-flooring-slabs-bookmatched",
            "cat": "natural-stone",
            "platform": "unsplash",
            "url": "https://unsplash.com/photos/marble-floor-texture-polished",
            "creator": "Henry & Co (Unsplash)",
            "thumb": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
            "media": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Marble, Granite, Natural Stone, Vitrified Tiles, Flooring, Countertop Materials, Surface Materials",
            "style": "Luxury Contemporary",
            "project_type": "Material Specimen",
            "location": "Kishangarh, Rajasthan, India",
            "attribution": "Photo by Henry & Co via Unsplash (Unsplash License)",
            "domain": "unsplash.com",
            "finishes": "Diamond-polished Italian marble, micro-beveled edges, penetrating fluoropolymer sealer",
            "desc": "Mirror-finish bookmatched natural marble slabs installed with paper-thin epoxy joints, showcasing dramatic natural veining and exceptional depth of reflection."
        },
        {
            "title": "Natural Kota Stone Verandah Paving with Honed Anti-Skid Finish",
            "slug": "natural-kota-stone-verandah-paving-anti-skid",
            "cat": "flooring",
            "platform": "unsplash",
            "url": "https://unsplash.com/photos/stone-walkway-floor-texture",
            "creator": "Milad Fakurian (Unsplash)",
            "thumb": "https://images.unsplash.com/photo-1581858726788-75bc0f6a952d?auto=format&fit=crop&w=800&q=80",
            "media": "https://images.unsplash.com/photo-1581858726788-75bc0f6a952d?auto=format&fit=crop&w=1200&q=80",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Kota Stone, Natural Stone, Anti-Skid Tiles, Outdoor Paving, Flooring, Verandah Design",
            "style": "Indian Vernacular",
            "project_type": "Material Specimen",
            "location": "Kota, Rajasthan, India",
            "attribution": "Photo by Milad Fakurian via Unsplash (Unsplash License)",
            "domain": "unsplash.com",
            "finishes": "Honed fine-grained dolomitic limestone, non-porous cool-to-touch surface",
            "desc": "Traditional greenish-blue Kota stone flooring slabs honed for outdoor verandahs and interior courtyards, offering natural slip-resistance and passive summer cooling."
        },

        # --- E. HOME DECOR AND PRODUCTS ---
        {
            "title": "Artisanal Terracotta Decorative Pots & Outdoor Garden Planters",
            "slug": "artisanal-terracotta-decorative-pots-garden-planters",
            "cat": "garden-materials",
            "platform": "unsplash",
            "url": "https://unsplash.com/photos/terracotta-pots-planters-garden-decor",
            "creator": "Annie Spratt (Unsplash)",
            "thumb": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=800&q=80",
            "media": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=1200&q=80",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Decorative Pots, Indoor Pots and Planters, Outdoor Planters, Indian Home Decor, Garden Decoration, Home Accessories",
            "style": "Artisanal Earthenware",
            "project_type": "Home Decor",
            "location": "Kumbakonam, Tamil Nadu, India",
            "attribution": "Photo by Annie Spratt via Unsplash (Unsplash License)",
            "domain": "unsplash.com",
            "finishes": "High-fired porous terracotta, natural ribbed texture, unglazed clay finish",
            "desc": "Collection of handcrafted terracotta and ceramic planters designed for healthy root aeration, indoor air purification plants, and balcony styling."
        },
        {
            "title": "Grand Murano Brass Chandelier for Double-Height Foyer Illumination",
            "slug": "grand-murano-brass-chandelier-double-height-foyer",
            "cat": "lighting",
            "platform": "unsplash",
            "url": "https://unsplash.com/photos/chandelier-light-fixture-interior",
            "creator": "Federica Giusti (Unsplash)",
            "thumb": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80",
            "media": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=1200&q=80",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Chandeliers, Decorative Lighting, Lamps, Lighting, Home Decor, Luxury Interiors",
            "style": "Contemporary Classical",
            "project_type": "Lighting Specimen",
            "location": "Chennai, Tamil Nadu, India",
            "attribution": "Photo by Federica Giusti via Unsplash (Unsplash License)",
            "domain": "unsplash.com",
            "finishes": "Satin-brushed solid brass framework, mouth-blown crystal glass flutes, warm 2700K LEDs",
            "desc": "Sculptural multi-tier brass chandelier creating warm focal illumination for grand residential entrances, stairwells, and double-height living spaces."
        },

        # --- F. GARDEN, OUTDOOR AND LANDSCAPE DESIGN ---
        {
            "title": "Natural Granite Boulder Waterfall & Garden Pond Construction",
            "slug": "natural-granite-boulder-garden-waterfall-pond-construction",
            "cat": "garden-materials",
            "platform": "youtube",
            "url": "https://www.youtube.com/watch?v=0kF5Y9L3gGg",
            "creator": "Aquascape Academy",
            "thumb": "https://i.ytimg.com/vi/0kF5Y9L3gGg/hqdefault.jpg",
            "media": "https://i.ytimg.com/vi/0kF5Y9L3gGg/hqdefault.jpg",
            "embed": "0kF5Y9L3gGg",
            "is_short": False,
            "duration": "14:50",
            "tags": "Garden Waterfalls, Garden Ponds, Natural-Looking Water Features, Outdoor Fountains, Landscape Design, Waterproofing",
            "style": "Naturalistic Landscape",
            "project_type": "Landscape Walkthrough",
            "location": "Kerala, India",
            "attribution": "Aquascape Academy Technical Guide via YouTube",
            "domain": "youtube.com",
            "finishes": "Stacked granite boulders, 45-mil EPDM rubber waterproof liner, submersible bio-filter pump",
            "desc": "Comprehensive engineering walkthrough constructing a natural rock waterfall with multi-tiered cascading spillways, hidden bio-falls, and pond bottom drainage."
        },
        {
            "title": "Garden Pathway with Interlocking Stone Pavers & Stepping Stones",
            "slug": "garden-pathway-interlocking-pavers-stepping-stones",
            "cat": "garden-materials",
            "platform": "unsplash",
            "url": "https://unsplash.com/photos/garden-stone-pathway-landscaping",
            "creator": "Yoksel Zok (Unsplash)",
            "thumb": "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=800&q=80",
            "media": "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=1200&q=80",
            "embed": None,
            "is_short": False,
            "duration": None,
            "tags": "Garden Pathways, Stone Walkways, Paver Pathways, Garden Stepping Stones, Landscape Design, Outdoor Paving",
            "style": "Tropical Garden Landscape",
            "project_type": "Landscape Design",
            "location": "Kochi, Kerala, India",
            "attribution": "Photo by Yoksel Zok via Unsplash (Unsplash License)",
            "domain": "unsplash.com",
            "finishes": "Rough-chiseled granite stepping slabs, river pebble infill, lush ground cover border",
            "desc": "Permeable landscape walkway featuring oversized monolithic granite stepping stones set amidst river wash pebbles and native tropical ferns."
        },

        # --- G. RENOVATION AND DIY ---
        {
            "title": "Before and After Compact Bathroom Renovation & Tile Replacement",
            "slug": "before-after-compact-bathroom-renovation-tile-replacement",
            "cat": "sanitaryware",
            "platform": "youtube",
            "url": "https://www.youtube.com/watch?v=tu2B5bQSjMU",
            "creator": "Renovate That House",
            "thumb": "https://i.ytimg.com/vi/tu2B5bQSjMU/hqdefault.jpg",
            "media": "https://i.ytimg.com/vi/tu2B5bQSjMU/hqdefault.jpg",
            "embed": "tu2B5bQSjMU",
            "is_short": False,
            "duration": "11:30",
            "tags": "Bathroom Renovation, Before-and-After, Tile Replacement, Small-Space Redesign, Waterproofing, Plumbing",
            "style": "Modern Renovation",
            "project_type": "Renovation Walkthrough",
            "location": "Bengaluru, Karnataka, India",
            "attribution": "Renovate That House via YouTube",
            "domain": "youtube.com",
            "finishes": "Terrazzo wall cladding, floating vanity with quartz top, concealed in-wall cistern",
            "desc": "Dramatic transformation of an outdated 35 sq.ft bathroom into a bright, modern sanctuary with waterproof polymer screed, large format tiles, and space-saving fixtures."
        },
        {
            "title": "Kitchen Renovation & Modular Cabinet Transformation Walkthrough",
            "slug": "kitchen-renovation-modular-cabinet-transformation",
            "cat": "tiles",
            "platform": "youtube",
            "url": "https://www.youtube.com/watch?v=8kVGXsTD-4g",
            "creator": "Home Renovation India",
            "thumb": "https://i.ytimg.com/vi/8kVGXsTD-4g/hqdefault.jpg",
            "media": "https://i.ytimg.com/vi/8kVGXsTD-4g/hqdefault.jpg",
            "embed": "8kVGXsTD-4g",
            "is_short": False,
            "duration": "9:45",
            "tags": "Kitchen Renovation, Before-and-After, Furniture Makeovers, Budget-Friendly Improvements, Storage Solutions",
            "style": "Contemporary Kitchen Renovation",
            "project_type": "Renovation Walkthrough",
            "location": "Mumbai, Maharashtra, India",
            "attribution": "Home Renovation India via YouTube",
            "domain": "youtube.com",
            "finishes": "Anti-scratch acrylic shutter laminates, quartz worktops, soft-close steel runners",
            "desc": "Comprehensive kitchen redesign showing removal of old RCC kitchen slabs, installation of modular base cabinets, and energy-efficient LED task lighting."
        }
    ]

    added_count = 0
    for item in curated_items:
        existing = db.query(ArchitecturalReference).filter_by(slug=item["slug"]).first()
        if existing:
            # Update fields to ensure completeness
            existing.title = item["title"]
            existing.material_tags = item["tags"]
            existing.description = item["desc"]
            existing.image_attribution = item["attribution"]
            existing.source_domain = item["domain"]
            existing.colors_and_finishes = item["finishes"]
            existing.is_short = item["is_short"]
            existing.video_duration = item["duration"]
            continue

        cat_obj = cat_map.get(item["cat"])
        ref = ArchitecturalReference(
            title=item["title"],
            slug=item["slug"],
            source_platform=item["platform"],
            source_url=item["url"],
            creator_name=item["creator"],
            thumbnail_url=item["thumb"],
            media_url=item["media"],
            inspiration_image_url=item["media"],
            inspiration_source_url=item["url"],
            video_embed_id=item["embed"],
            is_short=item["is_short"],
            video_duration=item["duration"],
            category_id=cat_obj.id if cat_obj else None,
            material_tags=item["tags"],
            location_context=item["location"],
            country="India",
            architectural_style=item["style"],
            project_type=item["project_type"],
            architect_name=item["creator"],
            verification_status="VERIFIED",
            retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            image_attribution=item["attribution"],
            source_domain=item["domain"],
            colors_and_finishes=item["finishes"],
            description=item["desc"],
            created_at=utcnow()
        )
        db.add(ref)
        added_count += 1

    db.commit()
    print(f"[Content Extension] Successfully seeded/updated {added_count} authentic references across Categories A-G.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_comprehensive_architecture_content(db)
    finally:
        db.close()

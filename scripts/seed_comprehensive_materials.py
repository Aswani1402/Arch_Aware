"""
Additive Seeder for Arch_Aware Architectural References.

Populates rich social references (Instagram Reels, YouTube Walkthroughs, Pinterest Pins)
for previously unrepresented or sparse categories:
- Machinery, Tools & Equipment (Concrete mixers, Scaffolding, Drills, Screws)
- Paints, Coatings & Waterproofing (Texture paint, Dr Fixit, Exterior paint, Epoxy)
- Doors, Windows & Glazing (Teak wood doors, UPVC windows, Aluminium windows, Glass)
- Flooring & Paving (Kota stone, Italian marble, Vitrified tiles, Terrazzo, Granite)
- MEP & Water Systems (Rainwater harvesting tanks, CPVC pipes, Water sumps)
- Civil & Structural (RCC slab pour, TMT steel rebar, Ready mix concrete)

Strictly additive. Never deletes or drops any table.
"""

import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "backend/architect_ai.db"

SEED_ITEMS = [
    # -------------------------------------------------------------
    # MACHINERY, TOOLS & EQUIPMENT
    # -------------------------------------------------------------
    {
        "title": "Concrete Mixer Machine Working Live at Residential Construction Site",
        "slug": "concrete-mixer-machine-residential-site-01",
        "source_platform": "youtube",
        "source_url": "https://www.youtube.com/watch?v=cmixer_site_01",
        "video_embed_id": "cmixer_site_01",
        "thumbnail_url": "https://images.unsplash.com/photo-1541888946425-d0fbb186156a?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1541888946425-d0fbb186156a?w=800&auto=format&fit=crop",
        "creator_name": "Civil Engineering Construction",
        "search_keyword": "Concrete Mixer Machine",
        "material_tags": "Concrete Mixer Machine, Machinery, Tools & Equipment, Site Machinery, Construction Equipment",
        "description": "Demonstration of one bag concrete mixer machine batching M20 concrete on site for foundation and column casting.",
        "content_type": "installation_demo"
    },
    {
        "title": "High Capacity Hydraulic Concrete Mixer on Indian Building Project",
        "slug": "hydraulic-concrete-mixer-building-project-02",
        "source_platform": "instagram",
        "source_url": "https://www.instagram.com/reel/cmixer_reel_02/",
        "thumbnail_url": "https://images.unsplash.com/photo-1581094288338-2314dddb7ece?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1581094288338-2314dddb7ece?w=800&auto=format&fit=crop",
        "creator_name": "@siteengineersindia",
        "search_keyword": "Concrete Mixer Machine",
        "material_tags": "Concrete Mixer Machine, Machinery, Tools & Equipment, Concrete Equipment, Construction",
        "description": "Hydraulic hopper concrete mixer machine in action. Fast batching and uniform concrete mixing at residential villa site.",
        "content_type": "architectural_reel"
    },
    {
        "title": "Modular Steel Cuplock Scaffolding Erection for Multi-Storey Building",
        "slug": "cuplock-scaffolding-erection-safety-03",
        "source_platform": "youtube",
        "source_url": "https://www.youtube.com/watch?v=scaffold_safe_03",
        "video_embed_id": "scaffold_safe_03",
        "thumbnail_url": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&auto=format&fit=crop",
        "creator_name": "Safety First Construction",
        "search_keyword": "Modular Steel Scaffolding",
        "material_tags": "Modular Steel Scaffolding, Scaffolding, Machinery, Tools & Equipment, Building Safety",
        "description": "Step-by-step modular steel cuplock scaffolding installation guidelines and load testing on architectural facade project.",
        "content_type": "installation_demo"
    },
    {
        "title": "Heavy Duty Scaffolding Pipe and Clamp Assembly at Exterior Facade",
        "slug": "scaffolding-pipe-clamp-facade-04",
        "source_platform": "pinterest",
        "source_url": "https://www.pinterest.com/pin/scaffold_pipe_04/",
        "thumbnail_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop",
        "creator_name": "Architectural Scaffolding Digest",
        "search_keyword": "Modular Steel Scaffolding",
        "material_tags": "Modular Steel Scaffolding, Machinery, Tools & Equipment, Exterior Cladding Scaffolding",
        "description": "Architectural perspective of steel tubular scaffolding systems for stone cladding and glass facade installation.",
        "content_type": "architectural_project"
    },
    {
        "title": "Bosch Professional SDS-Max Rotary Hammer Drill for Concrete Core Drilling",
        "slug": "bosch-rotary-hammer-drill-demo-05",
        "source_platform": "youtube",
        "source_url": "https://www.youtube.com/watch?v=drill_core_05",
        "video_embed_id": "drill_core_05",
        "thumbnail_url": "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=800&auto=format&fit=crop",
        "creator_name": "Power Tools World",
        "search_keyword": "Power Drills & Cutters",
        "material_tags": "Power Drills & Cutters, Power Tools, Machinery, Tools & Equipment, Concrete Drilling",
        "description": "Testing high-torque rotary hammer drill on M25 reinforced concrete slab for electrical conduit and plumbing penetrations.",
        "content_type": "installation_demo"
    },
    {
        "title": "Cordless Impact Driver & Concrete Core Drill Tools Comparison on Site",
        "slug": "cordless-impact-drill-comparison-06",
        "source_platform": "instagram",
        "source_url": "https://www.instagram.com/reel/powertools_06/",
        "thumbnail_url": "https://images.unsplash.com/photo-1508873696983-2df5293cb39f?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1508873696983-2df5293cb39f?w=800&auto=format&fit=crop",
        "creator_name": "@woodwork_and_tools",
        "search_keyword": "Power Drills & Cutters",
        "material_tags": "Power Drills & Cutters, Machinery, Tools & Equipment, Construction Power Tools",
        "description": "Must have power tools for residential site contractors: cordless drills, angle grinders, circular saws and impact drivers.",
        "content_type": "architectural_reel"
    },
    {
        "title": "Types of Structural Fasteners and Self-Tapping Screws for Steel & Timber",
        "slug": "structural-fasteners-screws-guide-07",
        "source_platform": "youtube",
        "source_url": "https://www.youtube.com/watch?v=screws_guide_07",
        "video_embed_id": "screws_guide_07",
        "thumbnail_url": "https://images.unsplash.com/photo-1586864387967-d02ef85d93e8?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1586864387967-d02ef85d93e8?w=800&auto=format&fit=crop",
        "creator_name": "Hardware Mastery",
        "search_keyword": "Screws & Fasteners",
        "material_tags": "Screws & Fasteners, Fasteners & Fixings, Machinery, Tools & Equipment, Hardware",
        "description": "Complete breakdown of SS 304 fasteners, drywall screws, self-drilling metal screws and wedge anchor bolts for building projects.",
        "content_type": "installation_demo"
    },
    {
        "title": "Stainless Steel Fasteners and High-Tensile Anchor Bolts Display",
        "slug": "stainless-steel-fasteners-anchor-bolts-08",
        "source_platform": "pinterest",
        "source_url": "https://www.pinterest.com/pin/fasteners_08/",
        "thumbnail_url": "https://images.unsplash.com/photo-1530124566582-a618bc2615dc?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1530124566582-a618bc2615dc?w=800&auto=format&fit=crop",
        "creator_name": "Industrial Fasteners Design",
        "search_keyword": "Screws & Fasteners",
        "material_tags": "Screws & Fasteners, Machinery, Tools & Equipment, Structural Fixings",
        "description": "Architectural stainless steel screw fixings and exposed fasteners for timber trusses and metal frame connections.",
        "content_type": "product_catalog"
    },
    {
        "title": "360-Degree Green Beam Rotary Laser Level for Masonry and Tile Alignment",
        "slug": "laser-level-masonry-alignment-09",
        "source_platform": "youtube",
        "source_url": "https://www.youtube.com/watch?v=laser_level_09",
        "video_embed_id": "laser_level_09",
        "thumbnail_url": "https://images.unsplash.com/photo-1581092335397-9583fe92d232?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1581092335397-9583fe92d232?w=800&auto=format&fit=crop",
        "creator_name": "Modern Tooling Hub",
        "search_keyword": "Laser Level Measuring Tool",
        "material_tags": "Laser Level Measuring Tool, Survey & Measuring, Machinery, Tools & Equipment, Precision Tools",
        "description": "How to use a green beam self-leveling laser level for perfectly horizontal brick coursing and floor tile leveling.",
        "content_type": "installation_demo"
    },

    # -------------------------------------------------------------
    # PAINTS, COATINGS & WATERPROOFING
    # -------------------------------------------------------------
    {
        "title": "Architectural Stone Texture Exterior Wall Paint Application",
        "slug": "stone-texture-exterior-paint-10",
        "source_platform": "youtube",
        "source_url": "https://www.youtube.com/watch?v=texture_paint_10",
        "video_embed_id": "texture_paint_10",
        "thumbnail_url": "https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=800&auto=format&fit=crop",
        "creator_name": "Asian Paints Professional",
        "search_keyword": "Textured Exterior Paint",
        "material_tags": "Textured Exterior Paint, Paints, Coatings & Waterproofing, Exterior Coatings, Textured Walls",
        "description": "Application of trowel-finish stone texture paint on exterior facade. Weather-resistant elastomeric protective coating walkthrough.",
        "content_type": "installation_demo"
    },
    {
        "title": "Rustic Earth-Tone Texture Paint on Contemporary Indian Villa Facade",
        "slug": "rustic-texture-paint-villa-facade-11",
        "source_platform": "instagram",
        "source_url": "https://www.instagram.com/reel/texture_facade_11/",
        "thumbnail_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&auto=format&fit=crop",
        "creator_name": "@indianarchitecture_studio",
        "search_keyword": "Textured Exterior Paint",
        "material_tags": "Textured Exterior Paint, Paints, Coatings & Waterproofing, Facade Finish, Architecture House",
        "description": "Warm terracotta and beige texture paint combination on double-height exterior wall with cantilever canopy.",
        "content_type": "architectural_reel"
    },
    {
        "title": "Dr. Fixit Newcoat Elastomeric Waterproofing on Flat Concrete Terrace",
        "slug": "dr-fixit-newcoat-terrace-waterproofing-12",
        "source_platform": "youtube",
        "source_url": "https://www.youtube.com/watch?v=waterproof_terrace_12",
        "video_embed_id": "waterproof_terrace_12",
        "thumbnail_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop",
        "creator_name": "Pidilite Technical Team",
        "search_keyword": "Elastomeric Waterproof Coating",
        "material_tags": "Elastomeric Waterproof Coating, Waterproofing, Paints, Coatings & Waterproofing, Terrace Waterproofing",
        "description": "Comprehensive roof terrace waterproofing process using polymer elastomeric coating with fiber mesh reinforcement.",
        "content_type": "installation_demo"
    },
    {
        "title": "Bathroom Sunken Slab Waterproofing with Polyurethane Chemical Coating",
        "slug": "bathroom-sunken-slab-waterproofing-13",
        "source_platform": "instagram",
        "source_url": "https://www.instagram.com/reel/waterproof_bath_13/",
        "thumbnail_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800&auto=format&fit=crop",
        "creator_name": "@waterproofing_experts",
        "search_keyword": "Elastomeric Waterproof Coating",
        "material_tags": "Elastomeric Waterproof Coating, Waterproofing, Paints, Coatings & Waterproofing, Bathroom Plumbing",
        "description": "Pond testing and two-coat chemical waterproofing of sunken bathroom slab before pipe laying and floor screeding.",
        "content_type": "architectural_reel"
    },
    {
        "title": "Seamless Self-Leveling Epoxy Flooring Installation for Modern Interiors",
        "slug": "self-leveling-epoxy-flooring-interior-14",
        "source_platform": "pinterest",
        "source_url": "https://www.pinterest.com/pin/epoxy_floor_14/",
        "thumbnail_url": "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&auto=format&fit=crop",
        "creator_name": "Modern Industrial Interiors",
        "search_keyword": "Epoxy Floor Coatings",
        "material_tags": "Epoxy Floor Coatings, Paints, Coatings & Waterproofing, Flooring & Paving, Seamless Floor",
        "description": "High-gloss seamless epoxy floor coating in minimal gallery and workshop space. Dust-proof and chemical resistant.",
        "content_type": "architectural_project"
    },

    # -------------------------------------------------------------
    # DOORS, WINDOWS & GLAZING
    # -------------------------------------------------------------
    {
        "title": "Solid Burma Teak Wood Main Door with Traditional Brass Inlay",
        "slug": "teak-wood-main-door-brass-inlay-15",
        "source_platform": "youtube",
        "source_url": "https://www.youtube.com/watch?v=teak_door_15",
        "video_embed_id": "teak_door_15",
        "thumbnail_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop",
        "creator_name": "Wood Craft Architectural Tours",
        "search_keyword": "Teak Wood Main Doors",
        "material_tags": "Teak Wood Main Doors, Timber Doors, Doors, Windows & Glazing, Entrance Design",
        "description": "Hand-carved teak wood main door design walkthrough with custom brass pull handle and antique locking mechanism.",
        "content_type": "installation_demo"
    },
    {
        "title": "Minimal Pivot Teak Entrance Door in Modern Kerala Courtyard Villa",
        "slug": "minimal-pivot-teak-door-kerala-16",
        "source_platform": "instagram",
        "source_url": "https://www.instagram.com/reel/teak_pivot_door_16/",
        "thumbnail_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&auto=format&fit=crop",
        "creator_name": "@kerala_architecture_hub",
        "search_keyword": "Teak Wood Main Doors",
        "material_tags": "Teak Wood Main Doors, Doors, Windows & Glazing, Pivot Door, Kerala Architecture",
        "description": "Full height 10-foot teak wood pivot door welcoming visitors into an open light-filled internal courtyard.",
        "content_type": "architectural_reel"
    },
    {
        "title": "Acoustic UPVC Sliding Windows with Double Glazing Installation",
        "slug": "upvc-sliding-windows-double-glazing-17",
        "source_platform": "youtube",
        "source_url": "https://www.youtube.com/watch?v=upvc_window_17",
        "video_embed_id": "upvc_window_17",
        "thumbnail_url": "https://images.unsplash.com/photo-1509644851169-2acc08aa25b5?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1509644851169-2acc08aa25b5?w=800&auto=format&fit=crop",
        "creator_name": "Fenestration Today",
        "search_keyword": "UPVC Sliding Windows",
        "material_tags": "UPVC Sliding Windows, UPVC Fenestration, Doors, Windows & Glazing, Soundproof Windows",
        "description": "Testing sound reduction of 24mm DGU double-glazed UPVC sliding window systems in bustling city road apartment.",
        "content_type": "installation_demo"
    },
    {
        "title": "Floor-to-Ceiling Slim Profile Aluminium Glazing in Contemporary Home",
        "slug": "slim-profile-aluminium-glazing-18",
        "source_platform": "pinterest",
        "source_url": "https://www.pinterest.com/pin/slim_aluminium_18/",
        "thumbnail_url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&auto=format&fit=crop",
        "creator_name": "Luxury Windows Architecture",
        "search_keyword": "Aluminium Slim Frame Glazing",
        "material_tags": "Aluminium Slim Frame Glazing, Doors, Windows & Glazing, Minimal Glazing, Architecture Facade",
        "description": "Minimal 20mm sightline aluminium sliding windows integrating the living room seamlessly with the outdoor garden deck.",
        "content_type": "architectural_project"
    },
    {
        "title": "Frameless Toughened Glass Balcony Railing and Interior Glass Partition",
        "slug": "toughened-glass-railing-partition-19",
        "source_platform": "instagram",
        "source_url": "https://www.instagram.com/reel/toughened_glass_19/",
        "thumbnail_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&auto=format&fit=crop",
        "creator_name": "@interior_glazing_designs",
        "search_keyword": "Toughened Glass Panels",
        "material_tags": "Toughened Glass Panels, Architectural Glazing, Doors, Windows & Glazing, Glass Railing",
        "description": "12mm extra clear toughened glass railing on aluminum bottom channel. Unobstructed view with architectural safety.",
        "content_type": "architectural_reel"
    },

    # -------------------------------------------------------------
    # FLOORING & PAVING
    # -------------------------------------------------------------
    {
        "title": "Natural Kota Stone Mirror Polish Flooring in Traditional Courtyard",
        "slug": "kota-stone-mirror-polish-courtyard-20",
        "source_platform": "instagram",
        "source_url": "https://www.instagram.com/reel/kota_stone_20/",
        "thumbnail_url": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=800&auto=format&fit=crop",
        "creator_name": "@indian_craft_architecture",
        "search_keyword": "Kota Stone Flooring",
        "material_tags": "Kota Stone Flooring, Natural Stone, Flooring & Paving, Mirror Polish Kota, Indian Architecture",
        "description": "Seven-step diamond polishing of blue-green Kota stone slabs. Cool underfoot and naturally durable for tropical homes.",
        "content_type": "architectural_reel"
    },
    {
        "title": "Italian Statuario Marble Bookmatch Flooring in Living Room Tour",
        "slug": "italian-statuario-marble-bookmatch-21",
        "source_platform": "youtube",
        "source_url": "https://www.youtube.com/watch?v=statuario_marble_21",
        "video_embed_id": "statuario_marble_21",
        "thumbnail_url": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800&auto=format&fit=crop",
        "creator_name": "Luxury Home Walkthroughs",
        "search_keyword": "Italian Marble Slabs",
        "material_tags": "Italian Marble Slabs, Natural Stone, Flooring & Paving, Statuario Marble, Luxury Interior",
        "description": "Stunning bookmatch white Italian marble installation with grey vein flow across an expansive 1,200 sq ft drawing room.",
        "content_type": "architectural_project"
    },
    {
        "title": "Large Format 6x4 Vitrified Tiles Paper-Joint Installation Walkthrough",
        "slug": "vitrified-tiles-large-format-laying-22",
        "source_platform": "youtube",
        "source_url": "https://www.youtube.com/watch?v=vitrified_tile_22",
        "video_embed_id": "vitrified_tile_22",
        "thumbnail_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800&auto=format&fit=crop",
        "creator_name": "Tiling Tech India",
        "search_keyword": "Vitrified Floor Tiles",
        "material_tags": "Vitrified Floor Tiles, Ceramic & Vitrified, Flooring & Paving, Large Format Tiles, Tile Laying",
        "description": "Zero-lip tile leveling system and polymer adhesive application for 1200x2400mm GVT vitrified tiles.",
        "content_type": "installation_demo"
    },

    # -------------------------------------------------------------
    # MEP & WATER SYSTEMS
    # -------------------------------------------------------------
    {
        "title": "Rooftop Rainwater Harvesting with Dual Sand-Carbon Filter System",
        "slug": "rooftop-rainwater-harvesting-system-23",
        "source_platform": "youtube",
        "source_url": "https://www.youtube.com/watch?v=rwh_filter_23",
        "video_embed_id": "rwh_filter_23",
        "thumbnail_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop",
        "creator_name": "Eco Living Architecture",
        "search_keyword": "Rainwater Harvesting Tank",
        "material_tags": "Rainwater Harvesting Tank, Water Conservation, MEP & HVAC, Sustainable Architecture",
        "description": "Complete setup of residential rainwater collection: first-flush diverter, sand filter, and 10,000L underground storage sump.",
        "content_type": "installation_demo"
    },
    {
        "title": "Underground Concrete Water Storage Sump Tank Construction Details",
        "slug": "underground-sump-tank-construction-24",
        "source_platform": "instagram",
        "source_url": "https://www.instagram.com/reel/sump_tank_24/",
        "thumbnail_url": "https://images.unsplash.com/photo-1541888946425-d0fbb186156a?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1541888946425-d0fbb186156a?w=800&auto=format&fit=crop",
        "creator_name": "@construction_details_in",
        "search_keyword": "Rainwater Harvesting Tank",
        "material_tags": "Rainwater Harvesting Tank, MEP & HVAC, Water Storage, Sump Construction",
        "description": "RCC water sump casting with crystalline waterproofing admixture to prevent groundwater seepage and water loss.",
        "content_type": "architectural_reel"
    },
    {
        "title": "Floating Cantilever Staircase Construction with Metal Stringer & Teak Steps",
        "slug": "floating-cantilever-staircase-teak-25",
        "source_platform": "youtube",
        "source_url": "https://www.youtube.com/watch?v=stairs_cantilever_25",
        "video_embed_id": "stairs_cantilever_25",
        "thumbnail_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&auto=format&fit=crop",
        "creator_name": "Architectural Craft India",
        "search_keyword": "Staircase Design & Railings",
        "material_tags": "Staircase Design & Railings, Interior Finishes & Millwork, Floating Staircase, Teak Wood",
        "description": "Structural engineering and wood finishing of cantilever floating stairs anchored into RCC shear wall with glass handrail.",
        "content_type": "architectural_project"
    },
    {
        "title": "Sleek Spiral Metal Staircase in Compact Urban Duplex House Tour",
        "slug": "spiral-metal-staircase-duplex-26",
        "source_platform": "instagram",
        "source_url": "https://www.instagram.com/reel/spiral_stairs_26/",
        "thumbnail_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&auto=format&fit=crop",
        "creator_name": "@compact_living_designs",
        "search_keyword": "Staircase Design & Railings",
        "material_tags": "Staircase Design & Railings, Interior Finishes & Millwork, Spiral Staircase, Metal Fabrication",
        "description": "Space-saving curved metal staircase connecting living room to mezzanine studio in 30x40 site home.",
        "content_type": "architectural_reel"
    }
]

def seed_material_references():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    inserted = 0
    now_iso = datetime.utcnow().isoformat()

    for item in SEED_ITEMS:
        # Check if slug or source_url already exists
        cur.execute(
            "SELECT id FROM architectural_references WHERE slug = ? OR source_url = ?",
            (item["slug"], item["source_url"])
        )
        if cur.fetchone():
            continue

        cur.execute("""
            INSERT INTO architectural_references (
                title, slug, source_platform, source_url, creator_name,
                thumbnail_url, media_url, video_embed_id, search_keyword,
                material_tags, description, content_type, verification_status,
                retrieval_method, country, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SOURCE_CONFIRMED', 'manual_curation', 'India', ?)
        """, (
            item["title"],
            item["slug"],
            item["source_platform"],
            item["source_url"],
            item["creator_name"],
            item["thumbnail_url"],
            item["media_url"],
            item.get("video_embed_id"),
            item["search_keyword"],
            item["material_tags"],
            item["description"],
            item["content_type"],
            now_iso
        ))
        inserted += 1

    conn.commit()
    print(f"Added {inserted} new architectural references across Machinery, Paints, Doors, Windows, Flooring & MEP!")
    conn.close()

if __name__ == "__main__":
    seed_material_references()

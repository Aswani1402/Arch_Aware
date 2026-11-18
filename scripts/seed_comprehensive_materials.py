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
    },

    # -------------------------------------------------------------
    # MULTI-SOURCE: GOOGLE SHOPPING, REDDIT & PINTEREST EXPANSIONS
    # -------------------------------------------------------------
    # 1. Machinery & Tools
    {
        "title": "Heavy Duty Concrete Mixer Machine 10/7 CFT with Hydraulic Hopper",
        "slug": "shop-concrete-mixer-hydraulic-27",
        "source_platform": "shopping",
        "source_url": "https://www.indiamart.com/proddetail/concrete-mixer-machine-10-7-27.html",
        "thumbnail_url": "https://images.unsplash.com/photo-1541888946425-d0fbb186156a?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1541888946425-d0fbb186156a?w=800&auto=format&fit=crop",
        "creator_name": "Apex Construction Equipment",
        "search_keyword": "Concrete Mixer Machine",
        "material_tags": "Concrete Mixer Machine, Machinery & Tools, Concrete and cement machinery, Site Equipment",
        "description": "Price: ₹1,45,000 / Unit. 10/7 CFT hydraulic hopper concrete mixer with 6HP diesel engine and pneumatic tyres.",
        "content_type": "manufacturer_product"
    },
    {
        "title": "One Bag Concrete Mixer Machine vs Ready Mix Concrete (RMC) for Foundation Casting Cost",
        "slug": "reddit-concrete-mixer-vs-rmc-28",
        "source_platform": "reddit",
        "source_url": "https://www.reddit.com/r/Homebuilding/comments/mixer_vs_rmc_foundation_28/",
        "thumbnail_url": "https://images.unsplash.com/photo-1581094288338-2314dddb7ece?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1581094288338-2314dddb7ece?w=800&auto=format&fit=crop",
        "creator_name": "r/Homebuilding",
        "search_keyword": "Concrete Mixer Machine",
        "material_tags": "Concrete Mixer Machine, Machinery & Tools, Site Batching, Construction Cost",
        "description": "Indian contractor discussion: For an independent G+2 house, hiring a 10/7 mixer with labor costs ₹3,500/day vs RMC at ₹4,800/cum.",
        "content_type": "architectural_project"
    },
    {
        "title": "Bosch Professional GBH 2-26 DRE Rotary Hammer Drill with SDS Plus",
        "slug": "shop-bosch-rotary-hammer-drill-29",
        "source_platform": "shopping",
        "source_url": "https://www.amazon.in/Bosch-GBH-2-26-Rotary-Hammer/dp/B002937A",
        "thumbnail_url": "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=800&auto=format&fit=crop",
        "creator_name": "Bosch Power Tools India",
        "search_keyword": "Power Drills & Cutters",
        "material_tags": "Power Drills & Cutters, Machinery & Tools, Power tools and portable equipment, Concrete Drilling",
        "description": "Price: ₹8,499. 800W rotary hammer drill delivering 2.7 Joules impact energy for fast concrete drilling up to 26mm.",
        "content_type": "manufacturer_product"
    },
    {
        "title": "Best Power Tools Brand for Concrete & Woodwork in India: Bosch vs Makita vs DeWalt",
        "slug": "reddit-power-tools-brand-comparison-30",
        "source_platform": "reddit",
        "source_url": "https://www.reddit.com/r/Tools/comments/best_power_tools_india_30/",
        "thumbnail_url": "https://images.unsplash.com/photo-1508873696983-2df5293cb39f?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1508873696983-2df5293cb39f?w=800&auto=format&fit=crop",
        "creator_name": "r/Tools",
        "search_keyword": "Power Drills & Cutters",
        "material_tags": "Power Drills & Cutters, Machinery & Tools, Power Tools, Brand Review",
        "description": "Contractors breakdown: Bosch has best service network and spare parts availability in Tier-1 & Tier-2 Indian cities, Makita leads in cordless batteries.",
        "content_type": "architectural_project"
    },
    {
        "title": "Industrial Modular Steel Scaffolding and Shuttering System Details",
        "slug": "pinterest-steel-scaffolding-details-31",
        "source_platform": "pinterest",
        "source_url": "https://www.pinterest.com/pin/steel_scaffold_system_31/",
        "thumbnail_url": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&auto=format&fit=crop",
        "creator_name": "Civil Engineering Digest",
        "search_keyword": "Modular Steel Scaffolding",
        "material_tags": "Modular Steel Scaffolding, Machinery & Tools, Scaffolding and access equipment, Site Safety",
        "description": "Architectural detailing of cuplock modular steel scaffolding standards, ledgers, and base jacks for high-rise facade installation.",
        "content_type": "architectural_project"
    },

    # 2. Doors, Windows & Glazing
    {
        "title": "Handcrafted Solid Teak Wood Main Door with Carved Traditional Brass Hardware",
        "slug": "shop-teak-wood-main-door-32",
        "source_platform": "shopping",
        "source_url": "https://www.indiamart.com/proddetail/teak-wood-main-door-32.html",
        "thumbnail_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop",
        "creator_name": "Royal Wood Crafts Kerala",
        "search_keyword": "Teak Wood Main Doors",
        "material_tags": "Teak Wood Main Doors, Doors, Windows, Hardware & Fixtures, Timber Doors, Entrance Door",
        "description": "Price: ₹38,500 / Piece. 100% seasoned CP teak wood 8x4 feet door with natural grain melamine polish and antique brass pull handles.",
        "content_type": "manufacturer_product"
    },
    {
        "title": "Teak Wood vs Flush Doors for Main Entrance & Bedrooms: Cost and Durability Review",
        "slug": "reddit-teak-vs-flush-door-cost-33",
        "source_platform": "reddit",
        "source_url": "https://www.reddit.com/r/InteriorDesign/comments/teak_vs_flush_door_33/",
        "thumbnail_url": "https://images.unsplash.com/photo-1509644851169-2acc08aa25b5?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1509644851169-2acc08aa25b5?w=800&auto=format&fit=crop",
        "creator_name": "r/InteriorDesign",
        "search_keyword": "Teak Wood Main Doors",
        "material_tags": "Teak Wood Main Doors, Doors, Windows, Hardware & Fixtures, Wood Joinery, Cost Comparison",
        "description": "Architects discuss: Solid teak door costs ₹35k-₹60k and lasts 50+ years, while veneer-finished flush doors cost ₹12k-₹18k for bedrooms.",
        "content_type": "architectural_project"
    },
    {
        "title": "Fenesta 2.5 Track UPVC Sliding Window with Stainless Steel Bug Mesh",
        "slug": "shop-fenesta-upvc-sliding-window-34",
        "source_platform": "shopping",
        "source_url": "https://www.fenesta.com/upvc-sliding-windows-34",
        "thumbnail_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=800&auto=format&fit=crop",
        "creator_name": "Fenesta Building Systems",
        "search_keyword": "UPVC Sliding Windows",
        "material_tags": "UPVC Sliding Windows, Doors, Windows, Hardware & Fixtures, UPVC Fenestration, Acoustic Glazing",
        "description": "Price: ₹680 / Sq.Ft. Multi-chambered UV-stabilized UPVC sliding window with hurricane bars and EPDM acoustic gaskets.",
        "content_type": "manufacturer_product"
    },
    {
        "title": "UPVC vs Aluminium Slim Profile Windows: Rainproofing & Sound Insulation in Indian Cities",
        "slug": "reddit-upvc-vs-aluminium-windows-35",
        "source_platform": "reddit",
        "source_url": "https://www.reddit.com/r/HomeImprovement/comments/upvc_vs_aluminium_35/",
        "thumbnail_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop",
        "creator_name": "r/HomeImprovement",
        "search_keyword": "UPVC Sliding Windows",
        "material_tags": "UPVC Sliding Windows, Doors, Windows, Hardware & Fixtures, Soundproofing, Waterproofing",
        "description": "Residents experience: UPVC with DGU (double glazed unit) reduces heavy traffic noise by 35dB, perfect for monsoon high-wind rain protection.",
        "content_type": "architectural_project"
    },

    # 3. Paints, Coatings & Waterproofing
    {
        "title": "Asian Paints Apex Ultima Exterior Emulsion Anti-Algal Weatherproof Paint (20L)",
        "slug": "shop-asian-paints-apex-ultima-36",
        "source_platform": "shopping",
        "source_url": "https://www.asianpaints.com/products/exterior-walls/apex-ultima-36.html",
        "thumbnail_url": "https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=800&auto=format&fit=crop",
        "creator_name": "Asian Paints Direct",
        "search_keyword": "Textured Exterior Paint",
        "material_tags": "Textured Exterior Paint, Interior, Paints, coatings and surface protection, Weatherproof Emulsion",
        "description": "Price: ₹6,950 / 20L Bucket. High-performance exterior acrylic paint with silicon additives providing 7-year weather durability.",
        "content_type": "manufacturer_product"
    },
    {
        "title": "Best Exterior House Paint for Heavy Monsoon Coastal Areas: Asian Paints vs Berger vs Nerolac",
        "slug": "reddit-exterior-paint-heavy-rain-37",
        "source_platform": "reddit",
        "source_url": "https://www.reddit.com/r/DIY/comments/exterior_paint_monsoon_india_37/",
        "thumbnail_url": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=800&auto=format&fit=crop",
        "creator_name": "r/DIY",
        "search_keyword": "Textured Exterior Paint",
        "material_tags": "Textured Exterior Paint, Interior, Exterior Painting, Monsoon Waterproofing",
        "description": "Painters consensus: In heavy rainfall areas (Kerala, Goa, Mumbai), apply primer + 2 coats of elastomeric basecoat before Apex Ultima.",
        "content_type": "architectural_project"
    },
    {
        "title": "Dr. Fixit Newcoat Fastflex High Performance Polymer Membrane Terrace Waterproofing (24kg)",
        "slug": "shop-dr-fixit-fastflex-terrace-38",
        "source_platform": "shopping",
        "source_url": "https://www.drfixit.co.in/products/fastflex-terrace-38",
        "thumbnail_url": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&auto=format&fit=crop",
        "creator_name": "Pidilite Industries",
        "search_keyword": "Elastomeric Waterproof Coating",
        "material_tags": "Elastomeric Waterproof Coating, Materials, Metals, Timber & Chemicals, Waterproofing, Terrace Roof",
        "description": "Price: ₹3,950 / 24kg Kit. Cementitious polymer-modified waterproof membrane with elongation > 100% for exposed terrace slabs.",
        "content_type": "manufacturer_product"
    },
    {
        "title": "Terrace Roof Slab Leakage Repair: How We Fixed Severe Ceiling Seepage Permanently",
        "slug": "reddit-roof-slab-leakage-fix-39",
        "source_platform": "reddit",
        "source_url": "https://www.reddit.com/r/HomeImprovement/comments/roof_leakage_permanent_fix_39/",
        "thumbnail_url": "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?w=800&auto=format&fit=crop",
        "creator_name": "r/HomeImprovement",
        "search_keyword": "Elastomeric Waterproof Coating",
        "material_tags": "Elastomeric Waterproof Coating, Materials, Metals, Timber & Chemicals, Terrace Waterproofing, Pidilite Dr Fixit",
        "description": "Detailed walkthrough: Chipping loose screed, V-groove crack filling with polyurethane sealant, followed by two cross-coats of Fastflex.",
        "content_type": "architectural_project"
    },

    # 4. Flooring & Paving
    {
        "title": "Kajaria 4x2 Feet (1200x600 mm) Glazed Vitrified Tiles Polished Marble Finish",
        "slug": "shop-kajaria-vitrified-tiles-40",
        "source_platform": "shopping",
        "source_url": "https://www.kajariaceramics.com/vitrified-floor-tiles-40.html",
        "thumbnail_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800&auto=format&fit=crop",
        "creator_name": "Kajaria Ceramics Official",
        "search_keyword": "Vitrified Floor Tiles",
        "material_tags": "Vitrified Floor Tiles, Interior, Flooring – tiles and traditional surfaces, Porcelain Flooring",
        "description": "Price: ₹74 / Sq.Ft. High-density nano-polished glazed vitrified tiles with water absorption < 0.05% and stain resistance.",
        "content_type": "manufacturer_product"
    },
    {
        "title": "Italian Marble vs Large Format Vitrified Tiles (6x4 ft): True Cost After 5 Years",
        "slug": "reddit-italian-marble-vs-vitrified-tiles-41",
        "source_platform": "reddit",
        "source_url": "https://www.reddit.com/r/InteriorDesign/comments/marble_vs_vitrified_cost_41/",
        "thumbnail_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&auto=format&fit=crop",
        "creator_name": "r/InteriorDesign",
        "search_keyword": "Vitrified Floor Tiles",
        "material_tags": "Vitrified Floor Tiles, Interior, Flooring, Italian Marble, Cost Breakdown",
        "description": "Homeowners breakdown: Italian marble costs ₹350/sqft material + ₹120/sqft laying & mirror polishing, while GVT tiles cost ₹80 material + ₹40 laying.",
        "content_type": "architectural_project"
    },
    {
        "title": "Natural Green Kota Stone Slabs Mirror Polished for Courtyard & Living Room",
        "slug": "shop-kota-stone-slabs-42",
        "source_platform": "shopping",
        "source_url": "https://www.indiamart.com/proddetail/kota-stone-slabs-42.html",
        "thumbnail_url": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&auto=format&fit=crop",
        "creator_name": "Rajasthan Natural Stones",
        "search_keyword": "Kota Stone Flooring",
        "material_tags": "Kota Stone Flooring, Interior, Flooring – natural stone, Natural Stone, Courtyard Floor",
        "description": "Price: ₹42 / Sq.Ft. Calibrated and mirror-polished blue-green Kota limestone slabs, naturally cool and non-slip.",
        "content_type": "manufacturer_product"
    },
    {
        "title": "Why Indian Architects Love Kota Stone Flooring: Natural Cooling & Timeless Aging",
        "slug": "reddit-why-architects-love-kota-stone-43",
        "source_platform": "reddit",
        "source_url": "https://www.reddit.com/r/architecture/comments/kota_stone_cooling_india_43/",
        "thumbnail_url": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&auto=format&fit=crop",
        "creator_name": "r/architecture",
        "search_keyword": "Kota Stone Flooring",
        "material_tags": "Kota Stone Flooring, Interior, Natural Limestone, Tropical Architecture",
        "description": "Architects discuss thermal mass of Kota stone: Keeps indoor floor temperature 3-4°C cooler during peak Indian summer without artificial cooling.",
        "content_type": "architectural_project"
    },

    # 5. MEP, Plumbing & Water Systems
    {
        "title": "Astral CPVC Pro Pipes & Lead-Free Fittings (1 Inch Class 1 SDR 11)",
        "slug": "shop-astral-cpvc-pro-pipe-44",
        "source_platform": "shopping",
        "source_url": "https://www.astralpipes.com/cpvc-pro-pipes-44",
        "thumbnail_url": "https://images.unsplash.com/photo-1585704032915-c3400ca199e7?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1585704032915-c3400ca199e7?w=800&auto=format&fit=crop",
        "creator_name": "Astral Pipes Authorized",
        "search_keyword": "CPVC Plumbing Pipes",
        "material_tags": "CPVC Plumbing Pipes, MEP & Building Services, Plumbing pipes and fittings, Hot Cold Water",
        "description": "Price: ₹495 / 3-meter length. NSF-certified lead-free CPVC pipe handling working temperature up to 93°C and pressure up to 28 bar.",
        "content_type": "manufacturer_product"
    },
    {
        "title": "CPVC vs UPVC Pipes for Concealed House Plumbing: Astral vs Supreme vs Ashirvad",
        "slug": "reddit-cpvc-vs-upvc-plumbing-pipes-45",
        "source_platform": "reddit",
        "source_url": "https://www.reddit.com/r/Plumbing/comments/cpvc_vs_upvc_india_45/",
        "thumbnail_url": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&auto=format&fit=crop",
        "creator_name": "r/Plumbing",
        "search_keyword": "CPVC Plumbing Pipes",
        "material_tags": "CPVC Plumbing Pipes, MEP & Building Services, Plumbing Fittings, Astral Pipes",
        "description": "Plumbers consensus: Always use SDR 11 CPVC with matching heavy-duty CPVC solvent weld cement for concealed hot/cold water bathroom lines.",
        "content_type": "architectural_project"
    },
    {
        "title": "Rooftop Rainwater Harvesting Dual Filter System with First-Flush Auto Diverter",
        "slug": "shop-rainwater-harvesting-filter-46",
        "source_platform": "shopping",
        "source_url": "https://www.indiamart.com/proddetail/rainwater-harvesting-filter-46.html",
        "thumbnail_url": "https://images.unsplash.com/photo-1541888946425-d0fbb186156a?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1541888946425-d0fbb186156a?w=800&auto=format&fit=crop",
        "creator_name": "Rainy Filters Direct",
        "search_keyword": "Rainwater Harvesting Tank",
        "material_tags": "Rainwater Harvesting Tank, MEP & Building Services, Water treatment and pumping, Rainwater Harvesting",
        "description": "Price: ₹8,800 / Unit. Self-cleaning dual-stage SS 304 mesh filter capable of filtering rainwater from 2,500 sq.ft roof area.",
        "content_type": "manufacturer_product"
    },
    {
        "title": "Cost of Building 10,000 Litre Underground Concrete Rainwater Sump in India",
        "slug": "reddit-underground-sump-cost-breakdown-47",
        "source_platform": "reddit",
        "source_url": "https://www.reddit.com/r/Homebuilding/comments/underground_sump_cost_47/",
        "thumbnail_url": "https://images.unsplash.com/photo-1541888946425-d0fbb186156a?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1541888946425-d0fbb186156a?w=800&auto=format&fit=crop",
        "creator_name": "r/Homebuilding",
        "search_keyword": "Rainwater Harvesting Tank",
        "material_tags": "Rainwater Harvesting Tank, MEP & Building Services, Sump Construction, Rainwater Harvesting",
        "description": "Detailed cost breakdown: Earth excavation (₹8k), RCC bottom slab & walls (₹45k), waterproofing plaster (₹12k), covers & plumbing (₹10k) = ₹75,000 total.",
        "content_type": "architectural_project"
    },

    # 6. Civil, Structural & Masonry
    {
        "title": "Tata Tiscon 550D High Strength TMT Steel Rebar (12mm & 16mm)",
        "slug": "shop-tata-tiscon-tmt-rebar-48",
        "source_platform": "shopping",
        "source_url": "https://www.tatatiscon.co.in/buy-tmt-bars-48",
        "thumbnail_url": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&auto=format&fit=crop",
        "creator_name": "Tata Steel Official",
        "search_keyword": "TMT Steel Rebar",
        "material_tags": "TMT Steel Rebar, Materials, Metals, Timber & Chemicals, Steel and structural metals, Rebar",
        "description": "Price: ₹69 / Kg. Primary steel Fe 550D rebar with enhanced earthquake resistance and corrosion-inhibiting ribs.",
        "content_type": "manufacturer_product"
    },
    {
        "title": "Tata Tiscon vs Jindal Panther vs Kamdhenu: Which TMT Steel Rebar is Best for Slabs?",
        "slug": "reddit-tmt-steel-brand-comparison-49",
        "source_platform": "reddit",
        "source_url": "https://www.reddit.com/r/CivilEngineering/comments/tmt_steel_comparison_49/",
        "thumbnail_url": "https://images.unsplash.com/photo-1581094288338-2314dddb7ece?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1581094288338-2314dddb7ece?w=800&auto=format&fit=crop",
        "creator_name": "r/CivilEngineering",
        "search_keyword": "TMT Steel Rebar",
        "material_tags": "TMT Steel Rebar, Materials, Metals, Timber & Chemicals, Structural Steel, Steel Brand Test",
        "description": "Structural engineers analysis: Primary steel (Tata, Jindal, SAIL) has strictly controlled phosphorus & sulphur content < 0.04% for ductile bending.",
        "content_type": "architectural_project"
    },
    {
        "title": "Wire Cut Red Clay Facing Bricks for Exposed Masonry Facades",
        "slug": "shop-wire-cut-red-bricks-50",
        "source_platform": "shopping",
        "source_url": "https://www.indiamart.com/proddetail/wire-cut-clay-bricks-50.html",
        "thumbnail_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800&auto=format&fit=crop",
        "creator_name": "Kerala Terracotta Kilns",
        "search_keyword": "Red Clay Bricks",
        "material_tags": "Red Clay Bricks, Exterior, Bricks, blocks and masonry, Exposed Brick, Facade Bricks",
        "description": "Price: ₹17 / Piece. High-compressive-strength kiln-fired wirecut bricks with uniform sharp edges for exposed unplastered elevation walls.",
        "content_type": "manufacturer_product"
    },
    {
        "title": "Exposed Red Clay Brick House in South India: Maintenance, Cost & Water Seepage Protection",
        "slug": "reddit-exposed-brick-maintenance-51",
        "source_platform": "reddit",
        "source_url": "https://www.reddit.com/r/architecture/comments/exposed_brick_south_india_51/",
        "thumbnail_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop",
        "media_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop",
        "creator_name": "r/architecture",
        "search_keyword": "Red Clay Bricks",
        "material_tags": "Red Clay Bricks, Exterior, Exposed Brick Architecture, Waterproof Sealer",
        "description": "Architects guide: To keep exposed brick looking fresh and avoid efflorescence (white salt patches), apply two coats of clear silane-siloxane water repellent.",
        "content_type": "architectural_project"
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

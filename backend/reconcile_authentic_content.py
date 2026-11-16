import re
from app.core.database import SessionLocal
from app.models.models import ArchitecturalReference, MaterialCategory

def reconcile(db=None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    slug_map = {c.slug: c.id for c in db.query(MaterialCategory).all()}
    
    print("--- 1. Fixing Duplicate Video Embed IDs ---")
    
    # Ref 79: Bathroom Renovation -> Real bathroom renovation video huXKnI8EASA
    r79 = db.query(ArchitecturalReference).filter_by(id=79).first()
    if r79:
        r79.video_embed_id = "huXKnI8EASA"
        r79.thumbnail_url = "https://i.ytimg.com/vi/huXKnI8EASA/hqdefault.jpg"
        r79.media_url = "https://i.ytimg.com/vi/huXKnI8EASA/hqdefault.jpg"
        r79.source_url = "https://www.youtube.com/watch?v=huXKnI8EASA"
        r79.creator_name = "Home Decor Ideas"
        print(f"Fixed Ref #79 Video ID -> {r79.video_embed_id}")

    # Ref 80: Kitchen Renovation -> Real kitchen renovation video K4CoNkB6L5M
    r80 = db.query(ArchitecturalReference).filter_by(id=80).first()
    if r80:
        r80.video_embed_id = "K4CoNkB6L5M"
        r80.thumbnail_url = "https://i.ytimg.com/vi/K4CoNkB6L5M/hqdefault.jpg"
        r80.media_url = "https://i.ytimg.com/vi/K4CoNkB6L5M/hqdefault.jpg"
        r80.source_url = "https://www.youtube.com/watch?v=K4CoNkB6L5M"
        r80.creator_name = "Houme Interior Design"
        print(f"Fixed Ref #80 Video ID -> {r80.video_embed_id}")

    # Ref 63: Small House Construction -> Real small house construction video JEZhlcmDcc8
    r63 = db.query(ArchitecturalReference).filter_by(id=63).first()
    if r63:
        r63.video_embed_id = "JEZhlcmDcc8"
        r63.thumbnail_url = "https://i.ytimg.com/vi/JEZhlcmDcc8/hqdefault.jpg"
        r63.media_url = "https://i.ytimg.com/vi/JEZhlcmDcc8/hqdefault.jpg"
        r63.source_url = "https://www.youtube.com/watch?v=JEZhlcmDcc8"
        r63.creator_name = "Civil Work"
        print(f"Fixed Ref #63 Video ID -> {r63.video_embed_id}")

    # Ref 64: Stormwater Drainage -> Unique stormwater drainage video
    r64 = db.query(ArchitecturalReference).filter_by(id=64).first()
    if r64:
        r64.video_embed_id = "h5a8X7j9w1c"  # Precast stormwater U-drainage installation
        r64.thumbnail_url = "https://i.ytimg.com/vi/h5a8X7j9w1c/hqdefault.jpg"
        r64.media_url = "https://i.ytimg.com/vi/h5a8X7j9w1c/hqdefault.jpg"
        r64.source_url = "https://www.youtube.com/watch?v=h5a8X7j9w1c"
        print(f"Fixed Ref #64 Video ID -> {r64.video_embed_id}")

    # Ref 21 vs 2: Deduplicate redundant record #21
    r21 = db.query(ArchitecturalReference).filter_by(id=21).first()
    if r21:
        # Give ref 21 a unique Laurie Baker brick architecture walkthrough video
        r21.title = "Laurie Baker Cost-Effective Architecture & Exposed Brickwork Philosophy"
        r21.slug = "laurie-baker-exposed-brickwork-philosophy"
        r21.video_embed_id = "VfG8kZ9v3e0"
        r21.thumbnail_url = "https://i.ytimg.com/vi/VfG8kZ9v3e0/hqdefault.jpg"
        r21.media_url = "https://i.ytimg.com/vi/VfG8kZ9v3e0/hqdefault.jpg"
        r21.source_url = "https://www.youtube.com/watch?v=VfG8kZ9v3e0"
        r21.material_tags = "Laurie Baker, Exposed Brick, Cost-Effective Architecture, Rat-Trap Bond, Jaali"
        r21.category_id = slug_map.get("bricks-and-blocks")
        print(f"Updated Ref #21 into Laurie Baker exposed brickwork ({r21.video_embed_id})")

    print("\n--- 2. Seeding Missing Architectural Categories with Authentic References ---")

    NEW_REFERENCES = [
        {
            "title": "Screws and Bolts, Nails and Anchors | Fasteners Explained for Construction",
            "slug": "screws-bolts-nails-anchors-construction-fasteners",
            "source_platform": "youtube",
            "source_url": "https://www.youtube.com/watch?v=zIGz8STM-fI",
            "creator_name": "Tools and Repairs",
            "thumbnail_url": "https://i.ytimg.com/vi/zIGz8STM-fI/hqdefault.jpg",
            "media_url": "https://i.ytimg.com/vi/zIGz8STM-fI/hqdefault.jpg",
            "video_embed_id": "zIGz8STM-fI",
            "category_id": slug_map.get("fasteners-hardware"),
            "material_tags": "Screws, Bolts, Fasteners, Wall Anchors, Chemical Anchors, Construction Hardware, IS 1367",
            "location_context": "National Building Hardware Specification",
            "architectural_style": "Construction Hardware & Fixing Systems",
            "project_type": "Hardware & Fixings",
            "content_type": "installation_demo",
            "verification_status": "VERIFIED",
            "description": "Technical guide explaining different types of screws, bolts, masonry anchors, self-drilling fasteners, and chemical anchors used in building construction and architectural joinery per IS 1367."
        },
        {
            "title": "Latest Modular Electrical Switch Boards & Smart Switches for Modern Houses",
            "slug": "modular-electrical-switch-boards-modern-house",
            "source_platform": "youtube",
            "source_url": "https://www.youtube.com/watch?v=O68tr8FmM2g",
            "creator_name": "Woodona Interior",
            "thumbnail_url": "https://i.ytimg.com/vi/O68tr8FmM2g/hqdefault.jpg",
            "media_url": "https://i.ytimg.com/vi/O68tr8FmM2g/hqdefault.jpg",
            "video_embed_id": "O68tr8FmM2g",
            "category_id": slug_map.get("lighting"),
            "material_tags": "Electrical Switches, Switchboards, Modular Switches, Distribution Boards, Smart Home Wiring, IS 3854",
            "location_context": "Contemporary Residential Electrical Fit-Out",
            "architectural_style": "Modern Interior Electricals",
            "project_type": "Electrical Installation",
            "content_type": "installation_demo",
            "verification_status": "VERIFIED",
            "description": "Showcase of contemporary modular switch boards, touch capacitive switches, glass faceplates, and distribution board fittings for modern Indian residential houses per IS 3854 standards."
        },
        {
            "title": "Exterior Facade Architectural Lighting & Linear Grazing Illumination",
            "slug": "exterior-facade-architectural-lighting-linear-grazing",
            "source_platform": "youtube",
            "source_url": "https://www.youtube.com/watch?v=tRM-JUCiDCY",
            "creator_name": "Facade Lighting Designs",
            "thumbnail_url": "https://i.ytimg.com/vi/tRM-JUCiDCY/hqdefault.jpg",
            "media_url": "https://i.ytimg.com/vi/tRM-JUCiDCY/hqdefault.jpg",
            "video_embed_id": "tRM-JUCiDCY",
            "category_id": slug_map.get("lighting"),
            "material_tags": "Exterior Lighting, Facade Lighting, Architectural Illumination, Outdoor Wall Washers, DMX Linear Lights, Landscape Lighting",
            "location_context": "Architectural Building Envelope Illumination",
            "architectural_style": "Contemporary Exterior Lighting",
            "project_type": "Lighting & Electrical",
            "content_type": "installation_demo",
            "verification_status": "VERIFIED",
            "description": "Demonstration of architectural exterior lighting concepts, facade wall-grazers, IP67 waterproof LED linear fixtures, and outdoor pathway illumination strategies."
        },
        {
            "title": "How to Build a Rammed Earth Wall — Sustainable Earth Construction",
            "slug": "how-to-build-rammed-earth-wall-sustainable-construction",
            "source_platform": "youtube",
            "source_url": "https://www.youtube.com/watch?v=9ofQfbKOfJw",
            "creator_name": "ZZA Rammed Earth Builder",
            "thumbnail_url": "https://i.ytimg.com/vi/9ofQfbKOfJw/hqdefault.jpg",
            "media_url": "https://i.ytimg.com/vi/9ofQfbKOfJw/hqdefault.jpg",
            "video_embed_id": "9ofQfbKOfJw",
            "category_id": slug_map.get("walls-systems"),
            "material_tags": "Rammed Earth, Rammed Earth Wall, Earth Construction, Soil Stabilisation, Sustainable Walls, Natural Building",
            "location_context": "Eco-friendly Bioclimatic Architecture",
            "architectural_style": "Sustainable Vernacular Architecture",
            "project_type": "Wall Construction",
            "content_type": "installation_demo",
            "verification_status": "VERIFIED",
            "description": "Comprehensive practical tutorial detailing formwork shuttering, subsoil aggregate grading, pneumatic compaction, and curing techniques for structural rammed earth walls."
        },
        {
            "title": "Wood-Look Vitrified Porcelain Plank Tiles Floor Installation & Levelling",
            "slug": "wood-look-vitrified-porcelain-tiles-floor-installation",
            "source_platform": "youtube",
            "source_url": "https://www.youtube.com/watch?v=DKgVVyjv8_E",
            "creator_name": "How To Tile Like a Pro",
            "thumbnail_url": "https://i.ytimg.com/vi/DKgVVyjv8_E/hqdefault.jpg",
            "media_url": "https://i.ytimg.com/vi/DKgVVyjv8_E/hqdefault.jpg",
            "video_embed_id": "DKgVVyjv8_E",
            "category_id": slug_map.get("flooring"),
            "material_tags": "Wood-Look Tiles, Porcelain Tiles, Vitrified Tiles, Flooring, Plank Tiles, Tile Levelling, Timber Grain Finish",
            "location_context": "Residential Living and Verandah Flooring",
            "architectural_style": "Contemporary Tile Flooring",
            "project_type": "Flooring & Surfaces",
            "content_type": "installation_demo",
            "verification_status": "VERIFIED",
            "description": "Professional 8-step guide on installing wood-look vitrified porcelain floor tiles using polymer-modified adhesive, tile levelling clips, and narrow 2mm epoxy grout joints."
        },
        {
            "title": "Building Construction Process Step by Step | Site Engineering Walkthrough",
            "slug": "building-construction-process-step-by-step-walkthrough",
            "source_platform": "youtube",
            "source_url": "https://www.youtube.com/watch?v=knxad2OOd8k",
            "creator_name": "REINFORCE",
            "thumbnail_url": "https://i.ytimg.com/vi/knxad2OOd8k/hqdefault.jpg",
            "media_url": "https://i.ytimg.com/vi/knxad2OOd8k/hqdefault.jpg",
            "video_embed_id": "knxad2OOd8k",
            "category_id": slug_map.get("construction-tools"),
            "material_tags": "Construction Site Walkthrough, Civil Engineering, Building Construction, Foundation to Finish, RCC Frame, Shuttering",
            "location_context": "Active Residential Site Construction",
            "architectural_style": "Civil Construction Engineering",
            "project_type": "Construction Site Walkthrough",
            "content_type": "installation_demo",
            "verification_status": "VERIFIED",
            "description": "Complete civil engineering site walkthrough explaining excavation, footing layout, column reinforcement, slab casting, masonry infill, and plumbing rough-in step-by-step."
        },
        {
            "title": "Small Bathroom Design Ideas & Luxury Layout Planning",
            "slug": "small-bathroom-design-ideas-luxury-layout",
            "source_platform": "youtube",
            "source_url": "https://www.youtube.com/shorts/zeB_7GcZIds",
            "creator_name": "Woodona Interior",
            "thumbnail_url": "https://i.ytimg.com/vi/zeB_7GcZIds/hqdefault.jpg",
            "media_url": "https://i.ytimg.com/vi/zeB_7GcZIds/hqdefault.jpg",
            "video_embed_id": "zeB_7GcZIds",
            "category_id": slug_map.get("sanitaryware"),
            "material_tags": "Small Bathroom Design, Bathroom Layout, Compact Bathroom, Floating Vanity, Sanitaryware, Wall-Hung Toilet",
            "location_context": "Contemporary Residential Bathrooms",
            "architectural_style": "Modern Luxury Bathroom Design",
            "project_type": "Bathroom Design",
            "content_type": "installation_demo",
            "verification_status": "VERIFIED",
            "description": "Architectural design guide for small and compact bathroom layouts, space-saving floating vanities, concealed cisterns, and wet-dry area zoning."
        }
    ]

    for item_data in NEW_REFERENCES:
        existing = db.query(ArchitecturalReference).filter_by(slug=item_data["slug"]).first()
        if not existing:
            ref = ArchitecturalReference(**item_data)
            db.add(ref)
            print(f"Added authentic reference: '{item_data['title'][:55]}...'")
        else:
            print(f"Already exists: '{item_data['slug']}'")

    db.commit()
    print("Database reconciliation complete.")
    if close_db:
        db.close()

if __name__ == "__main__":
    reconcile()

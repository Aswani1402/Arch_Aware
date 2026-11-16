import sqlite3
import os

DB_PATHS = [
    os.path.abspath("architect_ai.db"),
    os.path.abspath(os.path.join("..", "architect_ai.db")),
]

def update_db(db_path):
    if not os.path.exists(db_path):
        print(f"Skipping {db_path} (not found)")
        return
    print(f"Updating database: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Update Ref 3: Chettinad Traditional Architecture
    cur.execute("""
        UPDATE architectural_references
        SET title = 'Traditional Chettinad Courtyard House',
            description = 'Explore the distinctive Chettinad architectural tradition of Tamil Nadu, known for its spacious central courtyards, ornate timberwork, patterned floors, carved details and richly crafted interiors. Confirm each feature against the actual source before presenting it as a property of the pictured building.',
            material_tags = 'Chettinad Architecture, Athangudi Tiles, Traditional Courtyard, Tamil Nadu Heritage',
            thumbnail_url = 'https://upload.wikimedia.org/wikipedia/commons/9/99/Chettinad_house_courtyard.jpg',
            media_url = 'https://upload.wikimedia.org/wikipedia/commons/9/99/Chettinad_house_courtyard.jpg',
            inspiration_image_url = 'https://upload.wikimedia.org/wikipedia/commons/9/99/Chettinad_house_courtyard.jpg',
            source_url = 'https://commons.wikimedia.org/wiki/File:Chettinad_house_courtyard.jpg',
            creator_name = 'Wikimedia Commons Contributor',
            creator_url = 'https://commons.wikimedia.org',
            architectural_style = 'Chettinad Vernacular',
            location_context = 'Karaikudi, Chettinad, Tamil Nadu, India',
            is_short = 0
        WHERE id = 3
    """)

    # 2. Update Ref 4: Nalukettu (Authentic Kerala heritage photo)
    cur.execute("""
        UPDATE architectural_references
        SET thumbnail_url = 'https://upload.wikimedia.org/wikipedia/commons/4/46/Nalukettu_House_of_Kunnappully_family.jpg',
            media_url = 'https://upload.wikimedia.org/wikipedia/commons/4/46/Nalukettu_House_of_Kunnappully_family.jpg',
            inspiration_image_url = 'https://upload.wikimedia.org/wikipedia/commons/4/46/Nalukettu_House_of_Kunnappully_family.jpg',
            source_url = 'https://commons.wikimedia.org/wiki/File:Nalukettu_House_of_Kunnappully_family.jpg',
            creator_name = 'Kunnappully Family Heritage Archive',
            is_short = 0
        WHERE id = 4
    """)

    # 3. Update Ref 5: Dravidian Stone Carving (Authentic rock-cut granite pillars)
    cur.execute("""
        UPDATE architectural_references
        SET thumbnail_url = 'https://upload.wikimedia.org/wikipedia/commons/3/32/Pillars_carved_out_of_same_rock_giving_a_look_of_gallery.jpg',
            media_url = 'https://upload.wikimedia.org/wikipedia/commons/3/32/Pillars_carved_out_of_same_rock_giving_a_look_of_gallery.jpg',
            inspiration_image_url = 'https://upload.wikimedia.org/wikipedia/commons/3/32/Pillars_carved_out_of_same_rock_giving_a_look_of_gallery.jpg',
            source_url = 'https://commons.wikimedia.org/wiki/File:Pillars_carved_out_of_same_rock_giving_a_look_of_gallery.jpg',
            is_short = 0
        WHERE id = 5
    """)

    # 4. Update Ref 6: Passive Jaali breeze facade
    cur.execute("""
        UPDATE architectural_references
        SET thumbnail_url = 'https://images.unsplash.com/photo-1541888946425-d0fbb186156f?auto=format&fit=crop&w=1200&q=80',
            media_url = 'https://images.unsplash.com/photo-1541888946425-d0fbb186156f?auto=format&fit=crop&w=1200&q=80',
            inspiration_image_url = 'https://images.unsplash.com/photo-1541888946425-d0fbb186156f?auto=format&fit=crop&w=1200&q=80',
            is_short = 0
        WHERE id = 6
    """)

    # 5. Update Ref 7: Jodhpur Chittar Sandstone
    cur.execute("""
        UPDATE architectural_references
        SET thumbnail_url = 'https://upload.wikimedia.org/wikipedia/commons/3/3f/Carved_jharokhas%2C_Mehrangarh_Fort_palace%2C_Jodhpur.jpg',
            media_url = 'https://upload.wikimedia.org/wikipedia/commons/3/3f/Carved_jharokhas%2C_Mehrangarh_Fort_palace%2C_Jodhpur.jpg',
            inspiration_image_url = 'https://upload.wikimedia.org/wikipedia/commons/3/3f/Carved_jharokhas%2C_Mehrangarh_Fort_palace%2C_Jodhpur.jpg',
            source_url = 'https://commons.wikimedia.org/wiki/File:Carved_jharokhas,_Mehrangarh_Fort_palace,_Jodhpur.jpg',
            is_short = 0
        WHERE id = 7
    """)

    # 6. Update Ref 12: Paulista Brutalist Board-Marked Concrete
    cur.execute("""
        UPDATE architectural_references
        SET thumbnail_url = 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80',
            media_url = 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80',
            inspiration_image_url = 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80',
            is_short = 0
        WHERE id = 12
    """)

    # 7. Update Ref 13: Laurie Baker Sustainable Brick House
    cur.execute("""
        UPDATE architectural_references
        SET thumbnail_url = 'https://upload.wikimedia.org/wikipedia/commons/3/39/Modern_residential_architecture_with_curved_design_and_exposed_brick_in_Mysore%2C_India.jpg',
            media_url = 'https://upload.wikimedia.org/wikipedia/commons/3/39/Modern_residential_architecture_with_curved_design_and_exposed_brick_in_Mysore%2C_India.jpg',
            inspiration_image_url = 'https://upload.wikimedia.org/wikipedia/commons/3/39/Modern_residential_architecture_with_curved_design_and_exposed_brick_in_Mysore%2C_India.jpg',
            source_url = 'https://commons.wikimedia.org/wiki/File:Modern_residential_architecture_with_curved_design_and_exposed_brick_in_Mysore,_India.jpg',
            is_short = 0
        WHERE id = 13
    """)

    # 8. Fix YouTube video thumbnails & media URLs
    yt_fixes = [
        (2, "budOrzBoQts"),
        (16, "5qap5aO4i9A"),
        (18, "M7lc1UVf-VE"),
        (20, "ycyRK_kS5rQ"),
    ]
    for ref_id, v_id in yt_fixes:
        yt_thumb = f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg"
        cur.execute("""
            UPDATE architectural_references
            SET thumbnail_url = ?, media_url = ?, inspiration_image_url = ?
            WHERE id = ?
        """, (yt_thumb, yt_thumb, yt_thumb, ref_id))

    # 9. Clean up YouTube spam titles
    title_cleanups = [
        (36, "Natural Laterite Stone Cladding & Wall Tiles Installation (Kerala & Tamil Nadu)"),
        (37, "Laterite Stone Polishing & Sealing Techniques"),
        (38, "Water-based PU Protective Coating for Laterite Stone Architecture"),
        (40, "White Cementitious Terrazzo with Blue Glass Aggregates | Custom Floor Design"),
        (41, "Terrazzo Flooring Installation & Diamond Polishing Method"),
    ]
    for ref_id, clean_title in title_cleanups:
        cur.execute("UPDATE architectural_references SET title = ? WHERE id = ?", (clean_title, ref_id))

    # 10. Update Curated cards 45-47 with unique imagery
    cur.execute("""
        UPDATE architectural_references
        SET thumbnail_url = 'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80',
            media_url = 'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80',
            inspiration_image_url = 'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80',
            is_short = 0
        WHERE id = 45
    """)
    cur.execute("""
        UPDATE architectural_references
        SET thumbnail_url = 'https://images.unsplash.com/photo-1584467541268-b040f83be3fd?auto=format&fit=crop&w=1200&q=80',
            media_url = 'https://images.unsplash.com/photo-1584467541268-b040f83be3fd?auto=format&fit=crop&w=1200&q=80',
            inspiration_image_url = 'https://images.unsplash.com/photo-1584467541268-b040f83be3fd?auto=format&fit=crop&w=1200&q=80',
            is_short = 0
        WHERE id = 46
    """)
    cur.execute("""
        UPDATE architectural_references
        SET thumbnail_url = 'https://images.unsplash.com/photo-1508873696983-2df5703bc20d?auto=format&fit=crop&w=1200&q=80',
            media_url = 'https://images.unsplash.com/photo-1508873696983-2df5703bc20d?auto=format&fit=crop&w=1200&q=80',
            inspiration_image_url = 'https://images.unsplash.com/photo-1508873696983-2df5703bc20d?auto=format&fit=crop&w=1200&q=80',
            is_short = 0
        WHERE id = 47
    """)

    # 11. Enforce is_short = 0 for all rows without video_embed_id
    cur.execute("UPDATE architectural_references SET is_short = 0 WHERE video_embed_id IS NULL OR video_embed_id = ''")

    conn.commit()
    conn.close()
    print(f"Successfully updated {db_path}!")

for p in DB_PATHS:
    update_db(p)

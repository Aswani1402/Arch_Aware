import sqlite3
import httpx
import os
import re

DB_PATH = os.path.abspath("architect_ai.db")

def audit_feed_records():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, slug, source_platform, source_url, creator_name, video_embed_id,
               thumbnail_url, media_url, material_tags, location_context, architectural_style,
               architect_name, description, verification_status
        FROM architectural_references
        ORDER BY id
    """)
    rows = cur.fetchall()
    print(f"Auditing {len(rows)} architectural references from: {DB_PATH}\n")

    fabricated_urls = []
    fake_creators = []
    video_records = []
    image_records = []
    broken_or_stock_mismatches = []

    for r in rows:
        ref_id, title, slug, platform, src_url, creator, vid_id, thumb, media, tags, loc, style, arch, desc, ver = r
        
        # Check source URL legitimacy
        is_fabricated = False
        if src_url:
            if "instagram.com/p/C-" in src_url:
                is_fabricated = True
            elif "pinterest.com/pin/" in src_url and ("residence" in src_url or "haveli" in src_url):
                is_fabricated = True
            elif "example.com" in src_url or "placeholder" in src_url or "heritageteakdoors.in" in src_url:
                is_fabricated = True
            elif any(f"fake" in src_url.lower() for _ in [1]):
                is_fabricated = True

        if is_fabricated:
            fabricated_urls.append((ref_id, title, src_url))

        # Check video vs image
        if vid_id:
            video_records.append((ref_id, title, vid_id, src_url, thumb))
        else:
            image_records.append((ref_id, title, src_url, thumb, creator, arch, loc))

    print(f"Total Video Records: {len(video_records)}")
    print(f"Total Image Records: {len(image_records)}")
    print(f"Records with Fabricated / Placeholder Source URLs: {len(fabricated_urls)}")
    for f in fabricated_urls:
        print(f"  ID {f[0]}: '{f[1]}' -> Fabricated Source: {f[2]}")

    print("\n--- DETAILED IMAGE RECORDS AUDIT ---")
    for r in image_records:
        ref_id, title, src_url, thumb, creator, arch, loc = r
        print(f"ID {ref_id}: {title}")
        print(f"   Platform: {src_url}")
        print(f"   Thumb: {thumb}")
        print(f"   Creator: {creator} | Architect: {arch} | Loc: {loc}")

if __name__ == "__main__":
    audit_feed_records()

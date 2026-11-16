import httpx
import sqlite3
import os

def check_wikimedia_metadata():
    print("=== 1. WIKIMEDIA COMMONS METADATA CHECK FOR CHETTINAD & OTHERS ===")
    files = [
        "File:Chettinad_house_courtyard.jpg",
        "File:Chettinadu_house©.jpg",
        "File:Nalukettu_House_of_Kunnappully_family.jpg",
        "File:Pillars_carved_out_of_same_rock_giving_a_look_of_gallery.jpg",
        "File:Carved_jharokhas,_Mehrangarh_Fort_palace,_Jodhpur.jpg",
        "File:Modern_residential_architecture_with_curved_design_and_exposed_brick_in_Mysore,_India.jpg",
    ]
    url = "https://commons.wikimedia.org/w/api.php"
    headers = {"User-Agent": "ArchitectAI/2.0 (research-audit@internal.local)"}

    for f in files:
        params = {
            "action": "query",
            "titles": f,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|size",
            "format": "json"
        }
        try:
            r = httpx.get(url, params=params, headers=headers, timeout=10.0)
            data = r.json().get("query", {}).get("pages", {})
            for pid, p in data.items():
                title = p.get("title")
                imageinfo = p.get("imageinfo", [{}])[0]
                img_url = imageinfo.get("url")
                desc_url = imageinfo.get("descriptionurl")
                meta = imageinfo.get("extmetadata", {})
                artist = meta.get("Artist", {}).get("value", "Unknown")
                license_name = meta.get("LicenseShortName", {}).get("value", "Unknown")
                desc = meta.get("ImageDescription", {}).get("value", "None")
                print(f"File: {title}")
                print(f"  Direct Image URL: {img_url}")
                print(f"  Source Page: {desc_url}")
                print(f"  Artist / Author: {artist}")
                print(f"  License: {license_name}")
                print(f"  Description: {desc[:150]}...")
                print("-" * 50)
        except Exception as e:
            print(f"Error checking {f}: {e}")

def check_youtube_videos():
    print("\n=== 2. YOUTUBE VIDEO AUDIT ===")
    conn = sqlite3.connect("architect_ai.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, video_embed_id, source_url, thumbnail_url, material_tags
        FROM architectural_references
        WHERE video_embed_id IS NOT NULL AND video_embed_id != ''
        ORDER BY id
    """)
    rows = cur.fetchall()
    print(f"Total video references in DB: {len(rows)}\n")

    for r in rows:
        ref_id, title, vid_id, src_url, thumb, tags = r
        # Test oEmbed endpoint on YouTube (official public API without key requirement)
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid_id}&format=json"
        try:
            resp = httpx.get(oembed_url, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                real_title = data.get("title")
                real_author = data.get("author_name")
                real_author_url = data.get("author_url")
                print(f"[ACTIVE] ID {ref_id} (vid: {vid_id}):")
                print(f"   DB Title:   '{title}'")
                print(f"   Real Title: '{real_title}'")
                print(f"   Channel:    '{real_author}' ({real_author_url})")
            elif resp.status_code in [401, 403]:
                print(f"[EMBED_RESTRICTED] ID {ref_id} (vid: {vid_id}): Status {resp.status_code}")
            elif resp.status_code == 404:
                print(f"[UNAVAILABLE/DELETED] ID {ref_id} (vid: {vid_id}): 404 Not Found")
            else:
                print(f"[STATUS {resp.status_code}] ID {ref_id} (vid: {vid_id})")
        except Exception as e:
            print(f"[ERROR] ID {ref_id} (vid: {vid_id}): {e}")

if __name__ == "__main__":
    check_wikimedia_metadata()
    check_youtube_videos()

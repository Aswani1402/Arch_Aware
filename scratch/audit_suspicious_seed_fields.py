import sqlite3
import re
from pathlib import Path

seed_path = Path("backend/seed_catalogue.sqlite")
conn = sqlite3.connect(f"file:{seed_path.as_posix()}?mode=ro", uri=True)
cur = conn.cursor()

# 1. Inspect manufacturers.unverified_notes & source_url
print("=== MANUFACTURERS: unverified_notes & source_url ===")
rows = cur.execute("SELECT id, name, unverified_notes, source_url FROM manufacturers").fetchall()
for r in rows:
    print(f"ID: {r[0]:2d} | Name: {r[1]:30} | Unverified Notes: {r[2]} | Source URL: {r[3]}")

# 2. Inspect reference_product_matches.evidence_notes
print("\n=== REFERENCE_PRODUCT_MATCHES: evidence_notes ===")
rows = cur.execute("SELECT id, reference_id, product_id, match_type, evidence_notes FROM reference_product_matches").fetchall()
for r in rows:
    print(f"ID: {r[0]} | Ref: {r[1]} | Prod: {r[2]} | Type: {r[3]} | Notes: {r[4]}")

# 3. Inspect architectural_references: description email_hits and whatsapp_hits
print("\n=== ARCHITECTURAL_REFERENCES: Suspicious Description Hits ===")
re_email = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
re_whatsapp = re.compile(r'wa\.me|whatsapp', re.IGNORECASE)
re_mobile = re.compile(r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b')

rows = cur.execute("SELECT id, title, source_platform, creator_name, description FROM architectural_references").fetchall()
email_matches = []
whatsapp_matches = []
mobile_matches = []

for r in rows:
    desc = r[4] or ""
    title = r[1] or ""
    text = f"{title} {desc}"
    
    em = re_email.findall(text)
    if em:
        email_matches.append((r[0], r[1], r[2], r[3], em))
    
    wm = re_whatsapp.findall(text)
    if wm:
        whatsapp_matches.append((r[0], r[1], r[2], r[3]))
        
    mm = re_mobile.findall(text)
    if mm:
        mobile_matches.append((r[0], r[1], r[2], r[3], len(mm)))

print(f"Total References with Email: {len(email_matches)}")
for em in email_matches:
    # Redact actual email string for reporting privacy
    redacted = [re.sub(r'(?<=.).(?=.*@)|(?<=@.).(?=.*\.)', '*', e) for e in em[4]]
    print(f"  Ref ID: {em[0]} | Platform: {em[2]} | Creator: {em[3]} | Emails found: {redacted}")

print(f"\nTotal References with WhatsApp mention: {len(whatsapp_matches)}")
for wm in whatsapp_matches[:5]:
    print(f"  Ref ID: {wm[0]} | Platform: {wm[2]} | Creator: {wm[3]} | Title: {wm[1][:50]}")

print(f"\nTotal References with 10-digit Mobile-like number: {len(mobile_matches)}")
for mm in mobile_matches[:5]:
    print(f"  Ref ID: {mm[0]} | Platform: {mm[2]} | Creator: {mm[3]} | Matches count: {mm[4]}")

conn.close()


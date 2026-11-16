import sqlite3
import re
from pathlib import Path

seed_path = Path("backend/seed_catalogue.sqlite")
conn = sqlite3.connect(f"file:{seed_path.as_posix()}?mode=ro", uri=True)
cur = conn.cursor()

# 1. Integrity
integrity = cur.execute("PRAGMA integrity_check;").fetchall()
quick = cur.execute("PRAGMA quick_check;").fetchall()
cur.execute("PRAGMA foreign_keys = ON;")
fk_check = cur.execute("PRAGMA foreign_key_check;").fetchall()
journal_mode = cur.execute("PRAGMA journal_mode;").fetchone()[0]

print("=== REGENERATED SEED PRAGMA CHECKS ===")
print("PRAGMA integrity_check:", integrity)
print("PRAGMA quick_check:", quick)
print("PRAGMA foreign_key_check violations count:", len(fk_check))
print("PRAGMA journal_mode:", journal_mode)

# 2. Table and row counts
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()]
print("\n=== REGENERATED SEED TABLE COUNTS ===")
print(f"Total tables: {len(tables)}")
expected_counts = {
    "catalogue_categories": 10,
    "catalogue_subcategories": 184,
    "catalogue_materials": 6319,
    "material_categories": 56,
    "manufacturers": 20,
    "architectural_references": 504,
    "products": 21,
    "reference_product_matches": 9,
}

all_counts_match = True
for t, exp in expected_counts.items():
    actual = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    match = actual == exp
    if not match:
        all_counts_match = False
    print(f"  {t:30}: actual={actual:5}, expected={exp:5} -> {'MATCH' if match else 'MISMATCH'}")

print(f"All expected counts match: {all_counts_match}")

# 3. Privacy scan on architectural_references
re_email = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
re_contact_prefix = re.compile(
    r'(?:for\s+enq(?:uiries)?|call/whatsapp|call/wa|call-whatsapp|whatsapp|call\s+at|call|ph(?:one)?|contact|inquiries?)[:\s-]+(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,5}\)?[\s-]?)?\d{3,5}[\s-]?\d{3,5}[\s-]?\d{3,5}\b',
    re.IGNORECASE,
)
re_standalone_mobile = re.compile(r'\b(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b')
re_intl_phone = re.compile(r'\b0\d{2,4}[\s-]?\d{3}[\s-]?\d{4}\b')
re_wa_url = re.compile(r'\b(?:https?://)?(?:wa\.me|api\.whatsapp\.com)/\S+\b', re.IGNORECASE)

refs = cur.execute("SELECT id, title, description FROM architectural_references").fetchall()

email_hits = []
prefix_hits = []
mobile_hits = []
intl_hits = []
wa_hits = []

for r in refs:
    text = f"{r[1]} {r[2]}"
    em = re_email.findall(text)
    if em:
        email_hits.append((r[0], em))
    cp = re_contact_prefix.findall(text)
    if cp:
        prefix_hits.append((r[0], cp))
    wa = re_wa_url.findall(text)
    if wa:
        wa_hits.append((r[0], wa))
    
    # Standalone mobile (filter dimensions)
    mob = re_standalone_mobile.findall(text)
    for m in mob:
        # Check if dimension or measurement
        idx = text.find(m)
        after = text[idx+len(m):idx+len(m)+15].lower()
        before = text[max(0, idx-15):idx].lower()
        if not re.search(r'^\s*(?:mm|cm|m|ft|in|inch|sqft|sq\.?\s*ft|sqm|sq\s*m)\b', after) and not (re.search(r'^\s*[xX*]\s*\d+', after) or re.search(r'\d+\s*[xX*]\s*$', before)):
            mobile_hits.append((r[0], m))
            
    intl = re_intl_phone.findall(text)
    for m in intl:
        idx = text.find(m)
        after = text[idx+len(m):idx+len(m)+15].lower()
        before = text[max(0, idx-15):idx].lower()
        if not re.search(r'^\s*(?:mm|cm|m|ft|in|inch|sqft|sq\.?\s*ft|sqm|sq\s*m)\b', after) and not (re.search(r'^\s*[xX*]\s*\d+', after) or re.search(r'\d+\s*[xX*]\s*$', before)):
            intl_hits.append((r[0], m))

print("\n=== REGENERATED SEED PRIVACY SCAN ON ARCHITECTURAL_REFERENCES ===")
print(f"Remaining Email hits       : {len(email_hits)}")
print(f"Remaining Contact Prefix   : {len(prefix_hits)}")
print(f"Remaining WhatsApp URLs    : {len(wa_hits)}")
print(f"Remaining Standalone Mobile: {len(mobile_hits)}")
print(f"Remaining Intl Phone hits  : {len(intl_hits)}")

if email_hits:
    print("  Emails found in refs:", [e[0] for e in email_hits])
if prefix_hits:
    print("  Prefixes found in refs:", [p[0] for p in prefix_hits])
if mobile_hits:
    print("  Mobiles found in refs:", [m[0] for m in mobile_hits])
if intl_hits:
    print("  Intl phones found in refs:", [i[0] for i in intl_hits])

conn.close()


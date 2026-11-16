import sqlite3
import re

conn = sqlite3.connect("file:backend/architect_ai.db?mode=ro", uri=True)
cur = conn.cursor()

rows = cur.execute("SELECT id, title, description, creator_name, source_platform, source_url FROM architectural_references ORDER BY id ASC").fetchall()

# Regexes
re_email = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')

# Genuine Indian / International mobile & phone numbers in contact context
# e.g., "call 9876543210", "+91 9876543210", "WhatsApp: 98765 43210", "8089616...", "Ph: ..."
re_contact_patterns = [
    # Explicit contact phrases like "call/whatsapp 1234567890", "call: 12345...", "whatsapp: 12345..."
    re.compile(r'(?:call(?:/whatsapp|/wa)?|whatsapp|ph(?:one)?|contact|inquiries?)[:\s]+(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b', re.IGNORECASE),
    re.compile(r'\b(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b'),
    re.compile(r'\b(?:wa\.me/\d+|api\.whatsapp\.com/\S+)\b', re.IGNORECASE),
]

# Patterns for false positives (architectural dimensions, years, etc.)
re_dims = re.compile(r'\b\d+(?:\.\d+)?\s*(?:x|X|\*)\s*\d+(?:\.\d+)?(?:\s*(?:x|X|\*)\s*\d+(?:\.\d+)?)?\s*(?:mm|cm|m|in|inch|ft|feet|sqft|sq\.ft)?\b')
re_sqft = re.compile(r'\b\d{3,5}\s*(?:sq\.?\s*ft|sqft|sqm|sq\.?\s*m|square\s+feet)\b', re.IGNORECASE)
re_year = re.compile(r'\b(?:19|20)\d{2}\b')

detected_contacts = []

for r in rows:
    ref_id = r[0]
    title = r[1] or ""
    desc = r[2] or ""
    creator = r[3] or ""
    platform = r[4] or ""

    # Check for emails
    title_emails = re_email.findall(title)
    desc_emails = re_email.findall(desc)

    # Check for phones/whatsapp
    title_phones = []
    desc_phones = []

    # Check for explicit phrases or standalone 10-digit mobile numbers starting with 6-9
    for p in re_contact_patterns:
        for m in p.finditer(title):
            match_str = m.group(0)
            if not re_dims.match(match_str) and not re_sqft.match(match_str) and not re_year.match(match_str):
                title_phones.append((m.start(), m.end(), match_str))
        for m in p.finditer(desc):
            match_str = m.group(0)
            if not re_dims.match(match_str) and not re_sqft.match(match_str) and not re_year.match(match_str):
                desc_phones.append((m.start(), m.end(), match_str))

    # De-duplicate spans
    def dedupe_spans(spans):
        sorted_spans = sorted(spans, key=lambda x: (x[0], -x[1]))
        res = []
        for s in sorted_spans:
            if not res or s[0] >= res[-1][1]:
                res.append(s)
        return res

    title_phones = dedupe_spans(title_phones)
    desc_phones = dedupe_spans(desc_phones)

    if title_emails or desc_emails or title_phones or desc_phones:
        detected_contacts.append({
            "id": ref_id,
            "platform": platform,
            "creator": creator,
            "title": title,
            "desc": desc,
            "title_emails": len(title_emails),
            "desc_emails": len(desc_emails),
            "title_phones": len(title_phones),
            "desc_phones": len(desc_phones),
            "title_phone_matches": [m[2] for m in title_phones],
            "desc_phone_matches": [m[2] for m in desc_phones],
        })

conn.close()

print(f"Total references inspected: {len(rows)}")
print(f"Total references with detected contact patterns: {len(detected_contacts)}")
print("\n=== RECORD AUDIT SUMMARY (Privacy-Masked) ===")
for item in detected_contacts:
    print(f"Ref ID: {item['id']:3d} | Platform: {item['platform']:10} | Creator: {item['creator'][:25]:25}")
    print(f"  Title Email count: {item['title_emails']}, Desc Email count: {item['desc_emails']}")
    print(f"  Title Phone count: {item['title_phones']}, Desc Phone count: {item['desc_phones']}")
    # print pattern shape without revealing actual phone numbers
    masked_tp = [re.sub(r'\d', 'X', m) for m in item['title_phone_matches']]
    masked_dp = [re.sub(r'\d', 'X', m) for m in item['desc_phone_matches']]
    if masked_tp:
        print(f"  Title Phone patterns: {masked_tp}")
    if masked_dp:
        print(f"  Desc Phone patterns: {masked_dp}")


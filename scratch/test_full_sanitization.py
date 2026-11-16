import sqlite3
import re

re_email = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')

re_contact_prefix = re.compile(
    r'(?:for\s+enq(?:uiries)?|call/whatsapp|call/wa|whatsapp|call\s+at|call|ph(?:one)?|contact|inquiries?)[:\s-]+(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,5}\)?[\s-]?)?\d{3,5}[\s-]?\d{4,5}\b',
    re.IGNORECASE
)

re_standalone_mobile = re.compile(r'\b(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b')
re_wa_url = re.compile(r'\b(?:https?://)?(?:wa\.me|api\.whatsapp\.com)/\S+\b', re.IGNORECASE)

def sanitize_reference_text(text: str) -> str:
    if not text:
        return text
    
    # 1. Remove emails
    cleaned = re_email.sub("", text)
    
    # 2. Remove whatsapp URLs
    cleaned = re_wa_url.sub("", cleaned)
    
    # 3. Remove contact prefix phrases
    cleaned = re_contact_prefix.sub("", cleaned)
    
    # 4. Remove standalone mobile numbers
    def mobile_repl(match):
        s = match.string
        start = match.start()
        end = match.end()
        before = s[max(0, start-15):start].lower()
        after = s[end:min(len(s), end+15)].lower()
        # Preserve dimensions and measurement units
        if re.search(r'^\s*(?:mm|cm|m|ft|in|inch|sqft|sq\.?\s*ft|sqm|sq\s*m)\b', after):
            return match.group(0)
        if re.search(r'^\s*[xX*]\s*\d+', after) or re.search(r'\d+\s*[xX*]\s*$', before):
            return match.group(0)
        return ""

    cleaned = re_standalone_mobile.sub(mobile_repl, cleaned)
    
    # Clean up artifacts left behind
    cleaned = re.sub(r'\bCall at\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\bFor Enq\s*:-?\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'[\s|/,-]+$', '', cleaned) # trailing punctuation
    cleaned = re.sub(r'^\s*[\s|/,-]+', '', cleaned) # leading punctuation
    cleaned = re.sub(r'\s*\|\s*\|', ' |', cleaned) # double pipes
    cleaned = re.sub(r'\s{2,}', ' ', cleaned) # multiple spaces
    cleaned = re.sub(r'\s+([.,;:!?])', r'\1', cleaned) # space before punctuation
    return cleaned.strip()

conn = sqlite3.connect("file:backend/architect_ai.db?mode=ro", uri=True)
cur = conn.cursor()
rows = cur.execute("SELECT id, title, description FROM architectural_references").fetchall()

modified_records = []
dimension_check_passed = True

for r in rows:
    ref_id = r[0]
    orig_t = r[1] or ""
    orig_d = r[2] or ""
    san_t = sanitize_reference_text(orig_t)
    san_d = sanitize_reference_text(orig_d)
    
    if orig_t != san_t or orig_d != san_d:
        modified_records.append((ref_id, orig_t != san_t, orig_d != san_d))
    
    # Verify dimensions are preserved (e.g. 600x450 or mm or sqft)
    for sample in ["600x450", "300x300", "2400 sq.ft", "5 Marla", "GL28h", "M35", "M30"]:
        if sample in orig_t and sample not in san_t:
            print(f"ERROR: Dimension {sample} removed from title of Ref {ref_id}!")
            dimension_check_passed = False
        if sample in orig_d and sample not in san_d:
            print(f"ERROR: Dimension {sample} removed from desc of Ref {ref_id}!")
            dimension_check_passed = False

print(f"Total modified records: {len(modified_records)}")
print(f"Modified record IDs: {[r[0] for r in modified_records]}")
print(f"Dimension check passed: {dimension_check_passed}")

conn.close()


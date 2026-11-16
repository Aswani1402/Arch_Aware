import sqlite3
import re

re_email = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
re_contact_prefix = re.compile(
    r'(?:for\s+enq(?:uiries)?|call/whatsapp|call/wa|call-whatsapp|whatsapp|call\s+at|call|ph(?:one)?|contact|inquiries?)[:\s-]+(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,5}\)?[\s-]?)?\d{3,5}[\s-]?\d{3,5}[\s-]?\d{3,5}\b',
    re.IGNORECASE
)
re_standalone_mobile = re.compile(r'\b(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b')
re_intl_phone = re.compile(r'\b0\d{2,4}[\s-]?\d{3}[\s-]?\d{4}\b')
re_wa_url = re.compile(r'\b(?:https?://)?(?:wa\.me|api\.whatsapp\.com)/\S+\b', re.IGNORECASE)

def sanitize_reference_text(text: str, fallback_title: str = "") -> str:
    if not text:
        return text
    
    # Check if contact pattern exists
    if not (re_email.search(text) or re_contact_prefix.search(text) or re_standalone_mobile.search(text) or re_intl_phone.search(text) or re_wa_url.search(text)):
        return text
    
    cleaned = text
    cleaned = re_email.sub("", cleaned)
    cleaned = re_wa_url.sub("", cleaned)
    cleaned = re_contact_prefix.sub("", cleaned)
    
    def mobile_repl(match):
        s = match.string
        start = match.start()
        end = match.end()
        before = s[max(0, start-15):start].lower()
        after = s[end:min(len(s), end+15)].lower()
        if re.search(r'^\s*(?:mm|cm|m|ft|in|inch|sqft|sq\.?\s*ft|sqm|sq\s*m)\b', after):
            return match.group(0)
        if re.search(r'^\s*[xX*]\s*\d+', after) or re.search(r'\d+\s*[xX*]\s*$', before):
            return match.group(0)
        return ""

    cleaned = re_standalone_mobile.sub(mobile_repl, cleaned)
    cleaned = re_intl_phone.sub(mobile_repl, cleaned)
    
    cleaned = re.sub(r'\b(?:call/whatsapp|call/wa|call-whatsapp|call at|call|whatsapp|for enq\s*:-?)\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'[\s|/,-]+$', '', cleaned)
    cleaned = re.sub(r'^\s*[\s|/,-]+', '', cleaned)
    cleaned = re.sub(r'\s*\|\s*\|', ' |', cleaned)
    cleaned = re.sub(r'\s{2,}', ' ', cleaned)
    cleaned = re.sub(r'\s+([.,;:!?])', r'\1', cleaned).strip()

    if not cleaned and fallback_title:
        cleaned = fallback_title

    return cleaned

conn = sqlite3.connect("file:backend/architect_ai.db?mode=ro", uri=True)
cur = conn.cursor()

ids = [96, 111, 153, 158, 238, 244, 306, 317, 318, 326, 327, 433, 437, 440, 442, 447, 458, 489]

for rid in ids:
    row = cur.execute("SELECT id, title, description FROM architectural_references WHERE id=?", (rid,)).fetchone()
    st = sanitize_reference_text(row[1], fallback_title="Natural Marble & Granite Works")
    sd = sanitize_reference_text(row[2])
    print(f"Ref {rid:3d}:")
    print(f"  Title: {st}")
    print(f"  Desc : {sd[:80]}...")

conn.close()


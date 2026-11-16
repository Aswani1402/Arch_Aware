import sqlite3
import re

# Comprehensive, conservative regex for contact sanitization
re_email = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')

# Explicit call/whatsapp/contact phrases
re_contact_prefix = re.compile(
    r'(?:call/whatsapp|call/wa|whatsapp|call|ph(?:one)?|contact|inquiries?)[:\s]+(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,5}\)?[\s-]?)?\d{3,5}[\s-]?\d{4,5}\b',
    re.IGNORECASE
)

# Standalone mobile numbers (+91 or standard 10-digit starting with 6-9)
re_standalone_mobile = re.compile(r'\b(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b')

# WhatsApp URLs
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
    # Ensure not part of dimension (e.g. not preceded/followed by x, mm, sqft)
    def mobile_repl(match):
        start = match.start()
        end = match.end()
        # Look at surrounding characters in original cleaned text
        before = cleaned[max(0, start-10):start].lower()
        after = cleaned[end:min(len(cleaned), end+10)].lower()
        # If part of measurement or dimension, do not replace
        if any(unit in after for unit in ['mm', 'cm', 'sqft', 'sq.ft', 'sqm', 'sq m', 'feet', 'inch']):
            return match.group(0)
        if any(symbol in before for symbol in ['x', '*', 'by ']) or any(symbol in after for symbol in ['x', '*', ' by']):
            return match.group(0)
        return ""

    cleaned = re_standalone_mobile.sub(mobile_repl, cleaned)
    
    # 5. Clean up awkward punctuation/spacing left behind:
    cleaned = re.sub(r'[\s|/,-]+$', '', cleaned) # trailing punctuation
    cleaned = re.sub(r'\s*\|\s*\|', ' |', cleaned) # double pipes
    cleaned = re.sub(r'\s{2,}', ' ', cleaned) # multiple spaces
    cleaned = re.sub(r'\s+([.,;:!?])', r'\1', cleaned) # space before punctuation
    return cleaned.strip()


conn = sqlite3.connect("file:backend/architect_ai.db?mode=ro", uri=True)
cur = conn.cursor()

ids_to_check = [153, 158, 238, 244, 306, 317, 318, 326, 327, 437, 440, 442, 447, 458, 489]

print("=== TESTING REFERENCE SANITIZATION ON AFFECTED RECORDS ===")
for ref_id in ids_to_check:
    row = cur.execute("SELECT id, title, description FROM architectural_references WHERE id=?", (ref_id,)).fetchone()
    orig_title = row[1] or ""
    orig_desc = row[2] or ""
    san_title = sanitize_reference_text(orig_title)
    san_desc = sanitize_reference_text(orig_desc)
    
    # Check if contact patterns remain
    rem_email = re_email.findall(san_title + " " + san_desc)
    rem_prefix = re_contact_prefix.findall(san_title + " " + san_desc)
    rem_mobile = re_standalone_mobile.findall(san_title + " " + san_desc)
    
    # Filter out false positives in remaining mobile
    rem_mobile = [m for m in rem_mobile if not any(unit in (san_title + " " + san_desc).lower() for unit in ['sqft', 'mm', 'sq.ft'])]
    
    status = "CLEAN" if not rem_email and not rem_prefix and not rem_mobile else "FLAGGED"
    print(f"\nRef ID {ref_id:3d} [{status}]:")
    print(f"  Orig Title: {orig_title}")
    print(f"  San  Title: {san_title}")
    print(f"  Orig Desc : {orig_desc[:90]}...")
    print(f"  San  Desc : {san_desc[:90]}...")
    if status == "FLAGGED":
        print(f"  REMAINING: email={rem_email}, prefix={rem_prefix}, mobile={rem_mobile}")

conn.close()


import re

# Comprehensive Sanitizer Regexes

# 1. Emails (optionally preceded by "Email:", "E-mail:", etc.)
RE_EMAIL_WITH_LABEL = re.compile(
    r'(?i)(?:email|e-mail|mail)[:\s-]*[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
)
RE_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')

# 2. WhatsApp URLs (optionally preceded by "WhatsApp:", "Contact:", etc.)
RE_WA_URL = re.compile(
    r'(?i)(?:(?:contact|whatsapp|wa|chat)[:\s-]*)?(?:https?://)?(?:wa\.me|api\.whatsapp\.com)/\S+\b'
)

# 3. Contact prompts WITH numbers attached
# Matches: Call/WhatsApp: +91 80896 12345, Call: 9123325954, For enquiries: +91 98765 43210, Ph: 0484-2345678
RE_CONTACT_PROMPT_WITH_NUMBER = re.compile(
    r'(?i)(?:📞|☎️|📱|✉️|📧)?\s*'
    r'\b(?:call\s*(?:/\s*whatsapp|/\s*wa|-\s*whatsapp)?|whatsapp|call\s+at|phone|ph|contact(?:\s+us)?|inquiries|enquiries|for\s+(?:booking\s+)?(?:enquiries|inquiries)|email\s+for\s+(?:enquiries|inquiries))\b'
    r'(?:\s+for\s+details)?'
    r'[:\s-]*'
    r'(?:(?:\+|00)?\d{1,3}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{3,5}(?:[\s.-]?\d{3,5})?\b'
)

# 4. Standalone contact prompts WITHOUT numbers (e.g., Call for details, WhatsApp for enquiries, Contact us)
RE_STANDALONE_PROMPTS = re.compile(
    r'(?i)(?:📞|☎️|📱|✉️|📧)?\s*'
    r'\b(?:call\s+for\s+details|whatsapp\s+for\s+(?:enquiries|inquiries)|contact\s+us|for\s+booking\s+(?:enquiries|inquiries)|email\s+for\s+(?:enquiries|inquiries)|for\s+(?:enquiries|inquiries)|call\s*(?:/\s*whatsapp|/\s*wa|-\s*whatsapp)|call\s+at)\b[:\s-]*'
)

# 5. International numbers:
# +1 (US/Canada): +1 212 555 0199, +1-212-555-0199, +1 (212) 555-0199
RE_US_PHONE = re.compile(r'(?:^|(?<=[\s|/,-]))(?:\+1[\s.-]?)?\(?[2-9]\d{2}\)?[\s.-]?[2-9]\d{2}[\s.-]?\d{4}\b')

# +44 (UK): +44 7911 123456, +44 20 7946 0919
RE_UK_PHONE = re.compile(r'(?:^|(?<=[\s|/,-]))(?:\+44[\s.-]?)(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}\b')

# General international with leading 0: 0330 702 9992, 0312 0702901, 0484-2345678
RE_INTL_PHONE = re.compile(r'\b0\d{2,4}[\s-]?\d{3}[\s-]?\d{4}\b')

# Indian mobile numbers: +91 98471 23456, +91-98471-23456, 9847123456
RE_INDIAN_MOBILE = re.compile(r'(?:^|(?<=[\s|/,-]))(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b')


def sanitize_reference_text(text: str, fallback_title: str = "") -> str:
    """
    Conservatively sanitizes contact information from text fields while strictly preserving
    architectural dimensions, square footage, measurements, and specifications.
    """
    if not text:
        return text

    # Pre-check for any contact indicators
    has_contact = (
        RE_EMAIL.search(text)
        or RE_WA_URL.search(text)
        or RE_CONTACT_PROMPT_WITH_NUMBER.search(text)
        or RE_STANDALONE_PROMPTS.search(text)
        or RE_INDIAN_MOBILE.search(text)
        or RE_US_PHONE.search(text)
        or RE_UK_PHONE.search(text)
        or RE_INTL_PHONE.search(text)
        or any(icon in text for icon in ("📞", "☎️", "📱", "✉️", "📧"))
    )
    if not has_contact:
        return text

    cleaned = text

    # 1. Strip URLs & Emails (including optional labels like "Email:")
    cleaned = RE_EMAIL_WITH_LABEL.sub(" ", cleaned)
    cleaned = RE_EMAIL.sub(" ", cleaned)
    cleaned = RE_WA_URL.sub(" ", cleaned)

    # 2. Strip prompts with numbers attached
    cleaned = RE_CONTACT_PROMPT_WITH_NUMBER.sub(" ", cleaned)

    # 3. Helper for phone replacements with context-aware dimension guarding
    def dimension_guard(match):
        s = match.string
        start = match.start()
        end = match.end()
        before = s[max(0, start - 15) : start].lower()
        after = s[end : min(len(s), end + 15)].lower()

        matched_str = match.group(0).strip()
        digits = re.sub(r'\D', '', matched_str)

        # Context-aware unit check:
        # If the number has 8+ digits (e.g. 9847123456), it CANNOT be an architectural meter dimension!
        # (10 billion meters is ~25x the distance to the moon; no room or beam is 10 digits in meters).
        # Legitimate dimensions with 'm' (meters) are short numbers (e.g. 14m, 2.5m, 100m).
        if len(digits) >= 8:
            # 8+ digits: only preserve if explicitly in an unambiguous dimensional multiplication (e.g. 600x450x1200)
            if re.search(r'^\s*[xX*]\s*\d+', after) or re.search(r'\d+\s*[xX*]\s*$', before):
                return match.group(0)
            return " "

        # For smaller numbers (< 8 digits), protect dimensional units
        if re.search(r'^\s*(?:mm|cm|m\b|ft|in|inch|sqft|sq\.?\s*ft|sqm|sq\s*m)\b', after):
            return match.group(0)
        if re.search(r'^\s*[xX*]\s*\d+', after) or re.search(r'\d+\s*[xX*]\s*$', before):
            return match.group(0)

        return " "

    # 4. Strip Indian Mobiles
    cleaned = RE_INDIAN_MOBILE.sub(dimension_guard, cleaned)

    # 5. Strip US, UK, and International phones
    cleaned = RE_US_PHONE.sub(dimension_guard, cleaned)
    cleaned = RE_UK_PHONE.sub(dimension_guard, cleaned)
    cleaned = RE_INTL_PHONE.sub(dimension_guard, cleaned)

    # 6. Strip standalone contact prompts (e.g. "Call for details", "WhatsApp for enquiries", "Contact us")
    cleaned = RE_STANDALONE_PROMPTS.sub(" ", cleaned)

    # 7. Clean contact icons and remnant artifacts
    cleaned = re.sub(r'[📞☎️📱✉️📧]', ' ', cleaned)
    cleaned = re.sub(r'\b(?:call/whatsapp|call/wa|call-whatsapp|call at|for enq\s*:-?)\b', ' ', cleaned, flags=re.IGNORECASE)

    # 8. Clean redundant separators and punctuation
    cleaned = re.sub(r'(?:[\s|/,-]+\|)+', ' |', cleaned)
    cleaned = re.sub(r'\s*\|\s*\|', ' |', cleaned)
    cleaned = re.sub(r'\|\s*\|', '|', cleaned)
    cleaned = re.sub(r'\|\s*,', '|', cleaned)
    cleaned = re.sub(r':\s*\+', '', cleaned)
    cleaned = re.sub(r'\s*:\s*$', '', cleaned)
    # Pull trailing punctuation to previous word, then deduplicate dots
    cleaned = re.sub(r'\s+([.,;:!?])', r'\1', cleaned)
    cleaned = re.sub(r'\.{2,}', '.', cleaned)
    cleaned = re.sub(r'[\s|/,-]+$', '', cleaned)
    cleaned = re.sub(r'^\s*[\s|/,-]+', '', cleaned)
    cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip()

    if not cleaned and fallback_title:
        cleaned = fallback_title

    return cleaned

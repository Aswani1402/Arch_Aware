import re
import sys
from pathlib import Path

# Add repo root to sys.path to import sanitize_reference_text
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.create_sanitized_seed import (
    sanitize_reference_text,
    RE_EMAIL,
    RE_CONTACT_PREFIX,
    RE_STANDALONE_MOBILE,
    RE_INTL_PHONE,
    RE_WA_URL,
)

test_cases = [
    # 1. Standard Indian Mobiles & WhatsApp
    ("Standard 10-digit mobile", "Villa design in Kochi. Call 9847123456 for details.", "Villa design in Kochi. for details."),
    ("Formatted +91 mobile", "Contemporary Residence | +91 98471-23456 | Kerala", "Contemporary Residence | | Kerala"),
    ("wa.me link", "Penthouse interior https://wa.me/919847123456 modern look", "Penthouse interior modern look"),
    ("api.whatsapp link", "Contact https://api.whatsapp.com/send?phone=919847123456", ""),
    
    # 2. Studio Email
    ("Sales email", "Minimalist facade design. Email: sales@archstudio.com for plans", "Minimalist facade design. Email: for plans"),
    
    # 3. Contact prefixes
    ("Call/WhatsApp prefix with number", "Tropical Courtyard Home Call/WhatsApp: +91 80896 12345", "Tropical Courtyard Home"),
    ("For inquiries prefix", "Luxury Villa for enquiries: +91 98765 43210 Ark Architecture", "Luxury Villa Ark Architecture"),

    # 4. Legitimate Architectural Dimensions (Should be 100% PRESERVED)
    ("Tile Dimensions mm", "Statuario porcelain slabs 1200x2400 mm for lobby flooring", "Statuario porcelain slabs 1200x2400 mm for lobby flooring"),
    ("Area sq.ft", "Spacious 2400 sq.ft duplex residential plan", "Spacious 2400 sq.ft duplex residential plan"),
    ("Plot size Marla", "5 Marla Spanish elevation design in Lahore", "5 Marla Spanish elevation design in Lahore"),
    ("Beam grade GL28h", "Glulam structural beams grade GL28h spanning 14m", "Glulam structural beams grade GL28h spanning 14m"),
    ("Concrete grade M35", "High strength M35 grade reinforced concrete columns", "High strength M35 grade reinforced concrete columns"),
    ("Thickness mm", "8mm toughened safety glass railing", "8mm toughened safety glass railing"),

    # 5. Potential Edge Cases / False Positives / False Negatives
    ("Mobile followed by 'm'", "Site office 9847123456 m from main junction", "EXPECT_FALSE_NEGATIVE"),
    ("Mobile followed by 'sqm'", "Direct inquiry 9847123456 sqm plot", "EXPECT_FALSE_NEGATIVE"),
    ("International UK number", "London studio inquiries +44 7911 123456 project details", "EXPECT_FALSE_NEGATIVE"),
    ("US 10-digit number (starts with 2-5)", "New York showroom +1 212 555 0199 call now", "EXPECT_FALSE_NEGATIVE"),
    ("Prompt without number", "For inquiries contact our studio on Instagram @arkstudio", "For inquiries contact our studio on Instagram @arkstudio"),
    ("Landline without leading 0", "Kochi office 0484-2345678 ext 102", "EXPECT_PASS_OR_PARTIAL"),
]

print("=== SANITIZER TEST EVALUATION ===")
for name, input_text, expected in test_cases:
    output = sanitize_reference_text(input_text, fallback_title="Fallback Title")
    print(f"\n--- Test: {name} ---")
    print(f"INPUT:    {input_text}")
    print(f"OUTPUT:   {output}")
    if expected.startswith("EXPECT_"):
        print(f"ANALYSIS: Edge case category: {expected}")
    else:
        status = "MATCH" if output == expected else "DIFFER"
        print(f"EXPECTED: {expected}")
        print(f"STATUS:   {status}")


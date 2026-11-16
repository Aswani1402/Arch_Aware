from prototype_sanitizer import sanitize_reference_text

test_cases = [
    # Required Section A Cases:
    ("Case A.1: Call/WhatsApp prefix with number",
     "Tropical Courtyard Home Call/WhatsApp: +91 80896 12345",
     "Tropical Courtyard Home"),
    
    ("Case A.2: Separator cleanup with +91 number",
     "Residence | +91 98471-23456 | Kerala",
     "Residence | Kerala"),
    
    ("Case A.3: International US phone format",
     "New York showroom +1 212 555 0199 call now",
     "New York showroom call now"),
    
    ("Case A.4: 10-digit mobile followed by 'm'",
     "Site office 9847123456 m from main junction",
     "Site office m from main junction"),
    
    ("Case A.5a: Standalone prompt: Call for details",
     "Modern duplex penthouse. Call for details.",
     "Modern duplex penthouse."),
    
    ("Case A.5b: Standalone prompt: WhatsApp for enquiries",
     "Contemporary villa architecture. WhatsApp for enquiries.",
     "Contemporary villa architecture."),
    
    ("Case A.5c: Standalone prompt: Contact us",
     "Luxury residential interior design. Contact us today.",
     "Luxury residential interior design. today."),
    
    ("Case A.5d: Standalone prompt: For booking enquiries",
     "Beachfront residence design. For booking enquiries.",
     "Beachfront residence design."),
    
    ("Case A.5e: Standalone prompt: Email for enquiries",
     "Sustainable timber pavilion. Email for enquiries.",
     "Sustainable timber pavilion."),

    # Required Section B Cases:
    ("Section B: Indian mobile without country code",
     "Minimalist living room. 9847123456 Sadia Shaheen",
     "Minimalist living room. Sadia Shaheen"),
    
    ("Section B: Hyphenated Indian mobile",
     "Luxury master bedroom | 91-98737-79876 | Gurugram",
     "Luxury master bedroom | Gurugram"),
    
    ("Section B: Space-separated Indian mobile",
     "Interior design flat | 91 92474 49165 | Hyderabad",
     "Interior design flat | Hyderabad"),
    
    ("Section B: International UK number (+44)",
     "London studio inquiries +44 7911 123456 project details",
     "London studio project details"),
    
    ("Section B: WhatsApp wa.me URL",
     "Penthouse interior https://wa.me/919847123456 modern look",
     "Penthouse interior modern look"),
    
    ("Section B: WhatsApp api.whatsapp.com URL",
     "Contact https://api.whatsapp.com/send?phone=919847123456 modern look",
     "modern look"),
    
    ("Section B: Studio email address",
     "Minimalist facade design. Email: sales@archstudio.com for plans",
     "Minimalist facade design. for plans"),

    # Legitimate Architectural Specifications (MUST NOT BE REMOVED):
    ("Preserve: 600x450mm",
     "Rectified ceramic wall tile 600x450mm polished finish",
     "Rectified ceramic wall tile 600x450mm polished finish"),
    
    ("Preserve: 1200x2400 mm",
     "Statuario porcelain slabs 1200x2400 mm for lobby flooring",
     "Statuario porcelain slabs 1200x2400 mm for lobby flooring"),
    
    ("Preserve: 2400 sq.ft",
     "Spacious 2400 sq.ft duplex residential plan in Bangalore",
     "Spacious 2400 sq.ft duplex residential plan in Bangalore"),
    
    ("Preserve: 5 Marla",
     "5 Marla Spanish elevation design in DHA Lahore",
     "5 Marla Spanish elevation design in DHA Lahore"),
    
    ("Preserve: GL28h",
     "Glulam structural beams grade GL28h spanning 14m",
     "Glulam structural beams grade GL28h spanning 14m"),
    
    ("Preserve: M35",
     "High strength M35 grade reinforced concrete columns",
     "High strength M35 grade reinforced concrete columns"),
    
    ("Preserve: 8mm glass",
     "8mm toughened safety glass railing with stainless fittings",
     "8mm toughened safety glass railing with stainless fittings"),
    
    ("Preserve: 14m beam span",
     "Timber roof pavilion with 14m beam span across courtyard",
     "Timber roof pavilion with 14m beam span across courtyard"),
    
    ("Preserve: Ordinary text containing modern, minimalist, materials",
     "Modern minimalist villa featuring sustainable materials and open courtyards",
     "Modern minimalist villa featuring sustainable materials and open courtyards"),
]

print("=== TESTING PROTOTYPE SANITIZER ===")
failures = 0
for name, inp, expected in test_cases:
    out = sanitize_reference_text(inp, fallback_title="Architectural Reference")
    # Clean whitespace for comparison
    out_clean = " ".join(out.split())
    exp_clean = " ".join(expected.split())
    if out_clean == exp_clean:
        print(f"PASS: {name}")
    else:
        print(f"FAIL: {name}")
        print(f"  INPUT:    {inp}")
        print(f"  OUTPUT:   {out_clean}")
        print(f"  EXPECTED: {exp_clean}")
        failures += 1

print(f"\nTotal: {len(test_cases)} tests | Failures: {failures}")


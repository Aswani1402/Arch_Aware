"""
NIVORA — Phase 1.3.4 Comprehensive Contact Sanitizer Regression Test Suite
Validates:
1. Contact scrubbing (Indian mobiles with/without +91, hyphenated, space-separated, US +1, UK +44, WhatsApp URLs, emails, prompts)
2. Architectural specifications preservation (600x450mm, 1200x2400 mm, 2400 sq.ft, 5 Marla, GL28h, M35, 8mm glass, 14m beam span)
3. Ordinary vocabulary preservation (modern, minimalist, materials)
4. Context-aware unit detection vs 10-digit false negatives
5. Isolated temporary database test fixture (never touches production development DB)
"""

import sqlite3
import tempfile
import shutil
from pathlib import Path
import pytest

from scripts.create_sanitized_seed import sanitize_reference_text


# ==============================================================================
# 1. CONTACT REMOVAL REGRESSIONS (FALSE NEGATIVE GUARDS)
# ==============================================================================

def test_indian_mobile_with_plus_91_and_separator_cleanup():
    inp = "Tropical Courtyard Home Call/WhatsApp: +91 80896 12345"
    out = sanitize_reference_text(inp)
    assert out == "Tropical Courtyard Home"
    assert "+91" not in out
    assert "80896" not in out
    assert "Call/WhatsApp" not in out
    assert not out.endswith(":")
    assert not out.endswith("+")


def test_indian_mobile_formatted_separators():
    inp = "Residence | +91 98471-23456 | Kerala"
    out = sanitize_reference_text(inp)
    assert out == "Residence | Kerala"
    assert "+91" not in out
    assert "98471" not in out
    assert "| |" not in out


def test_indian_mobile_without_country_code():
    inp = "Minimalist living room. 9847123456 Sadia Shaheen"
    out = sanitize_reference_text(inp)
    assert "9847123456" not in out
    assert "Sadia Shaheen" in out


def test_hyphenated_and_space_separated_numbers():
    inp1 = "Luxury master bedroom | 91-98737-79876 | Gurugram"
    out1 = sanitize_reference_text(inp1)
    assert "98737" not in out1
    assert out1 == "Luxury master bedroom | Gurugram"

    inp2 = "Interior design flat | 91 92474 49165 | Hyderabad"
    out2 = sanitize_reference_text(inp2)
    assert "92474" not in out2
    assert out2 == "Interior design flat | Hyderabad"

    inp3 = "DHA Lahore | 0330 702 9992 | Town"
    out3 = sanitize_reference_text(inp3)
    assert "0330" not in out3
    assert out3 == "DHA Lahore | Town"


def test_international_numbers_us_and_uk():
    # US +1 format
    inp_us = "New York showroom +1 212 555 0199 call now"
    out_us = sanitize_reference_text(inp_us)
    assert "+1" not in out_us
    assert "212 555 0199" not in out_us
    assert "New York showroom" in out_us

    # UK +44 format
    inp_uk = "London studio inquiries +44 7911 123456 project details"
    out_uk = sanitize_reference_text(inp_uk)
    assert "+44" not in out_uk
    assert "7911 123456" not in out_uk
    assert "London studio" in out_uk
    assert "project details" in out_uk


def test_whatsapp_urls():
    inp1 = "Penthouse interior https://wa.me/919847123456 modern look"
    out1 = sanitize_reference_text(inp1)
    assert "wa.me" not in out1
    assert "919847123456" not in out1
    assert "Penthouse interior modern look" in out1

    inp2 = "Contact https://api.whatsapp.com/send?phone=919847123456 modern look"
    out2 = sanitize_reference_text(inp2)
    assert "whatsapp.com" not in out2
    assert "919847123456" not in out2
    assert "modern look" in out2


def test_email_addresses():
    inp = "Minimalist facade design. Email: sales@archstudio.com for plans"
    out = sanitize_reference_text(inp)
    assert "sales@archstudio.com" not in out
    assert "sales@" not in out
    assert "Email:" not in out
    assert "Minimalist facade design. for plans" in out


def test_standalone_contact_prompts_without_numbers():
    cases = [
        ("Modern duplex penthouse. Call for details.", "Modern duplex penthouse."),
        ("Contemporary villa architecture. WhatsApp for enquiries.", "Contemporary villa architecture."),
        ("Luxury residential interior design. Contact us today.", "Luxury residential interior design. today."),
        ("Beachfront residence design. For booking enquiries.", "Beachfront residence design."),
        ("Sustainable timber pavilion. Email for enquiries.", "Sustainable timber pavilion."),
    ]
    for inp, exp in cases:
        out = sanitize_reference_text(inp)
        assert out == exp, f"Failed standalone prompt scrub for '{inp}': got '{out}'"


def test_context_aware_unit_detection_not_fooled_by_single_m():
    # A 10-digit phone number followed by 'm' MUST be removed, not preserved as a meter measurement
    inp = "Site office 9847123456 m from main junction"
    out = sanitize_reference_text(inp)
    assert "9847123456" not in out, f"10-digit phone number was falsely preserved: {out}"
    assert "Site office" in out
    assert "main junction" in out


# ==============================================================================
# 2. ARCHITECTURAL SPECIFICATIONS PRESERVATION (FALSE POSITIVE GUARDS)
# ==============================================================================

def test_preserve_tile_and_slab_dimensions():
    inp1 = "Rectified ceramic wall tile 600x450mm polished finish"
    assert sanitize_reference_text(inp1) == inp1

    inp2 = "Statuario porcelain slabs 1200x2400 mm for lobby flooring"
    assert sanitize_reference_text(inp2) == inp2


def test_preserve_area_and_plot_sizes():
    inp1 = "Spacious 2400 sq.ft duplex residential plan in Bangalore"
    assert sanitize_reference_text(inp1) == inp1

    inp2 = "5 Marla Spanish elevation design in DHA Lahore"
    assert sanitize_reference_text(inp2) == inp2


def test_preserve_structural_grades_and_spans():
    inp_gl = "Glulam structural beams grade GL28h spanning 14m"
    assert sanitize_reference_text(inp_gl) == inp_gl

    inp_m35 = "High strength M35 grade reinforced concrete columns"
    assert sanitize_reference_text(inp_m35) == inp_m35

    inp_glass = "8mm glass railing with stainless steel stanchions"
    assert sanitize_reference_text(inp_glass) == inp_glass

    inp_beam = "Timber roof pavilion with 14m beam span across courtyard"
    assert sanitize_reference_text(inp_beam) == inp_beam


def test_preserve_ordinary_architectural_vocabulary():
    inp = "Modern minimalist villa featuring sustainable materials and open courtyards"
    assert sanitize_reference_text(inp) == inp


# ==============================================================================
# 3. TEMPORARY DATABASE SANITIZATION ROUNDTRIP (ISOLATED FIXTURE)
# ==============================================================================

def test_sanitizer_in_isolated_sqlite_database():
    """Verify that sanitization executes faithfully in a real SQLite table without touching production."""
    with tempfile.TemporaryDirectory(prefix="nivora_sanitizer_db_") as tmpdir:
        db_path = Path(tmpdir) / "test_references.sqlite"
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE test_refs (
                id INTEGER PRIMARY KEY,
                title TEXT,
                description TEXT
            );
        """)

        test_data = [
            (1, "Kerala Home Call/WhatsApp: +91 80896 12345", "Spacious 2400 sq.ft villa Call 9847123456"),
            (2, "Modern Minimalist Villa 600x450mm", "Features 14m beam span and M35 concrete"),
            (3, "UK Studio Project", "Inquiries: +44 7911 123456 or email sales@studio.co.uk"),
        ]
        cur.executemany("INSERT INTO test_refs VALUES (?, ?, ?);", test_data)
        conn.commit()

        # Sanitize records in-place in temporary database
        for rid, t, d in cur.execute("SELECT id, title, description FROM test_refs").fetchall():
            clean_t = sanitize_reference_text(t)
            clean_d = sanitize_reference_text(d)
            cur.execute("UPDATE test_refs SET title = ?, description = ? WHERE id = ?", (clean_t, clean_d, rid))
        conn.commit()

        # Verify results
        r1 = cur.execute("SELECT title, description FROM test_refs WHERE id = 1").fetchone()
        assert r1[0] == "Kerala Home"
        assert "2400 sq.ft" in r1[1]
        assert "9847123456" not in r1[1]

        r2 = cur.execute("SELECT title, description FROM test_refs WHERE id = 2").fetchone()
        assert "600x450mm" in r2[0]
        assert "14m beam span" in r2[1]
        assert "M35" in r2[1]

        r3 = cur.execute("SELECT title, description FROM test_refs WHERE id = 3").fetchone()
        assert "+44" not in r3[1]
        assert "sales@studio.co.uk" not in r3[1]

        conn.close()


import os
import re
import sqlite3
import pytest
from pathlib import Path

from scripts.create_sanitized_seed import (
    sanitize_reference_text,
    DEFAULT_TARGET,
    APPROVED_TABLES,
    EXCLUDED_TABLES,
)

RE_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
RE_CONTACT_PREFIX = re.compile(
    r'(?:for\s+enq(?:uiries)?|call/whatsapp|call/wa|call-whatsapp|whatsapp|call\s+at|call|ph(?:one)?|contact|inquiries?)[:\s-]+(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,5}\)?[\s-]?)?\d{3,5}[\s-]?\d{3,5}[\s-]?\d{3,5}\b',
    re.IGNORECASE,
)
RE_STANDALONE_MOBILE = re.compile(r'\b(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b')


def test_seed_exists_and_has_delete_journal_mode():
    assert DEFAULT_TARGET.exists(), f"Seed file missing at {DEFAULT_TARGET}"
    conn = sqlite3.connect(f"file:{DEFAULT_TARGET.as_posix()}?mode=ro", uri=True)
    mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
    conn.close()
    assert mode.lower() == "delete", f"Expected DELETE journal mode on seed, got {mode}"


def test_seed_contains_exactly_eight_approved_tables():
    conn = sqlite3.connect(f"file:{DEFAULT_TARGET.as_posix()}?mode=ro", uri=True)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()]
    conn.close()

    assert len(tables) == 8
    assert sorted(tables) == sorted(APPROVED_TABLES)


def test_seed_excludes_confidential_tables():
    conn = sqlite3.connect(f"file:{DEFAULT_TARGET.as_posix()}?mode=ro", uri=True)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    conn.close()

    for confidential in ["users", "suppliers", "saved_items", "supplier_products", "quotation_requests", "quotation_responses"]:
        assert confidential not in tables, f"Confidential table {confidential} found in production seed!"


def test_seed_exact_row_counts_and_zero_foreign_key_violations():
    conn = sqlite3.connect(f"file:{DEFAULT_TARGET.as_posix()}?mode=ro", uri=True)
    cur = conn.cursor()

    expected = {
        "catalogue_categories": 10,
        "catalogue_subcategories": 184,
        "catalogue_materials": 6319,
        "material_categories": 56,
        "manufacturers": 20,
        "architectural_references": 504,
        "products": 21,
        "reference_product_matches": 9,
    }

    for tbl, count in expected.items():
        actual = cur.execute(f'SELECT COUNT(*) FROM "{tbl}"').fetchone()[0]
        assert actual == count, f"Table {tbl} row count mismatch: expected {count}, got {actual}"

    cur.execute("PRAGMA foreign_keys = ON;")
    fk_violations = cur.execute("PRAGMA foreign_key_check;").fetchall()
    conn.close()

    assert len(fk_violations) == 0, f"Foreign key violations found in seed: {fk_violations}"


def test_seed_privacy_zero_emails_or_phones_in_references():
    conn = sqlite3.connect(f"file:{DEFAULT_TARGET.as_posix()}?mode=ro", uri=True)
    rows = conn.execute("SELECT id, title, description FROM architectural_references").fetchall()
    conn.close()

    for rid, title, desc in rows:
        text = f"{title or ''} {desc or ''}"
        assert not RE_EMAIL.search(text), f"Email found in Ref {rid}: {text}"
        assert not RE_CONTACT_PREFIX.search(text), f"Contact prefix found in Ref {rid}: {text}"


def test_sanitizer_preserves_dimensions_and_specifications():
    samples = [
        ("KPC M35 Precast Heavy Duty Drainage Slab (600x450x75mm)", "600x450x75mm"),
        ("Precast Stormwater U-Drain Channel (300x300mm)", "300x300mm"),
        ("5 Marla Modern Design House with 2400 sq.ft living area", "5 Marla"),
        ("5 Marla Modern Design House with 2400 sq.ft living area", "2400 sq.ft"),
        ("1 Kanal Victorian House", "1 Kanal"),
        ("Glulam Timber Beam GL28h", "GL28h"),
    ]

    for text, spec in samples:
        sanitized = sanitize_reference_text(text)
        assert spec in sanitized, f"Spec '{spec}' was incorrectly removed from '{text}'! Got: '{sanitized}'"


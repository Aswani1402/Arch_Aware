#!/usr/bin/env python3
"""
NIVORA — Production SQLite Seed Sanitization & Generation Tool

Generates a sanitized, production-ready SQLite seed database (backend/seed_catalogue.sqlite)
from the source database (backend/architect_ai.db) by strictly including approved public
catalogue and architectural reference data while excluding confidential user accounts,
password hashes, supplier contact details, and user-specific bookmarks.

Sanitizes raw social media and video contact details (phone numbers, WhatsApp links, emails)
from architectural reference titles and descriptions while strictly preserving all architectural
measurements, dimensions, and specifications.

Usage:
    python scripts/create_sanitized_seed.py [--source PATH] [--target PATH] [--force] [--backup-existing]
"""

import argparse
import datetime
import hashlib
import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Default Paths
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = WORKSPACE_ROOT / "backend" / "architect_ai.db"
DEFAULT_TARGET = WORKSPACE_ROOT / "backend" / "seed_catalogue.sqlite"

# Approved Tables Policy (Public Architecture Taxonomy & Catalogue)
APPROVED_TABLES = [
    "catalogue_categories",
    "catalogue_subcategories",
    "catalogue_materials",
    "material_categories",
    "manufacturers",
    "architectural_references",
    "products",
    "reference_product_matches",
]

# Excluded Tables Policy & Justification
EXCLUDED_TABLES = {
    "users": "Confidential user accounts, email addresses, roles, and password hashes.",
    "suppliers": "Personal vendor contacts, mobile phone numbers, personal WhatsApp links, and physical addresses.",
    "saved_items": "User-specific bookmark collections and personal project links.",
    "supplier_products": "Commercial supplier pricing, stock quantities, and quotes referencing excluded suppliers.",
    "quotation_requests": "Confidential commercial quotation inquiries and user project details.",
    "quotation_responses": "Proprietary vendor price quotes, delivery terms, and quote messages.",
    "daily_collection_records": "Operational task execution and crawler monitoring logs.",
    "catalogue_import_runs": "Operational CSV catalogue batch import audit logs.",
    "source_sync_logs": "Operational ingestion synchronization status logs.",
    "custom_keywords": "Temporary search keyword tracking state (0 records).",
    "inspiration_materials": "Visual inference tags containing orphaned foreign key references; excluded from base catalogue.",
    "source_connectors": "Platform connector operational configurations.",
}

# Regex patterns for contact sanitization

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

    # Pre-check: only sanitize if a contact pattern is present
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


def verify_source_database(source_path: Path) -> Dict[str, any]:
    """Verify source database accessibility, size, and integrity in read-only mode."""
    if not source_path.exists():
        raise FileNotFoundError(f"Source database not found at {source_path}")

    size = source_path.stat().st_size
    with open(source_path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()

    conn = sqlite3.connect(f"file:{source_path.as_posix()}?mode=ro", uri=True)
    cur = conn.cursor()
    journal_mode = cur.execute("PRAGMA journal_mode;").fetchone()[0]
    integrity = cur.execute("PRAGMA integrity_check;").fetchone()[0]
    quick = cur.execute("PRAGMA quick_check;").fetchone()[0]
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
    row_counts = {t: cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tables}
    conn.close()

    if integrity != "ok" or quick != "ok":
        raise RuntimeError(f"Source database integrity check failed: integrity={integrity}, quick={quick}")

    return {
        "path": str(source_path),
        "size": size,
        "sha256": sha256,
        "journal_mode": journal_mode,
        "integrity": integrity,
        "quick": quick,
        "tables": row_counts,
        "total_rows": sum(row_counts.values()),
    }


def sanitize_and_export_seed(
    source_path: Path,
    target_path: Path,
    force: bool = False,
    backup_existing: bool = False,
    include_inspiration: bool = False,
) -> Dict[str, any]:
    """
    Exports sanitized data from source SQLite database to a new target seed file.
    """
    source_path = source_path.resolve()
    target_path = target_path.resolve()

    # Pre-verification of source database
    src_meta = verify_source_database(source_path)
    print(f"[Seed Generator] Source Database Verified: {src_meta['size']:,} bytes, {src_meta['total_rows']:,} rows, SHA256: {src_meta['sha256']}")

    # Safety: Refuse to overwrite without explicit flag
    if target_path.exists():
        if backup_existing:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = target_path.with_name(f"{target_path.stem}.backup_{timestamp}{target_path.suffix}")
            shutil.copy2(target_path, backup_path)
            print(f"[Seed Generator] Backed up existing seed to {backup_path}")
            target_path.unlink()
        elif force:
            print(f"[Seed Generator] Overwriting existing seed database (--force specified)")
            target_path.unlink()
        else:
            raise FileExistsError(
                f"Target seed database already exists at {target_path}. "
                "Refusing to overwrite. Pass --force to replace or --backup-existing to preserve a copy."
            )

    tables_to_export = list(APPROVED_TABLES)
    if include_inspiration:
        tables_to_export.append("inspiration_materials")

    # Connect to source in strictly read-only mode
    source_uri = f"file:{source_path.as_posix()}?mode=ro"
    src_conn = sqlite3.connect(source_uri, uri=True)
    src_cur = src_conn.cursor()

    # Create destination database
    target_path.parent.mkdir(parents=True, exist_ok=True)
    dst_conn = sqlite3.connect(target_path.as_posix())
    dst_cur = dst_conn.cursor()

    # Destination settings: Standard DELETE mode (never WAL on source seed)
    dst_cur.execute("PRAGMA journal_mode = delete;")
    dst_cur.execute("PRAGMA synchronous = NORMAL;")
    dst_cur.execute("PRAGMA foreign_keys = OFF;")

    audit_summary = []
    sanitized_references_count = 0

    try:
        for table in tables_to_export:
            # 1. Extract exact table DDL
            ddl_row = src_cur.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
            ).fetchone()
            if not ddl_row or not ddl_row[0]:
                raise RuntimeError(f"Could not retrieve schema DDL for approved table '{table}'")

            table_ddl = ddl_row[0]
            dst_cur.execute(table_ddl)

            # 2. Extract and create indexes
            indexes = src_cur.execute(
                "SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name=? AND sql IS NOT NULL", (table,)
            ).fetchall()
            for idx_row in indexes:
                dst_cur.execute(idx_row[0])

            # 3. Get source count
            source_count = src_cur.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]

            # 4. Extract approved columns
            cols_info = src_cur.execute(f'PRAGMA table_info("{table}")').fetchall()
            col_names = [c[1] for c in cols_info]
            col_list_str = ", ".join([f'"{c}"' for c in col_names])
            placeholders = ", ".join(["?"] * len(col_names))

            # 5. Extract rows with referential integrity and privacy sanitization
            if table == "reference_product_matches":
                # Ensure foreign keys are strictly satisfied
                query = f"""
                    SELECT {col_list_str} FROM "{table}"
                    WHERE reference_id IN (SELECT id FROM architectural_references)
                      AND product_id IN (SELECT id FROM products)
                    ORDER BY id ASC
                """
                rows = src_cur.execute(query).fetchall()
            elif table == "inspiration_materials":
                # Filter out orphaned reference_id
                query = f"""
                    SELECT {col_list_str} FROM "{table}"
                    WHERE reference_id IN (SELECT id FROM architectural_references)
                    ORDER BY id ASC
                """
                rows = src_cur.execute(query).fetchall()
            elif table == "architectural_references":
                raw_rows = src_cur.execute(f'SELECT {col_list_str} FROM "{table}" ORDER BY id ASC').fetchall()
                title_idx = col_names.index("title")
                desc_idx = col_names.index("description")
                rows = []
                for r in raw_rows:
                    r_list = list(r)
                    orig_t = r_list[title_idx] or ""
                    orig_d = r_list[desc_idx] or ""
                    san_t = sanitize_reference_text(orig_t, fallback_title="Architectural Reference Design")
                    san_d = sanitize_reference_text(orig_d)
                    if orig_t != san_t or orig_d != san_d:
                        sanitized_references_count += 1
                    r_list[title_idx] = san_t
                    r_list[desc_idx] = san_d
                    rows.append(tuple(r_list))
            else:
                rows = src_cur.execute(f'SELECT {col_list_str} FROM "{table}" ORDER BY id ASC').fetchall()

            insert_sql = f'INSERT INTO "{table}" ({col_list_str}) VALUES ({placeholders})'
            dst_cur.executemany(insert_sql, rows)

            exported_count = len(rows)
            delta = exported_count - source_count
            note = "Complete"
            if delta != 0:
                note = f"{abs(delta)} orphaned reference(s) omitted"
            elif table == "architectural_references":
                note = f"Complete ({sanitized_references_count} records sanitized)"

            audit_summary.append({
                "table": table,
                "source_count": source_count,
                "exported_count": exported_count,
                "delta": delta,
                "columns": col_names,
                "note": note,
            })

        dst_conn.commit()

        # Run integrity checks on the newly created seed
        dst_cur.execute("PRAGMA foreign_keys = ON;")
        integrity = dst_cur.execute("PRAGMA integrity_check;").fetchone()[0]
        quick = dst_cur.execute("PRAGMA quick_check;").fetchone()[0]
        fk_violations = dst_cur.execute("PRAGMA foreign_key_check;").fetchall()

        if integrity != "ok" or quick != "ok":
            raise RuntimeError(f"Integrity check failed on generated seed: integrity={integrity}, quick={quick}")

        if fk_violations:
            raise RuntimeError(f"Foreign key violations detected in generated seed: {fk_violations}")

    except Exception as exc:
        dst_conn.rollback()
        dst_conn.close()
        if target_path.exists():
            target_path.unlink()
        raise exc
    finally:
        src_conn.close()
        dst_conn.close()

    return {
        "source": str(source_path),
        "target": str(target_path),
        "target_size_bytes": target_path.stat().st_size,
        "sanitized_references_count": sanitized_references_count,
        "included_tables": audit_summary,
        "excluded_tables": EXCLUDED_TABLES,
    }


def main():
    parser = argparse.ArgumentParser(description="Create sanitized production SQLite seed for NIVORA.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Source database path")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET, help="Target seed database path")
    parser.add_argument("--force", action="store_true", help="Overwrite existing target file without prompt")
    parser.add_argument("--backup-existing", action="store_true", help="Backup existing target file before creating new")
    parser.add_argument("--include-inspiration", action="store_true", help="Include referentially valid inspiration_materials")

    args = parser.parse_args()

    print("=" * 70)
    print(" NIVORA — Sanitized SQLite Seed Generator")
    print("=" * 70)

    try:
        result = sanitize_and_export_seed(
            source_path=args.source,
            target_path=args.target,
            force=args.force,
            backup_existing=args.backup_existing,
            include_inspiration=args.include_inspiration,
        )

        print("\n=== EXPORT AUDIT SUMMARY ===")
        print(f"{'Table Name':<30} {'Source':<8} {'Exported':<10} {'Status'}")
        print("-" * 70)
        total_source = 0
        total_exported = 0
        for item in result["included_tables"]:
            total_source += item["source_count"]
            total_exported += item["exported_count"]
            print(f"{item['table']:<30} {item['source_count']:<8} {item['exported_count']:<10} {item['note']}")
        print("-" * 70)
        print(f"{'TOTAL ROWS':<30} {total_source:<8} {total_exported:<10}")

        print(f"\nArchitectural References Sanitized: {result['sanitized_references_count']} records cleaned of contact info")

        print("\n=== EXCLUDED TABLES (CONFIDENTIAL & OPERATIONAL) ===")
        for tbl, reason in result["excluded_tables"].items():
            print(f"- {tbl:<25}: {reason}")

        print(f"\nArtifact created successfully: {result['target']} ({result['target_size_bytes']:,} bytes)")
        sys.exit(0)

    except Exception as exc:
        print(f"\n[ERROR] Seed generation aborted: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

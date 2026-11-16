import os
import sys
import sqlite3
import argparse
import re
from pathlib import Path

SOURCE_DEFAULT = Path("backend/architect_ai.db")
TARGET_DEFAULT = Path("backend/seed_catalogue.sqlite")

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

EXCLUDED_TABLES_REASONS = {
    "users": "Confidential user accounts, authentication credentials, and password hashes.",
    "suppliers": "Personal contact details, direct mobile phone numbers, personal WhatsApp links, and residential/business addresses.",
    "saved_items": "User-specific collections and personal bookmark associations.",
    "supplier_products": "Proprietary supplier pricing, stock levels, and quotes referencing excluded suppliers.",
    "quotation_requests": "Confidential user project requests and commercial quotation submissions.",
    "quotation_responses": "Proprietary vendor price quotes, delivery terms, and quote messages.",
    "daily_collection_records": "Operational task execution and crawler monitoring logs.",
    "catalogue_import_runs": "Operational CSV catalogue batch import audit logs.",
    "source_sync_logs": "Operational ingestion synchronization status logs.",
    "custom_keywords": "Temporary search keyword tracking state (0 rows).",
    "inspiration_materials": "Visual inference tags containing orphaned foreign key references; excluded to ensure 100% relational integrity.",
    "source_connectors": "Platform connector operational configurations.",
}

def create_sanitized_seed(source_path: Path, target_path: Path, force: bool = False, include_inspiration: bool = False):
    print(f"[Sanitize Seed] Source: {source_path}")
    print(f"[Sanitize Seed] Target: {target_path}")

    if not source_path.exists():
        raise FileNotFoundError(f"Source database not found: {source_path}")

    if target_path.exists():
        if not force:
            raise FileExistsError(
                f"Target seed database already exists at {target_path}. "
                "Refusing to overwrite without explicit --force flag."
            )
        else:
            print(f"[Sanitize Seed] Target exists and --force specified. Removing {target_path}...")
            target_path.unlink()

    tables_to_export = list(APPROVED_TABLES)
    if include_inspiration:
        tables_to_export.append("inspiration_materials")

    # Connect to source in strictly read-only mode
    source_uri = f"file:{source_path.resolve().as_posix()}?mode=ro"
    src_conn = sqlite3.connect(source_uri, uri=True)
    src_cur = src_conn.cursor()

    # Create destination database
    target_path.parent.mkdir(parents=True, exist_ok=True)
    dst_conn = sqlite3.connect(target_path.resolve().as_posix())
    dst_cur = dst_conn.cursor()

    # Enforce standard SQLite journal mode on the seed artifact (DELETE mode, NOT WAL)
    dst_cur.execute("PRAGMA journal_mode = delete;")
    dst_cur.execute("PRAGMA synchronous = NORMAL;")
    dst_cur.execute("PRAGMA foreign_keys = OFF;") # turned on after copying for validation

    audit_records = []

    try:
        # Recreate tables & indices
        for table in tables_to_export:
            # 1. Fetch DDL
            table_ddl_row = src_cur.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
            ).fetchone()
            if not table_ddl_row or not table_ddl_row[0]:
                raise RuntimeError(f"Could not retrieve DDL for approved table: {table}")
            
            table_ddl = table_ddl_row[0]
            dst_cur.execute(table_ddl)

            # 2. Recreate indices
            indices = src_cur.execute(
                "SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name=? AND sql IS NOT NULL", (table,)
            ).fetchall()
            for idx in indices:
                dst_cur.execute(idx[0])

            # 3. Source count
            source_count = src_cur.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]

            # 4. Copy data with referential integrity filtering
            cols_info = src_cur.execute(f'PRAGMA table_info("{table}")').fetchall()
            col_names = [c[1] for c in cols_info]
            col_list_str = ", ".join([f'"{c}"' for c in col_names])
            placeholders = ", ".join(["?"] * len(col_names))

            if table == "reference_product_matches":
                # Filter out orphan reference_id=16
                query = f"""
                    SELECT {col_list_str} FROM "{table}"
                    WHERE reference_id IN (SELECT id FROM architectural_references)
                      AND product_id IN (SELECT id FROM products)
                    ORDER BY id ASC
                """
                rows = src_cur.execute(query).fetchall()
            elif table == "inspiration_materials":
                # Filter out orphan reference_id=16
                query = f"""
                    SELECT {col_list_str} FROM "{table}"
                    WHERE reference_id IN (SELECT id FROM architectural_references)
                    ORDER BY id ASC
                """
                rows = src_cur.execute(query).fetchall()
            else:
                rows = src_cur.execute(f'SELECT {col_list_str} FROM "{table}" ORDER BY id ASC').fetchall()

            insert_sql = f'INSERT INTO "{table}" ({col_list_str}) VALUES ({placeholders})'
            dst_cur.executemany(insert_sql, rows)

            exported_count = len(rows)
            delta = exported_count - source_count
            audit_records.append({
                "table": table,
                "source_count": source_count,
                "exported_count": exported_count,
                "delta": delta,
                "status": "VALIDATED" if delta == 0 else f"FILTERED ({delta} orphan(s) excluded)"
            })

        dst_conn.commit()

        # Run SQLite validation
        dst_cur.execute("PRAGMA foreign_keys = ON;")
        integrity = dst_cur.execute("PRAGMA integrity_check;").fetchone()[0]
        quick = dst_cur.execute("PRAGMA quick_check;").fetchone()[0]
        fk_violations = dst_cur.execute("PRAGMA foreign_key_check;").fetchall()

        if integrity != "ok" or quick != "ok":
            raise RuntimeError(f"Seed database integrity check failed: integrity={integrity}, quick={quick}")

        if fk_violations:
            raise RuntimeError(f"Seed database has foreign key violations: {fk_violations}")

    except Exception as e:
        dst_conn.rollback()
        dst_conn.close()
        if target_path.exists():
            target_path.unlink()
        raise e
    finally:
        src_conn.close()
        dst_conn.close()

    print("\n[Sanitize Seed] Successfully generated seed database!")
    return audit_records

if __name__ == "__main__":
    records = create_sanitized_seed(SOURCE_DEFAULT, TARGET_DEFAULT, force=True)
    for r in records:
        print(f"Table: {r['table']:30} Source: {r['source_count']:5} Exported: {r['exported_count']:5} Status: {r['status']}")


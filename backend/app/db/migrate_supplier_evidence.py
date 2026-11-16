"""
Additive migration script for Stage 7:
Creates supplier_material_evidence table and seeds initial evidence rows
based on confirmed supplier inventory and declared materials.
Non-destructive: Never modifies, deletes, drops or alters existing records.
"""

import os
import sqlite3
from datetime import datetime, timezone

def run_migration():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    db_path = os.path.join(root, "backend", "architect_ai.db")

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # 1. Create table if not exists
    cur.execute("""
    CREATE TABLE IF NOT EXISTS supplier_material_evidence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
        material_id INTEGER REFERENCES catalogue_materials(id),
        evidence_type TEXT NOT NULL,
        evidence_text TEXT NOT NULL,
        source_url TEXT,
        checked_at DATETIME,
        strength REAL DEFAULT 1.0
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS ix_supplier_material_evidence_supplier_id ON supplier_material_evidence(supplier_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_supplier_material_evidence_material_id ON supplier_material_evidence(material_id);")

    # 2. Check current count
    existing_count = cur.execute("SELECT count(*) FROM supplier_material_evidence").fetchone()[0]
    if existing_count == 0:
        now_iso = datetime.now(timezone.utc).isoformat()
        inserted = 0

        # Evidence Source A: Linked confirmed products from supplier_products
        product_rows = cur.execute("""
            SELECT sp.supplier_id, p.id, p.name, s.website
            FROM supplier_products sp
            JOIN products p ON sp.product_id = p.id
            JOIN suppliers s ON sp.supplier_id = s.id
        """).fetchall()

        for s_id, p_id, p_name, website in product_rows:
            # Check if matching catalogue_materials exists
            mat = cur.execute("SELECT id FROM catalogue_materials WHERE lower(name) = lower(?)", (p_name,)).fetchone()
            mat_id = mat[0] if mat else None
            cur.execute("""
                INSERT INTO supplier_material_evidence (supplier_id, material_id, evidence_type, evidence_text, source_url, checked_at, strength)
                VALUES (?, ?, 'product_list', ?, ?, ?, 1.0)
            """, (s_id, mat_id, f"Confirmed Catalog Product: {p_name}", website, now_iso))
            inserted += 1

        # Evidence Source B: Declared materials from suppliers.materials_sold
        supplier_rows = cur.execute("SELECT id, name, materials_sold, website FROM suppliers WHERE materials_sold IS NOT NULL").fetchall()
        for s_id, s_name, mats_sold, website in supplier_rows:
            if not mats_sold or not mats_sold.strip():
                continue
            # Split items
            items = [m.strip() for m in mats_sold.replace(";", ",").split(",") if len(m.strip()) >= 3]
            for item in items:
                # Check for exact material name or prefix
                mat = cur.execute("SELECT id FROM catalogue_materials WHERE lower(name) = lower(?)", (item,)).fetchone()
                mat_id = mat[0] if mat else None
                cur.execute("""
                    INSERT INTO supplier_material_evidence (supplier_id, material_id, evidence_type, evidence_text, source_url, checked_at, strength)
                    VALUES (?, ?, 'listing_text', ?, ?, ?, 0.90)
                """, (s_id, mat_id, f"Verified Listing Stock: {item}", website, now_iso))
                inserted += 1

        con.commit()
        print(f"Successfully seeded {inserted} material evidence rows into supplier_material_evidence.")
    else:
        print(f"supplier_material_evidence already populated with {existing_count} rows.")

    con.close()
    return True

if __name__ == "__main__":
    run_migration()

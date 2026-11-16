import sqlite3
import os

dbs = ["architect_ai.db", "backend/architect_ai.db"]

print("=" * 70)
print("SQLITE DATABASE INTEGRITY & RECORD PRESERVATION CHECK")
print("=" * 70)

for db_path in dbs:
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        continue

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT count(*) FROM architectural_references")
    ref_count = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM suppliers")
    sup_count = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM products")
    prod_count = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM saved_items")
    saved_count = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM material_categories")
    cat_count = cur.fetchone()[0]

    print(f"File: {db_path}")
    print(f"  - Architectural References : {ref_count}")
    print(f"  - Verified Suppliers       : {sup_count}")
    print(f"  - Products                 : {prod_count}")
    print(f"  - Saved Collections Items  : {saved_count}")
    print(f"  - Material Categories      : {cat_count}")
    conn.close()
    print("-" * 70)


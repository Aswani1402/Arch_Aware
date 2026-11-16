import sqlite3
import json

conn = sqlite3.connect('file:backend/architect_ai.db?mode=ro', uri=True)
cursor = conn.cursor()

# 1. Inspect manufacturers contact_info
print("=== MANUFACTURERS contact_info ===")
for row in cursor.execute("SELECT id, name, contact_info FROM manufacturers LIMIT 10").fetchall():
    print(f"ID: {row[0]}, Name: {row[1]}, contact_info: {row[2]}")

# 2. Inspect source_connectors
print("\n=== SOURCE_CONNECTORS ===")
for row in cursor.execute("SELECT id, name, platform, is_active, config_json FROM source_connectors").fetchall():
    print(f"ID: {row[0]}, Name: {row[1]}, Platform: {row[2]}, Active: {row[3]}, config_json: {row[4]}")

# 3. Inspect inspiration_materials sample
print("\n=== INSPIRATION_MATERIALS Sample ===")
for row in cursor.execute("SELECT id, reference_id, name, category_slug, material_category, identification_type, product_id FROM inspiration_materials LIMIT 10").fetchall():
    print(f"ID: {row[0]}, Ref: {row[1]}, Name: {row[2]}, CatSlug: {row[3]}, MatCat: {row[4]}, Type: {row[5]}, ProdId: {row[6]}")

# Check if any inspiration_materials reference_id or product_id are missing in parent tables
ref_ids_in_insp = set(r[0] for r in cursor.execute("SELECT DISTINCT reference_id FROM inspiration_materials WHERE reference_id IS NOT NULL").fetchall())
ref_ids_in_arch = set(r[0] for r in cursor.execute("SELECT id FROM architectural_references").fetchall())
diff_refs = ref_ids_in_insp - ref_ids_in_arch
print(f"\nInspiration refs not in architectural_references: {len(diff_refs)}")

prod_ids_in_insp = set(r[0] for r in cursor.execute("SELECT DISTINCT product_id FROM inspiration_materials WHERE product_id IS NOT NULL").fetchall())
prod_ids_in_prods = set(r[0] for r in cursor.execute("SELECT id FROM products").fetchall())
diff_prods = prod_ids_in_insp - prod_ids_in_prods
print(f"Inspiration prods not in products: {len(diff_prods)}")

conn.close()


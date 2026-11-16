import sqlite3

conn = sqlite3.connect('file:backend/architect_ai.db?mode=ro', uri=True)
cursor = conn.cursor()

def check_fk(from_table, from_col, to_table, to_col):
    q = f"""
    SELECT COUNT(*) FROM "{from_table}" 
    WHERE "{from_col}" IS NOT NULL 
      AND "{from_col}" NOT IN (SELECT "{to_col}" FROM "{to_table}")
    """
    orphans = cursor.execute(q).fetchone()[0]
    total = cursor.execute(f'SELECT COUNT(*) FROM "{from_table}"').fetchone()[0]
    non_null = cursor.execute(f'SELECT COUNT(*) FROM "{from_table}" WHERE "{from_col}" IS NOT NULL').fetchone()[0]
    print(f"FK {from_table}.{from_col} -> {to_table}.{to_col}: total={total}, non_null={non_null}, orphans={orphans}")

print("=== CHECKING ALL ALLOWLIST CANDIDATE FOREIGN KEYS ===")
check_fk("catalogue_subcategories", "category_id", "catalogue_categories", "id")
check_fk("catalogue_materials", "category_id", "catalogue_categories", "id")
check_fk("catalogue_materials", "subcategory_id", "catalogue_subcategories", "id")
check_fk("architectural_references", "category_id", "material_categories", "id")
check_fk("architectural_references", "manufacturer_id", "manufacturers", "id")
check_fk("products", "category_id", "material_categories", "id")
check_fk("products", "manufacturer_id", "manufacturers", "id")
check_fk("reference_product_matches", "reference_id", "architectural_references", "id")
check_fk("reference_product_matches", "product_id", "products", "id")
check_fk("inspiration_materials", "reference_id", "architectural_references", "id")
check_fk("inspiration_materials", "category_id", "material_categories", "id")
check_fk("inspiration_materials", "product_id", "products", "id")

conn.close()


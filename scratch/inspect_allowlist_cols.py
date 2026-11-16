import sqlite3
import json

conn = sqlite3.connect('file:backend/architect_ai.db?mode=ro', uri=True)
cursor = conn.cursor()

allowlist_tables = [
    'catalogue_categories',
    'catalogue_subcategories',
    'catalogue_materials',
    'material_categories',
    'manufacturers',
    'architectural_references',
    'products',
    'reference_product_matches'
]

print("=== CHECKING COLUMNS FOR ALLOWLIST TABLES ===")
for t in allowlist_tables:
    cols = cursor.execute(f'PRAGMA table_info("{t}")').fetchall()
    col_names = [c[1] for c in cols]
    print(f"\nTable: {t}")
    print(f"Columns ({len(col_names)}): {', '.join(col_names)}")

conn.close()


import sqlite3

conn = sqlite3.connect('file:backend/architect_ai.db?mode=ro', uri=True)
cur = conn.cursor()

print("=== 1. CATALOGUE CATEGORIES & MATERIAL COUNTS ===")
cur.execute('''
    SELECT c.id, c.name, c.slug, COUNT(m.id) as material_count
    FROM catalogue_categories c
    LEFT JOIN catalogue_subcategories s ON s.category_id = c.id
    LEFT JOIN catalogue_materials m ON m.subcategory_id = s.id
    GROUP BY c.id, c.name, c.slug
    ORDER BY c.id
''')
cat_rows = cur.fetchall()
total_mat = 0
for row in cat_rows:
    print(f"ID {row[0]}: {row[1]} (slug: {row[2]}) -> {row[3]} materials")
    total_mat += row[3]
print(f"Total materials across categories: {total_mat}")

print("\n=== 2. DISTINCT SUBCATEGORIES COUNT PER CATEGORY ===")
cur.execute('''
    SELECT c.id, c.name, COUNT(DISTINCT s.id) as sub_count, COUNT(m.id) as mat_count
    FROM catalogue_categories c
    JOIN catalogue_subcategories s ON s.category_id = c.id
    LEFT JOIN catalogue_materials m ON m.subcategory_id = s.id
    GROUP BY c.id, c.name
    ORDER BY c.id
''')
for row in cur.fetchall():
    print(f"Category {row[0]} '{row[1]}': {row[2]} subcategories, {row[3]} materials")

print("\n=== 3. SAMPLE OF SUBCATEGORIES (ALL 184) ===")
cur.execute('''
    SELECT c.name, s.id, s.name, s.slug, COUNT(m.id) as mat_count
    FROM catalogue_categories c
    JOIN catalogue_subcategories s ON s.category_id = c.id
    LEFT JOIN catalogue_materials m ON m.subcategory_id = s.id
    GROUP BY c.name, s.id, s.name, s.slug
    ORDER BY c.id, s.id
''')
all_subs = cur.fetchall()
print(f"Total subcategories returned: {len(all_subs)}")
for s in all_subs[:30]:
    print(f"  [{s[0]}] Subcat #{s[1]}: {s[2]} ({s[3]}) -> {s[4]} materials")
print(f"  ... and {len(all_subs)-30} more subcategories")

print("\n=== 4. CHECK MATERIAL_CATEGORIES TABLE (TAXONOMY SYSTEM 2) ===")
cur.execute("PRAGMA table_info(material_categories);")
print("material_categories columns:", [r[1] for r in cur.fetchall()])
cur.execute("SELECT COUNT(*) FROM material_categories;")
print("material_categories total rows:", cur.fetchone()[0])
cur.execute("SELECT id, name, slug FROM material_categories ORDER BY id;")
mat_cats = cur.fetchall()
for mc in mat_cats[:15]:
    print(f"  ID {mc[0]}: {mc[1]} ({mc[2]})")
print(f"  ... and {len(mat_cats)-15} more rows")

print("\n=== 5. WHERE DO 'Site Preparation', 'Foundation and Structure', 'Bricks, Blocks and Masonry' COME FROM? ===")
cur.execute("""
    SELECT 'material_categories' as source_table, id, name, slug FROM material_categories 
    WHERE name LIKE '%Site Preparation%' OR name LIKE '%Foundation%' OR name LIKE '%Masonry%' OR name LIKE '%Exterior%' OR name LIKE '%Earthwork%'
""")
for r in cur.fetchall():
    print(" ", r)

cur.execute("""
    SELECT 'catalogue_categories' as source_table, id, name, slug FROM catalogue_categories
    WHERE name LIKE '%Site Preparation%' OR name LIKE '%Foundation%' OR name LIKE '%Masonry%' OR name LIKE '%Exterior%' OR name LIKE '%Earthwork%'
""")
for r in cur.fetchall():
    print(" ", r)

cur.execute("""
    SELECT 'catalogue_subcategories' as source_table, id, name, slug FROM catalogue_subcategories
    WHERE name LIKE '%Site Preparation%' OR name LIKE '%Foundation%' OR name LIKE '%Masonry%' OR name LIKE '%Exterior%' OR name LIKE '%Earthwork%'
""")
for r in cur.fetchall():
    print(" ", r)

print("\n=== 6. CHECK FOR KEYWORD LIBRARY IN BACKEND PYTHON FILES ===")
conn.close()


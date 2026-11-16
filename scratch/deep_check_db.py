import sqlite3
import re

conn = sqlite3.connect('file:backend/architect_ai.db?mode=ro', uri=True)
cursor = conn.cursor()

tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]

print("=== CHECKING FOREIGN KEY VIOLATIONS IN SOURCE DATABASE ===")
cursor.execute("PRAGMA foreign_keys = ON;")
violations = cursor.execute("PRAGMA foreign_key_check;").fetchall()
print(f"Total FK violations in source DB: {len(violations)}")
for v in violations:
    print("  FK violation:", v)

print("\n=== CHECKING INSPIRATION_MATERIALS FK DETAILS ===")
cursor.execute("""
    SELECT im.id, im.reference_id, im.category_id, im.product_id
    FROM inspiration_materials im
    WHERE (im.reference_id IS NOT NULL AND im.reference_id NOT IN (SELECT id FROM architectural_references))
       OR (im.category_id IS NOT NULL AND im.category_id NOT IN (SELECT id FROM material_categories))
       OR (im.product_id IS NOT NULL AND im.product_id NOT IN (SELECT id FROM products))
""")
insp_fk_issues = cursor.fetchall()
print("Inspiration materials FK issues count:", len(insp_fk_issues))
for row in insp_fk_issues:
    print(" ", row)

print("\n=== CHECKING ALL TABLES FOR EMAIL / PHONE / PASSWORDS / TOKENS ===")
email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
# Note: we only count occurrences, never print values!

for t in tables:
    cols = [c[1] for c in cursor.execute(f'PRAGMA table_info("{t}")').fetchall()]
    text_cols = [c[1] for c in cursor.execute(f'PRAGMA table_info("{t}")').fetchall() if any(tp in str(c[2]).upper() for tp in ['TEXT', 'CHAR', 'CLOB', 'VARCHAR'])]
    
    email_hits = 0
    phone_hits = 0
    pwd_hits = 0
    
    # check column names
    sensitive_col_names = [c for c in cols if any(k in c.lower() for k in ['password', 'hash', 'token', 'secret', 'key', 'auth', 'email', 'phone', 'whatsapp'])]
    
    print(f"Table: {t:30} Sensitive col names: {sensitive_col_names}")

conn.close()


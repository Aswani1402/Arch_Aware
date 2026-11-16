import sqlite3
import os
import re

seed_path = "backend/seed_catalogue.sqlite"

print(f"=== VALIDATING {seed_path} ===")
file_size = os.path.getsize(seed_path)
print(f"File Size: {file_size:,} bytes")

conn = sqlite3.connect(f"file:{seed_path}?mode=ro", uri=True)
cur = conn.cursor()

# 1. PRAGMA integrity_check
integrity = cur.execute("PRAGMA integrity_check;").fetchall()
print("PRAGMA integrity_check:", integrity)

# 2. PRAGMA quick_check
quick = cur.execute("PRAGMA quick_check;").fetchall()
print("PRAGMA quick_check:", quick)

# 3. PRAGMA journal_mode
journal_mode = cur.execute("PRAGMA journal_mode;").fetchone()[0]
print("PRAGMA journal_mode:", journal_mode)

# 4. PRAGMA foreign_key_check
cur.execute("PRAGMA foreign_keys = ON;")
fk_check = cur.execute("PRAGMA foreign_key_check;").fetchall()
print(f"PRAGMA foreign_key_check violations ({len(fk_check)}):", fk_check)

# 5. Tables & Views
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()]
print(f"Tables count: {len(tables)}")
print("Tables list:", tables)

# 6. Sensitive Tables Check
sensitive_tables = [t for t in tables if t in ['users', 'suppliers', 'saved_items', 'quotation_requests', 'quotation_responses']]
print("Sensitive tables present:", sensitive_tables)

# 7. Sensitive data scanning across all text columns
email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
phone_pattern = re.compile(r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b') # Indian mobile format
pwd_pattern = re.compile(r'\$2[aby]\$[0-9]{2}\$[A-Za-z0-9./]{53}|argon2')

email_matches = 0
phone_matches = 0
pwd_matches = 0

for t in tables:
    cols = [c[1] for c in cur.execute(f'PRAGMA table_info("{t}")').fetchall()]
    # check row counts
    count = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    print(f"Table: {t:30} Rows: {count:5} Columns: {len(cols)}")
    
    # scan for passwords/hashes
    for row in cur.execute(f'SELECT * FROM "{t}"').fetchall():
        row_str = " ".join([str(val) for val in row if val is not None])
        if pwd_pattern.search(row_str):
            pwd_matches += 1

print(f"\nSensitive Scan Results:")
print(f"Password/Hash matches: {pwd_matches}")

conn.close()


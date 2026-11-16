import os, hashlib, sqlite3, datetime

db_path = 'backend/architect_ai.db'
size = os.path.getsize(db_path)
mtime = datetime.datetime.fromtimestamp(os.path.getmtime(db_path), tz=datetime.timezone.utc)

with open(db_path, 'rb') as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()

uri = f"file:{os.path.abspath(db_path)}?mode=ro"
conn = sqlite3.connect(uri, uri=True)
cur = conn.cursor()

journal_mode = cur.execute('PRAGMA journal_mode;').fetchone()[0]
integrity = cur.execute('PRAGMA integrity_check;').fetchall()
quick = cur.execute('PRAGMA quick_check;').fetchall()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [row[0] for row in cur.fetchall() if not row[0].startswith('sqlite_')]

row_counts = {}
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t}";')
    row_counts[t] = cur.fetchone()[0]

cur.execute('SELECT id, user_id, item_type, reference_id, product_id, supplier_id, project_collection, created_at FROM saved_items;')
saved_items_rows = cur.fetchall()

conn.close()

print('=== ORIGINAL DB AUDIT ===')
print(f'File Size: {size}')
print(f'SHA256: {sha256}')
print(f'MTime (UTC): {mtime.isoformat()}')
print(f'Journal Mode: {journal_mode}')
print(f'Integrity Check: {integrity}')
print(f'Quick Check: {quick}')
print(f'Total Tables: {len(tables)}')
total_rows = sum(row_counts.values())
print(f'Total Rows: {total_rows}')
for t, c in row_counts.items():
    print(f'  {t}: {c}')
print('Saved items rows:')
for r in saved_items_rows:
    print(' ', r)


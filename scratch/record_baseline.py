import os
import hashlib
import sqlite3
import datetime

db_path = 'backend/architect_ai.db'
size = os.path.getsize(db_path)
mtime = datetime.datetime.fromtimestamp(os.path.getmtime(db_path), tz=datetime.timezone.utc)
with open(db_path, 'rb') as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()

conn = sqlite3.connect(f'file:{os.path.abspath(db_path)}?mode=ro', uri=True)
cur = conn.cursor()
integrity = cur.execute('PRAGMA integrity_check;').fetchall()
quick = cur.execute('PRAGMA quick_check;').fetchall()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
row_counts = {t: cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tables}
conn.close()

print('=== PRE-PHASE 1.3.4 BASELINE ===')
print(f'Path: {os.path.abspath(db_path)}')
print(f'Size: {size}')
print(f'SHA256: {sha256}')
print(f'MTime (UTC): {mtime.isoformat()}')
print(f'Integrity: {integrity}')
print(f'Quick: {quick}')
print(f'Tables ({len(tables)}): total_rows={sum(row_counts.values())}')


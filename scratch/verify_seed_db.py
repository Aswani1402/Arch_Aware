import sqlite3

conn = sqlite3.connect('file:backend/seed_catalogue.sqlite?mode=ro', uri=True)
cur = conn.cursor()

tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()]
print('Seed Tables:', tables)

row_counts = {}
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t}"')
    row_counts[t] = cur.fetchone()[0]

for t, c in row_counts.items():
    print(f'  {t}: {c}')

print('Total seed rows:', sum(row_counts.values()))

integrity = cur.execute('PRAGMA integrity_check;').fetchall()
quick = cur.execute('PRAGMA quick_check;').fetchall()
fk_check = cur.execute('PRAGMA foreign_key_check;').fetchall()

print('Integrity:', integrity)
print('Quick Check:', quick)
print('Foreign Key Violations:', len(fk_check), fk_check)

print('\nSample Manufacturer Contacts (Commercial/Corporate):')
cur.execute('SELECT id, name, contact_info, source_url FROM manufacturers LIMIT 5;')
for m in cur.fetchall():
    print(' ', m)

conn.close()


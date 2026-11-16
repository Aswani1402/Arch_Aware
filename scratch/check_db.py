import sqlite3

c = sqlite3.connect('backend/architect_ai.db')
cur = c.cursor()
tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
print(f"Total tables: {len(tables)}")
for (t,) in tables:
    cnt = cur.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
    print(f"  {t}: {cnt}")
c.close()

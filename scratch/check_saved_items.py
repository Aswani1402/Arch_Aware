import sqlite3

conn = sqlite3.connect("file:backend/architect_ai.db?mode=ro", uri=True)
cur = conn.cursor()
rows = cur.execute("SELECT * FROM saved_items").fetchall()
print("saved_items rows in architect_ai.db:")
for r in rows:
    print(" ", r)

# Check all tables and row counts
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;").fetchall()]
print("\nTable counts:")
total = 0
for t in tables:
    c = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    total += c
    print(f"  {t:30}: {c}")
print(f"Total rows: {total}")
conn.close()


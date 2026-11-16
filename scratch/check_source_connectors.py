import sqlite3

conn = sqlite3.connect("file:backend/architect_ai.db?mode=ro", uri=True)
cur = conn.cursor()
cols = [c[1] for c in cur.execute("PRAGMA table_info(source_connectors);").fetchall()]
print(f"source_connectors columns: {cols}")
conn.close()


import sqlite3
import os

db_path = "architect_ai.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cur.fetchall()]
print(f"Database: {os.path.abspath(db_path)} ({os.path.getsize(db_path)} bytes)")
print("Tables and counts:")
for t in sorted(tables):
    try:
        count = cur.execute(f"SELECT count(*) FROM [{t}]").fetchone()[0]
        print(f"  {t}: {count}")
    except Exception as e:
        print(f"  {t}: ERROR ({e})")
conn.close()

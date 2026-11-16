import sqlite3
import hashlib
import os

def inspect_db(path):
    print(f"=== INSPECTING {path} ===")
    if not os.path.exists(path):
        print("FILE NOT FOUND")
        return
    with open(path, "rb") as f:
        data = f.read()
    size = len(data)
    sha = hashlib.sha256(data).hexdigest()
    print(f"Size: {size}")
    print(f"SHA-256: {sha}")

    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("PRAGMA integrity_check;")
    print(f"integrity_check: {cur.fetchall()}")
    cur.execute("PRAGMA quick_check;")
    print(f"quick_check: {cur.fetchall()}")
    cur.execute("PRAGMA foreign_key_check;")
    fk = cur.fetchall()
    print(f"foreign_key_check: {len(fk)} violations ({fk[:5]})")
    cur.execute("PRAGMA journal_mode;")
    print(f"journal_mode: {cur.fetchone()[0]}")

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
    tables = [row[0] for row in cur.fetchall()]
    print(f"Total tables: {len(tables)}")
    total_rows = 0
    breakdown = {}
    for t in tables:
        cur.execute(f'SELECT COUNT(*) FROM "{t}";')
        cnt = cur.fetchone()[0]
        breakdown[t] = cnt
        total_rows += cnt
        print(f"  {t}: {cnt}")
    print(f"SUM OF ROWS: {total_rows}")
    conn.close()
    return size, sha, len(tables), total_rows, breakdown

if __name__ == "__main__":
    inspect_db("backend/architect_ai.db")
    print()
    inspect_db("backend/seed_catalogue.sqlite")


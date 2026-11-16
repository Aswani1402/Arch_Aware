import os
import sqlite3

def run_migration():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(root, "architect_ai.db")
    if not os.path.exists(db_path):
        db_path = os.path.join(root, "backend", "architect_ai.db")

    print(f"[Migration] Opening database at: {db_path}")
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # 1. Check if is_demo column already exists
    cur.execute("PRAGMA table_info(suppliers)")
    columns = [col[1] for col in cur.fetchall()]
    if "is_demo" not in columns:
        print("[Migration] Adding is_demo column to suppliers table...")
        cur.execute("ALTER TABLE suppliers ADD COLUMN is_demo BOOLEAN DEFAULT 0")
        con.commit()
    else:
        print("[Migration] is_demo column already exists in suppliers table.")

    # 2. Mark demo suppliers (IDs 1-24, 47-54, 75-78)
    demo_ids = list(range(1, 25)) + list(range(47, 55)) + list(range(75, 79))
    placeholders = ",".join("?" for _ in demo_ids)
    cur.execute(f"UPDATE suppliers SET is_demo = 1 WHERE id IN ({placeholders})", demo_ids)
    cur.execute(f"UPDATE suppliers SET is_demo = 0 WHERE id NOT IN ({placeholders})", demo_ids)
    con.commit()

    # 3. Verify counts
    cur.execute("SELECT is_demo, count(*) FROM suppliers GROUP BY is_demo")
    breakdown = cur.fetchall()
    print("[Migration] Suppliers breakdown by is_demo:", breakdown)

    cur.execute("SELECT count(*) FROM suppliers")
    total = cur.fetchone()[0]
    print(f"[Migration] Total suppliers verified: {total}")
    assert total == 78, f"Supplier count changed! Expected 78, got {total}"

    con.close()
    print("[Migration] Done safely and additively.")

if __name__ == "__main__":
    run_migration()

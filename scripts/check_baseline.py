import os
import sqlite3
import hashlib

def sha256_file(path: str) -> str:
    if not os.path.exists(path):
        return "FILE NOT FOUND"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def check_baseline():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(root, "backend", "architect_ai.db")
    seed_path = os.path.join(root, "backend", "seed_catalogue.sqlite")

    print("=" * 60)
    print("MATERIQ BASELINE VERIFICATION REPORT")
    print("=" * 60)

    db_sha = sha256_file(db_path)
    seed_sha = sha256_file(seed_path)
    print(f"backend/architect_ai.db SHA-256:     {db_sha}")
    print(f"backend/seed_catalogue.sqlite SHA-256: {seed_sha}")

    if not os.path.exists(db_path):
        print(f"ERROR: {db_path} does not exist!")
        return False

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    tables = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

    counts = {}
    for table in ["catalogue_materials", "suppliers", "users", "saved_items"]:
        if table in tables:
            cnt = cur.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            counts[table] = cnt
        else:
            counts[table] = "TABLE MISSING"
    con.close()

    print("\nROW COUNTS:")
    for t, cnt in counts.items():
        print(f"  - {t:<22}: {cnt}")

    # Integrity assertions
    assert counts.get("catalogue_materials") == 6319, f"Expected 6319 catalogue materials, got {counts.get('catalogue_materials')}"
    assert counts.get("suppliers") == 78, f"Expected 78 suppliers, got {counts.get('suppliers')}"
    assert counts.get("users") >= 1, "Users table is empty"
    print("\nSTATUS: VERIFIED (All baseline constraints satisfied: 6,319 materials, 78 suppliers, databases intact)")
    print("=" * 60)
    return True

if __name__ == "__main__":
    check_baseline()

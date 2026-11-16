import sqlite3

def get_saved_items(db_path):
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cur = conn.cursor()
    rows = cur.execute("SELECT id, user_id, item_type, reference_id, product_id, supplier_id, project_collection, created_at FROM saved_items ORDER BY id").fetchall()
    conn.close()
    return rows

current_rows = get_saved_items("backend/architect_ai.db")
backup_rows = get_saved_items("backend/architect_ai.db.backup_phase_a_pre")

print("=== CURRENT saved_items in backend/architect_ai.db ===")
for r in current_rows:
    print(" ", r)

print("\n=== BACKUP saved_items in backend/architect_ai.db.backup_phase_a_pre ===")
for r in backup_rows:
    print(" ", r)

# Check byte offset 270194 in both files
with open("backend/architect_ai.db", "rb") as f1, open("backend/architect_ai.db.backup_phase_a_pre", "rb") as f2:
    f1.seek(270170)
    b1 = f1.read(60)
    f2.seek(270170)
    b2 = f2.read(60)

print("\n=== RAW BYTES ON PAGE 66 (OFFSET 270170 - 270230) ===")
print("Current bytes:", b1)
print("Backup  bytes:", b2)


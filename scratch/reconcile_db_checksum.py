import os
import hashlib
import sqlite3

db_path = "backend/architect_ai.db"
backup_path = "backend/architect_ai.db.backup_phase_a_pre"

def get_db_info(path):
    if not os.path.exists(path):
        return None
    stat = os.stat(path)
    with open(path, "rb") as f:
        data = f.read()
        sha256 = hashlib.sha256(data).hexdigest()
        header = data[:100]
    
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    cur = conn.cursor()
    journal_mode = cur.execute("PRAGMA journal_mode;").fetchone()[0]
    integrity = cur.execute("PRAGMA integrity_check;").fetchall()
    quick = cur.execute("PRAGMA quick_check;").fetchall()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;").fetchall()]
    row_counts = {t: cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tables}
    conn.close()

    change_counter = int.from_bytes(header[24:28], "big")
    schema_cookie = int.from_bytes(header[40:44], "big")
    file_format_write = header[18]
    file_format_read = header[19]

    return {
        "path": path,
        "size": stat.st_size,
        "sha256": sha256,
        "journal_mode": journal_mode,
        "integrity": integrity,
        "quick": quick,
        "tables": row_counts,
        "total_rows": sum(row_counts.values()),
        "change_counter": change_counter,
        "schema_cookie": schema_cookie,
        "header_info": {
            "write_version": file_format_write,
            "read_version": file_format_read,
        }
    }

current_info = get_db_info(db_path)
backup_info = get_db_info(backup_path)

print("=== CURRENT DATABASE ===")
print("Path:", current_info["path"])
print("Size:", current_info["size"])
print("SHA256:", current_info["sha256"])
print("Journal Mode:", current_info["journal_mode"])
print("Integrity Check:", current_info["integrity"])
print("Quick Check:", current_info["quick"])
print("Change Counter:", current_info["change_counter"])
print("Schema Cookie:", current_info["schema_cookie"])
print("Total Tables:", len(current_info["tables"]))
print("Total Rows:", current_info["total_rows"])

print("\n=== BACKUP PRE-PHASE A DATABASE ===")
if backup_info:
    print("Path:", backup_info["path"])
    print("Size:", backup_info["size"])
    print("SHA256:", backup_info["sha256"])
    print("Change Counter:", backup_info["change_counter"])
    print("Schema Cookie:", backup_info["schema_cookie"])
    print("Total Rows:", backup_info["total_rows"])

# Check byte differences between current and backup if backup exists
if backup_info:
    with open(db_path, "rb") as f1, open(backup_path, "rb") as f2:
        d1 = f1.read()
        d2 = f2.read()
    
    diffs = []
    for i in range(min(len(d1), len(d2))):
        if d1[i] != d2[i]:
            diffs.append((i, d1[i], d2[i]))
    print(f"\nByte differences count: {len(diffs)}")
    if diffs:
        print("First 20 byte differences (offset, current, backup):")
        for d in diffs[:20]:
            print(f"  Offset {d[0]} (0x{d[0]:x}): current=0x{d[1]:02x}, backup=0x{d[2]:02x}")


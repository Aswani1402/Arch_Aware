import sqlite3
import json

conn = sqlite3.connect('file:backend/architect_ai.db?mode=ro', uri=True)
cursor = conn.cursor()
tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]

schema_info = {}

for t in tables:
    count = cursor.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    cols = cursor.execute(f'PRAGMA table_info("{t}")').fetchall()
    # cols format: (cid, name, type, notnull, dflt_value, pk)
    fks = cursor.execute(f'PRAGMA foreign_key_list("{t}")').fetchall()
    # fks format: (id, seq, table, from, to, on_update, on_delete, match)
    indices = cursor.execute(f'PRAGMA index_list("{t}")').fetchall()
    # indices: (seq, name, unique, origin, partial)
    sql = cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone()[0]
    
    schema_info[t] = {
        "count": count,
        "columns": [{"name": c[1], "type": c[2], "notnull": bool(c[3]), "default": c[4], "pk": c[5]} for c in cols],
        "foreign_keys": [{"target_table": fk[2], "from": fk[3], "to": fk[4], "on_update": fk[5], "on_delete": fk[6]} for fk in fks],
        "indices": [{"name": idx[1], "unique": bool(idx[2])} for idx in indices],
        "sql": sql
    }

conn.close()

with open('scratch/schema_inspection.json', 'w', encoding='utf-8') as f:
    json.dump(schema_info, f, indent=2)

print(f"Inspected {len(tables)} tables.")
for t, data in schema_info.items():
    print(f"Table: {t:30} Rows: {data['count']:5} FKs: {len(data['foreign_keys'])}")


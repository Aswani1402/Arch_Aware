import sqlite3

conn = sqlite3.connect('file:backend/architect_ai.db?mode=ro', uri=True)
cursor = conn.cursor()
r = cursor.execute("SELECT id, title, slug FROM architectural_references WHERE slug LIKE '%drainage%' OR slug LIKE '%kanyakumari%'").fetchall()
print('Found references:', r)

# check min/max id in architectural_references
min_max = cursor.execute("SELECT MIN(id), MAX(id), COUNT(*) FROM architectural_references").fetchone()
print(f"Architectural references: min={min_max[0]}, max={min_max[1]}, count={min_max[2]}")

# check what happened to id 16
id_16 = cursor.execute("SELECT id FROM architectural_references WHERE id=16").fetchone()
print("ID 16 exists?:", id_16)

# check ids around 15-20
around = cursor.execute("SELECT id, slug FROM architectural_references WHERE id BETWEEN 14 AND 20").fetchall()
print("IDs 14-20 in architectural_references:", around)

conn.close()


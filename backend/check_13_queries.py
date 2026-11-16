import sqlite3

queries = [
    'brick', 'drainage', 'cement', 'bedroom', 'lighting',
    'marble', 'tiles', 'garden waterfall', 'decorative pots',
    'garden pathway', 'bathroom renovation', 'kitchen design', 'boundary wall'
]

conn = sqlite3.connect('architect_ai.db')
cur = conn.cursor()

print("Checking 13 required test queries in current DB:")
for q in queries:
    words = q.lower().split()
    clauses = ' AND '.join([f'(LOWER(title) LIKE "%{w}%" OR LOWER(description) LIKE "%{w}%" OR LOWER(material_tags) LIKE "%{w}%")' for w in words])
    cur.execute(f'SELECT id, title, material_tags FROM architectural_references WHERE {clauses}')
    rows = cur.fetchall()
    print(f"=== Query: '{q}' -> {len(rows)} matches ===")
    for r in rows[:3]:
        print(f"   [{r[0]}] {r[1][:65]}")

conn.close()

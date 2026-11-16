import sqlite3

conn = sqlite3.connect('file:backend/architect_ai.db?mode=ro', uri=True)
cur = conn.cursor()

print("=== DUPLICATE TITLES IN architectural_references ===")
cur.execute('''
    SELECT title, COUNT(*) as cnt, GROUP_CONCAT(id) as ids, source_platform
    FROM architectural_references
    GROUP BY lower(trim(title))
    HAVING cnt > 1
    ORDER BY cnt DESC
    LIMIT 20;
''')
dups = cur.fetchall()
print(f"Total duplicate title groups: {len(dups)}")
for d in dups:
    print(f"  Count: {d[1]} | IDs: {d[2]} | Platform: {d[3]} | Title: {d[0][:80]}")

print("\n=== TOTAL REFERENCES BY PLATFORM ===")
cur.execute('''
    SELECT source_platform, COUNT(*)
    FROM architectural_references
    GROUP BY source_platform
    ORDER BY COUNT(*) DESC;
''')
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} records")

conn.close()


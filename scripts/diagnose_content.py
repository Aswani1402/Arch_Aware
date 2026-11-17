import sqlite3

conn = sqlite3.connect("backend/architect_ai.db")
c = conn.cursor()

c.execute("SELECT count(*) FROM architectural_references")
print("Total architectural_references:", c.fetchone()[0])

for term in ["machin", "tool", "paint", "door", "window", "floor", "brick", "concrete"]:
    c.execute(f"SELECT count(*) FROM architectural_references WHERE title LIKE '%{term}%' OR search_keyword LIKE '%{term}%'")
    print(f"Matches for '{term}':", c.fetchone()[0])

c.execute("SELECT source_platform, count(*) FROM architectural_references GROUP BY source_platform")
print("\nBy platform:", c.fetchall())

conn.close()

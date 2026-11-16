import sqlite3

conn = sqlite3.connect('file:backend/architect_ai.db?mode=ro', uri=True)
cursor = conn.cursor()

print("=== ALL 20 MANUFACTURERS ===")
rows = cursor.execute("SELECT id, name, company_name, official_website, contact_info FROM manufacturers").fetchall()
for r in rows:
    print(f"ID: {r[0]:2d} | {r[1]:35} | Website: {str(r[3])[:30]:30} | Contact: {r[4]}")

conn.close()


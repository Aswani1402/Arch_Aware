import sqlite3
import re

conn = sqlite3.connect('file:backend/architect_ai.db?mode=ro', uri=True)
cursor = conn.cursor()

email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
phone_regex = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')

rows = cursor.execute("SELECT id, name, element_location, notes, detail_image_url FROM inspiration_materials").fetchall()

email_hits = []
phone_hits = []

for r in rows:
    text = f"{r[1]} {r[2]} {r[3]} {r[4]}"
    if email_regex.search(text):
        email_hits.append(r[0])
    if phone_regex.search(text):
        phone_hits.append(r[0])

print(f"inspiration_materials rows inspected: {len(rows)}")
print(f"Email hits: {len(email_hits)}")
print(f"Phone hits: {len(phone_hits)}")

conn.close()


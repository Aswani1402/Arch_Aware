import os
import re

terms = [
    'Heritage Crafts',
    'PINTEREST Specimen',
    'Pinterest Preview',
    'Aathangudi',
    'CURATED_PINTEREST_REFERENCES',
    'CURATED_REDDIT_REFERENCES',
    'CURATED_INSTAGRAM_REFERENCES'
]

print("=== SEARCHING CODEBASE FOR CURATED CONTENT STRINGS ===")
for section in ['backend', 'frontend']:
    for root, dirs, files in os.walk(section):
        if any(ig in root for ig in ['node_modules', '.next', 'venv', '__pycache__']):
            continue
        for f in files:
            if f.endswith(('.py', '.tsx', '.ts', '.json', '.sql')):
                p = os.path.join(root, f)
                try:
                    with open(p, encoding='utf-8', errors='ignore') as fh:
                        content = fh.read()
                    for term in terms:
                        if term.lower() in content.lower():
                            for idx, line in enumerate(content.splitlines(), 1):
                                if term.lower() in line.lower():
                                    print(f"[{term}] in {p}:{idx} -> {line.strip()[:100]}")
                except Exception:
                    pass

print("\n=== SEARCHING SQLITE DATABASE FOR Aathangudi and Heritage Crafts ===")
import sqlite3
conn = sqlite3.connect('file:backend/architect_ai.db?mode=ro', uri=True)
cur = conn.cursor()
for term in ['Heritage Crafts', 'Aathangudi', 'Athangudi', 'Specimen']:
    cur.execute(f"SELECT id, title, source_platform, creator_name FROM architectural_references WHERE title LIKE '%{term}%' OR description LIKE '%{term}%' LIMIT 10;")
    rows = cur.fetchall()
    print(f"architectural_references matches for '{term}': {len(rows)}")
    for r in rows:
        print(" ", r)
conn.close()


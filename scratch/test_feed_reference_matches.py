import sqlite3

conn = sqlite3.connect('backend/architect_ai.db')
c = conn.cursor()

queries = ['Fly ash brick', 'Hollow concrete block', 'Marble flooring', 'Laterite stone']
for q in queries:
    words = [w.lower() for w in q.split() if len(w) >= 2]
    clauses = []
    params = []
    for w in words:
        clauses.append('(title LIKE ? OR material_tags LIKE ? OR description LIKE ?)')
        params.extend([f'%{w}%', f'%{w}%', f'%{w}%'])
    where = ' OR '.join(clauses)
    c.execute(f'SELECT id, title, source_platform, material_tags FROM architectural_references WHERE {where} LIMIT 5', params)
    rows = c.fetchall()
    c.execute(f'SELECT COUNT(*) FROM architectural_references WHERE {where}', params)
    cnt = c.fetchone()[0]
    print(f'=== Query: "{q}" -> {cnt} matches in architectural_references ===')
    for r in rows:
        print(f'   ID {r[0]}: "{r[1]}" ({r[2]}) [tags: {r[3]}]')

conn.close()


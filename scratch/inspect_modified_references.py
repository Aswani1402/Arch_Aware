import sqlite3

src_conn = sqlite3.connect('file:backend/architect_ai.db?mode=ro', uri=True)
dst_conn = sqlite3.connect('file:backend/seed_catalogue.sqlite?mode=ro', uri=True)

src_cur = src_conn.cursor()
dst_cur = dst_conn.cursor()

src_rows = {r[0]: (r[1] or "", r[2] or "") for r in src_cur.execute('SELECT id, title, description FROM architectural_references ORDER BY id').fetchall()}
dst_rows = {r[0]: (r[1] or "", r[2] or "") for r in dst_cur.execute('SELECT id, title, description FROM architectural_references ORDER BY id').fetchall()}

src_conn.close()
dst_conn.close()

modified = []
for rid, (s_title, s_desc) in src_rows.items():
    d_title, d_desc = dst_rows[rid]
    if s_title != d_title or s_desc != d_desc:
        modified.append((rid, s_title, d_title, s_desc, d_desc))

print(f'Total modified architectural_references in seed: {len(modified)}')
for rid, st, dt, sd, dd in modified:
    print(f'\n--- Ref ID {rid} ---')
    if st != dt:
        print(f'  TITLE BEFORE: {st}')
        print(f'  TITLE AFTER:  {dt}')
    if sd != dd:
        print(f'  DESC BEFORE:  {sd[:140]}...')
        print(f'  DESC AFTER:   {dd[:140]}...')


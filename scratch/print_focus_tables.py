import json

with open('scratch/schema_inspection.json') as f:
    data = json.load(f)

focus_tables = ['inspiration_materials', 'manufacturers', 'material_categories', 'products', 'source_connectors']

for t in focus_tables:
    d = data[t]
    print(f"=== {t} (rows: {d['count']}) ===")
    cols = [c['name'] + (f" [{c['type']}]" if c['type'] else "") + (" (PK)" if c['pk'] else "") for c in d['columns']]
    print(f"  Cols ({len(cols)}): {', '.join(cols)}")
    if d['foreign_keys']:
        for fk in d['foreign_keys']:
            print(f"  FK: {fk['from']} -> {fk['target_table']}.{fk['to']}")
    if d['indices']:
        idx_names = [i['name'] + (' (UNIQUE)' if i['unique'] else '') for i in d['indices']]
        print(f"  Indices: {', '.join(idx_names)}")
    print()


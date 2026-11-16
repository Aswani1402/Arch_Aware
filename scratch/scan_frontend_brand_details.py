import os
import re

frontend_dir = 'frontend'
results = []

for root, dirs, files in os.walk(frontend_dir):
    # skip node_modules and .next
    if 'node_modules' in root or '.next' in root:
        continue
    for f in files:
        if f.endswith(('.tsx', '.ts', '.html', '.json', '.md')):
            fpath = os.path.join(root, f)
            try:
                with open(fpath, 'r', encoding='utf-8') as fp:
                    lines = fp.readlines()
                for i, line in enumerate(lines):
                    if re.search(r'\b(nivora|architect\s*ai)\b', line, re.IGNORECASE):
                        # Determine context
                        results.append({
                            'file': fpath.replace('\\', '/'),
                            'line': i + 1,
                            'text': line.strip()
                        })
            except Exception as e:
                pass

print(f"Total occurrences found in frontend: {len(results)}")
# Group by file
files_map = {}
for r in results:
    files_map.setdefault(r['file'], []).append(r)

for fpath, items in files_map.items():
    print(f"\n{fpath} ({len(items)} occurrences):")
    for it in items[:4]:
        print(f"  L{it['line']}: {it['text'][:100]}")


import os
import re

patterns = {
    'NIVORA': re.compile(r'\bnivora\b', re.IGNORECASE),
    'Architect AI': re.compile(r'architect[\s_-]?ai', re.IGNORECASE),
}

results = {'frontend': [], 'backend': []}

for section in ['frontend', 'backend']:
    for root, dirs, files in os.walk(section):
        if any(ignored in root for ignored in ['.next', 'node_modules', 'venv', '__pycache__', '.git']):
            continue
        for f in files:
            if f.endswith(('.tsx', '.ts', '.js', '.jsx', '.json', '.py', '.html', '.css', '.md', '.yaml', '.yml', '.env', '.example')):
                p = os.path.join(root, f)
                try:
                    with open(p, encoding='utf-8', errors='ignore') as fh:
                        for line_no, line in enumerate(fh, 1):
                            for pat_name, pat in patterns.items():
                                if pat.search(line):
                                    results[section].append((p, line_no, pat_name, line.strip()))
                except Exception as e:
                    pass

print(f"Total occurrences in frontend: {len(results['frontend'])}")
print(f"Total occurrences in backend: {len(results['backend'])}")

# Group frontend by file
frontend_files = {}
for p, lno, pat, l in results['frontend']:
    frontend_files.setdefault(p, []).append((lno, pat, l))

print(f"\nUnique Frontend Files with old branding: {len(frontend_files)}")
for p, hits in sorted(frontend_files.items()):
    print(f"\nFile: {p} ({len(hits)} hits)")
    for lno, pat, l in hits[:5]:
        print(f"  L{lno} [{pat}]: {l[:90]}")
    if len(hits) > 5:
        print(f"  ... and {len(hits)-5} more lines")

# Group backend by file
backend_files = {}
for p, lno, pat, l in results['backend']:
    backend_files.setdefault(p, []).append((lno, pat, l))

print(f"\nUnique Backend Files with old branding: {len(backend_files)}")
for p, hits in sorted(backend_files.items()):
    print(f"\nFile: {p} ({len(hits)} hits)")
    for lno, pat, l in hits[:4]:
        print(f"  L{lno} [{pat}]: {l[:90]}")
    if len(hits) > 4:
        print(f"  ... and {len(hits)-4} more lines")


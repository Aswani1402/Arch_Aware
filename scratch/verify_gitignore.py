import fnmatch
from pathlib import Path

rules = []
with open('.gitignore') as f:
    for line in f:
        l = line.strip()
        if l and not l.startswith('#'):
            rules.append(l)

def is_ignored(path_str):
    p = path_str.replace('\\', '/')
    name = Path(p).name
    ignored = False
    for r in rules:
        if r.startswith('!'):
            pattern = r[1:].lstrip('/')
            if fnmatch.fnmatch(p, pattern) or fnmatch.fnmatch(name, pattern):
                ignored = False
        else:
            pattern = r.lstrip('/')
            if fnmatch.fnmatch(p, pattern) or fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(p, f"*/{pattern}"):
                ignored = True
    return ignored

test_files = [
    'backend/architect_ai.db',
    'architect_ai.db',
    'backend/architect_ai.db.backup_phase_a_pre',
    'backend/seed_catalogue.sqlite',
    'backend/seed_catalogue.backup_20261113.sqlite',
    '.env',
    'backend/.env',
    'render.yaml',
]

print("=== GITIGNORE MATCHING SIMULATION ===")
for tf in test_files:
    status = "IGNORED" if is_ignored(tf) else "ELIGIBLE TO TRACK"
    print(f"{tf:45}: {status}")


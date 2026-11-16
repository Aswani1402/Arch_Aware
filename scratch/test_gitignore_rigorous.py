import fnmatch
from pathlib import PurePath

gitignore_rules = [
    ".env",
    ".env.local",
    ".env.*.local",
    "__pycache__/",
    "*.py[cod]",
    "*$py.class",
    "venv/",
    ".pytest_cache/",
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "!backend/seed_catalogue.sqlite",
    "*.backup*",
    "*.pre",
    "*.bak",
    "node_modules/",
    ".next/",
    "out/",
    "build/",
    "dist/",
    ".DS_Store",
    "Thumbs.db",
    ".idea/",
    ".vscode/",
]

test_paths = [
    "backend/architect_ai.db",
    "backend/architect_ai.db.backup_phase_a_pre",
    "backend/seed_catalogue.sqlite",
    "backend/seed_catalogue.backup_20261113_213712.sqlite",
    ".env",
    "backend/.env",
]

def evaluate_gitignore(path: str, rules: list) -> tuple:
    p = PurePath(path)
    matched_rule = None
    ignored = False

    for rule in rules:
        rule_clean = rule.strip()
        if not rule_clean or rule_clean.startswith("#"):
            continue

        is_negated = rule_clean.startswith("!")
        pattern = rule_clean[1:] if is_negated else rule_clean

        # Trailing slash means dir only
        dir_only = pattern.endswith("/")
        if dir_only:
            pattern = pattern[:-1]

        # Check if pattern matches basename or full path
        match = False
        if "/" in pattern:
            # Matches full path relative to root
            match = fnmatch.fnmatch(str(p).replace("\\", "/"), pattern)
        else:
            match = fnmatch.fnmatch(p.name, pattern)

        if match:
            if is_negated:
                ignored = False
                matched_rule = f"!{pattern} (re-included)"
            else:
                ignored = True
                matched_rule = pattern

    return ignored, matched_rule

print("=== GITIGNORE PATTERN EVALUATION ===")
for tp in test_paths:
    ign, rule = evaluate_gitignore(tp, gitignore_rules)
    status = "IGNORED" if ign else "TRACKED (ELIGIBLE)"
    print(f"{tp:<52} : {status:<18} [Rule: {rule}]")


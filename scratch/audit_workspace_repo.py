import os
import glob
from pathlib import Path

repo_root = Path(".").resolve()

# 1. Check Git repository
git_dir = repo_root / ".git"
has_git = git_dir.exists()

print("=== WORKSPACE & REPOSITORY AUDIT ===")
print(f"Project root: {repo_root}")
print(f"Git repo exists: {has_git}")

# 2. Check key files existence
key_files = [
    "render.yaml",
    ".gitignore",
    ".env",
    "backend/.env",
    ".env.example",
    "backend/.env.example",
    "backend/requirements.txt",
    "frontend/package.json",
    "backend/app/main.py",
    "backend/app/core/database.py",
    "backend/architect_ai.db",
    "backend/seed_catalogue.sqlite",
]

for kf in key_files:
    p = repo_root / kf
    print(f"File {kf:<35}: {'EXISTS' if p.exists() else 'MISSING'}")

# 3. Check for any database backup files
backups = glob.glob("**/*.bak*", recursive=True) + glob.glob("**/*.backup*", recursive=True) + glob.glob("**/*.pre*", recursive=True)
print(f"\nFound {len(backups)} backup files:")
for b in backups:
    print(f"  {b}")

# 4. Check .env files and permissions/presence
env_files = glob.glob("**/.env*", recursive=True)
print(f"\nFound {len(env_files)} env files:")
for ef in env_files:
    if "node_modules" not in ef and "venv" not in ef:
        print(f"  {ef} ({os.path.getsize(ef)} bytes)")


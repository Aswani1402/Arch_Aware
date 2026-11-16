import os
import shutil
import hashlib
import datetime

SOURCE_DIR = r"C:\Users\Aswini_Ayappan\OneDrive\Desktop\Architect_AI"
BACKUPS_PARENT = r"C:\Users\Aswini_Ayappan\OneDrive\Desktop\Architect_AI_Backups"

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
TARGET_DIR = os.path.join(BACKUPS_PARENT, f"backup_pre_stage1_{timestamp}")

EXCLUDE_DIRS = {
    ".next",
    "node_modules",
    ".pytest_cache",
    "__pycache__",
    "venv",
    ".git"
}

def get_file_hash(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

print(f"Creating backup directory: {TARGET_DIR}")
os.makedirs(TARGET_DIR, exist_ok=False)

total_files = 0
total_bytes = 0

for root, dirs, files in os.walk(SOURCE_DIR):
    # filter out excluded dirs
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    
    rel_path = os.path.relpath(root, SOURCE_DIR)
    if rel_path == ".":
        dest_dir = TARGET_DIR
    else:
        dest_dir = os.path.join(TARGET_DIR, rel_path)
        os.makedirs(dest_dir, exist_ok=True)
        
    for f in files:
        src_file = os.path.join(root, f)
        dest_file = os.path.join(dest_dir, f)
        try:
            shutil.copy2(src_file, dest_file)
            total_files += 1
            total_bytes += os.path.getsize(dest_file)
        except Exception as e:
            print(f"Error copying {src_file}: {e}")

print(f"Backup completed.")
print(f"Total files copied: {total_files}")
print(f"Total size: {total_bytes} bytes ({total_bytes / (1024*1024):.2f} MB)")

# Verify Databases
db1_src = os.path.join(SOURCE_DIR, "backend", "architect_ai.db")
db1_dst = os.path.join(TARGET_DIR, "backend", "architect_ai.db")
db2_src = os.path.join(SOURCE_DIR, "backend", "seed_catalogue.sqlite")
db2_dst = os.path.join(TARGET_DIR, "backend", "seed_catalogue.sqlite")

db1_src_hash = get_file_hash(db1_src)
db1_dst_hash = get_file_hash(db1_dst)
db2_src_hash = get_file_hash(db2_src)
db2_dst_hash = get_file_hash(db2_dst)

print("\n--- DATABASE VERIFICATION ---")
print(f"architect_ai.db Source: {db1_src_hash}")
print(f"architect_ai.db Backup: {db1_dst_hash}")
print(f"Match: {db1_src_hash == db1_dst_hash}")

print(f"seed_catalogue.sqlite Source: {db2_src_hash}")
print(f"seed_catalogue.sqlite Backup: {db2_dst_hash}")
print(f"Match: {db2_src_hash == db2_dst_hash}")

# Check critical files in backup
critical_files = [
    os.path.join(TARGET_DIR, "frontend", "lib", "brandConfig.ts"),
    os.path.join(TARGET_DIR, "frontend", "app", "page.tsx"),
    os.path.join(TARGET_DIR, "backend", "app", "main.py"),
    os.path.join(TARGET_DIR, "backend", "app", "core", "config.py"),
    os.path.join(TARGET_DIR, "backend", ".env"),
    os.path.join(TARGET_DIR, ".env"),
]

print("\n--- CRITICAL FILES VERIFICATION ---")
for cf in critical_files:
    exists = os.path.isfile(cf)
    print(f"{os.path.basename(cf)} ({os.path.dirname(cf)[len(TARGET_DIR)+1:]}): {'EXISTS' if exists else 'MISSING'}")

print(f"\nBACKUP_PATH={TARGET_DIR}")


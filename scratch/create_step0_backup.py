import os
import shutil
import hashlib
import datetime
import sys

SOURCE_DIR = r"C:\Users\Aswini_Ayappan\OneDrive\Desktop\Architect_AI"
BACKUPS_BASE = r"C:\Users\Aswini_Ayappan\OneDrive\Desktop\Architect_AI_Backups"

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
TARGET_DIR = os.path.join(BACKUPS_BASE, f"backup_pre_phase1_{timestamp}")

EXCLUDE_DIRS = {
    ".next",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".git"
}

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

print(f"Creating backup directory: {TARGET_DIR}")
os.makedirs(TARGET_DIR, exist_ok=False)

copied_files = 0
copied_bytes = 0

for root, dirs, files in os.walk(SOURCE_DIR):
    # Exclude directories
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    
    # Calculate relative path
    rel_path = os.path.relpath(root, SOURCE_DIR)
    dest_dir = os.path.join(TARGET_DIR, rel_path)
    os.makedirs(dest_dir, exist_ok=True)
    
    for f in files:
        src_file = os.path.join(root, f)
        dest_file = os.path.join(dest_dir, f)
        try:
            shutil.copy2(src_file, dest_file)
            copied_files += 1
            copied_bytes += os.path.getsize(src_file)
        except Exception as e:
            print(f"ERROR copying {src_file}: {e}")
            sys.exit(1)

print(f"Total files copied: {copied_files}")
print(f"Total backup size: {copied_bytes} bytes ({copied_bytes / (1024*1024):.2f} MB)")

# Verify Databases
orig_db = os.path.join(SOURCE_DIR, "backend", "architect_ai.db")
orig_seed = os.path.join(SOURCE_DIR, "backend", "seed_catalogue.sqlite")

backup_db = os.path.join(TARGET_DIR, "backend", "architect_ai.db")
backup_seed = os.path.join(TARGET_DIR, "backend", "seed_catalogue.sqlite")

if not os.path.exists(backup_db) or not os.path.exists(backup_seed):
    print("FATAL: Databases missing in backup!")
    sys.exit(1)

sha_orig_db = sha256_file(orig_db)
sha_backup_db = sha256_file(backup_db)

sha_orig_seed = sha256_file(orig_seed)
sha_backup_seed = sha256_file(backup_seed)

print("\n--- DATABASE VERIFICATION ---")
print(f"Original DB SHA-256:  {sha_orig_db}")
print(f"Backup DB SHA-256:    {sha_backup_db}")
print(f"Original Seed SHA256: {sha_orig_seed}")
print(f"Backup Seed SHA256:   {sha_backup_seed}")

BASELINE_ORIG_SHA = "f8c04d78a38ba917bd06dc69ff246d814949f46f8a70cc947a7c0d8d5f93b8a4"
BASELINE_SEED_SHA = "1a6c5438a696aec0e23eaf5e3fe5f121b0ed53534893064b962e11af32b4e8ca"

assert sha_orig_db == sha_backup_db == BASELINE_ORIG_SHA, "Original DB checksum mismatch!"
assert sha_orig_seed == sha_backup_seed == BASELINE_SEED_SHA, "Seed DB checksum mismatch!"

print("\n>>> STEP 0 BACKUP & VERIFICATION: 100% SUCCESS <<<")
print(f"Backup Location: {TARGET_DIR}")


import json
import os
import hashlib

def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

db_json = "backend/app/db/full_taxonomy.json"
test_json = "backend/app/tests/full_taxonomy.json"

print(f"DB JSON exists: {os.path.exists(db_json)} (Hash: {file_hash(db_json)[:12]})")
print(f"Test JSON exists: {os.path.exists(test_json)} (Hash: {file_hash(test_json)[:12]})")
print(f"Files identical: {file_hash(db_json) == file_hash(test_json)}")

with open(db_json, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Categories count in JSON: {data.get('categories_count')}")
print(f"Subcategories count in JSON: {data.get('subcategories_count')}")
print(f"Items count in JSON: {data.get('items_count')}")
print(f"Variants count in JSON: {data.get('variants_count')}")


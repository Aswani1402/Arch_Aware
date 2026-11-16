import glob
import re

files_to_check = [
    "backend/app/tests/test_bathroom_fittings_regression.py",
    "backend/app/tests/test_catalogue_import.py",
    "backend/app/tests/test_feed_personalization_regression.py",
    "backend/app/tests/test_live_apis_and_llm.py",
    "backend/app/tests/test_master_prompt_features.py",
    "backend/app/tests/test_phase9_cache_and_scheduler.py",
    "backend/app/tests/test_pinterest_integration.py",
    "backend/app/tests/test_socialcrawl_integration.py",
]

for f in files_to_check:
    print(f"=== {f} ===")
    lines = open(f, encoding="utf-8").readlines()
    for i, line in enumerate(lines, 1):
        if "TestClient" in line or "client." in line or "SessionLocal" in line:
            if any(verb in line for verb in ["post", "put", "patch", "delete", "SessionLocal()"]):
                print(f"  Line {i}: {line.strip()[:100]}")


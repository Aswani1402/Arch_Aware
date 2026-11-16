import sys
from fastapi.testclient import TestClient
from app.main import app
from app.tests.test_search_relevance_rigorous import QUERIES_CONFIG

client = TestClient(app)

print("=" * 80)
print("AUDITING 13 QUERIES WITH TESTCLIENT")
print("=" * 80)

total = len(QUERIES_CONFIG)
passed = 0
failed = 0

for q, rules in QUERIES_CONFIG.items():
    resp = client.get("/api/feed", params={"q": q, "page_size": 20})
    if resp.status_code != 200:
        print(f"[FAIL] HTTP {resp.status_code} on query '{q}'")
        failed += 1
        continue
    data = resp.json()
    items = data.get("items", [])
    print(f"\nQUERY: '{q}' -> {len(items)} results (expected >= {rules['min_expected_matches']})")
    
    if len(items) < rules["min_expected_matches"]:
        print(f"  [ERROR] Not enough matches: {len(items)} < {rules['min_expected_matches']}")
        failed += 1
        continue
        
    has_err = False
    for idx, item in enumerate(items, 1):
        title = item.get("title", "")
        desc = item.get("description", "")
        tags = item.get("material_tags", "")
        combined = f"{title} {desc} {tags}".lower()
        
        has_pos = any(ev.lower() in combined for ev in rules["required_evidence"])
        contamination = [fb for fb in rules["forbidden_evidence"] if fb.lower() in combined]
        
        if not has_pos:
            print(f"  [FAIL Result #{idx}] '{title}' missing positive evidence {rules['required_evidence']}")
            has_err = True
        if contamination:
            print(f"  [FAIL Result #{idx}] '{title}' contaminated with {contamination}")
            has_err = True
        if idx <= 2:
            print(f"  #{idx}: {title} (Tags: {tags})")
            
    if has_err:
        failed += 1
    else:
        passed += 1
        print(f"  [PASS] Clean query '{q}'")

print("\n" + "=" * 80)
print(f"RESULT: {passed}/{total} queries passed ({failed} failed)")
print("=" * 80)

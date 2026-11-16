import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.app.services.keyword_library import search_keyword_library, expand_search_query_with_synonyms

test_queries = [
    "Staircase",
    "Chandelier",
    "Kerala House Elevation",
    "Marble Flooring",
    "Modular Kitchen",
    "TMT Bars",
    "Athangudi Tiles",
    "Landscape Stones",
    "Wooden Doors",
    "Decorative Wall Panels"
]

print("=" * 80)
print("VERIFICATION OF 10 AUDIT KEYWORDS")
print("=" * 80)

all_passed = True
for q in test_queries:
    syns = expand_search_query_with_synonyms(q)
    results = search_keyword_library(q)
    passed = len(results) > 0
    if not passed:
        all_passed = False
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] Query: '{q}'")
    print(f"       Synonyms ({len(syns)}): {', '.join(syns[:5])}...")
    print(f"       Categories Matched: {len(results)}")
    for r in results[:2]:
        matched_subs = [m["subcategory"] for m in r.get("matches", [])]
        print(f"         - {r['category_name']} -> {', '.join(matched_subs[:3])}")
    print()

print(f"Overall Result: {'ALL 10 PASSED' if all_passed else 'SOME FAILED'}")


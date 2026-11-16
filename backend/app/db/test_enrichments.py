import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.app.services.keyword_library import search_keyword_library, expand_search_query_with_synonyms

additional_queries = [
    "HVAC",
    "CCTV",
    "Fire Extinguisher",
    "Office Furniture",
    "Curtains",
    "Rammed Earth",
    "Precast Concrete",
    "Excavator",
    "Water Storage Tank",
    "Architectural Drawings",
    "UltraTech Cement",
    "Tata Tiscon",
    "Kohler",
    "Kajaria",
    "Asian Paints"
]

print("=" * 80)
print("VERIFICATION OF DOMAIN CATALOGUE ENRICHMENTS (SECTIONS A-M & 5-14)")
print("=" * 80)

all_passed = True
for q in additional_queries:
    syns = expand_search_query_with_synonyms(q)
    results = search_keyword_library(q)
    passed = len(results) > 0
    if not passed:
        all_passed = False
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] Query: '{q}' -> {len(results)} category matches")
    for r in results[:2]:
        matched_subs = [m["subcategory"] for m in r.get("matches", [])]
        print(f"         - {r['category_name']} -> {', '.join(matched_subs[:3])}")

print(f"\nEnrichment Verification Result: {'ALL PASSED' if all_passed else 'SOME FAILED'}")


import sys
import os
import json
sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.main import app
from app.services.keyword_library import expand_search_query_with_synonyms

client = TestClient(app)

exact_10_terms = [
    "Staircase",
    "Kitchen",
    "Wardrobe",
    "Landscaping",
    "Exterior Facade",
    "Brick",
    "TMT Steel",
    "Athangudi Tiles",
    "Bathroom Fittings",
    "Lighting"
]

print("=" * 80)
print("TESTING EXACT ORIGINAL 10 KEYWORDS (PHASE 5A AUDIT)")
print("=" * 80)

audit_results = []

for term in exact_10_terms:
    print(f"\n>>> Keyword: '{term}'")
    # 1. Test Search API
    res_search = client.get(f"/api/categories/keywords/search?q={term}")
    search_data = res_search.json() if res_search.status_code == 200 else {}
    results = search_data.get("results", [])
    syns = expand_search_query_with_synonyms(term)

    is_recognized = len(results) > 0
    matched_cats = [r["category_name"] for r in results]
    matched_subs = []
    matched_items = []
    matched_variants = []

    for r in results:
        for m in r.get("matches", []):
            sub_name = m.get("subcategory")
            if sub_name and sub_name not in matched_subs:
                matched_subs.append(sub_name)
            for it in m.get("items", []):
                it_name = it.get("name")
                if it_name and it_name not in matched_items:
                    matched_items.append(it_name)
                for v in it.get("variants", []):
                    if v not in matched_variants:
                        matched_variants.append(v)

    # 2. Test Feed API
    res_feed = client.get(f"/api/feed?q={term}&page_size=10")
    feed_data = res_feed.json() if res_feed.status_code == 200 else {}
    feed_items = feed_data.get("items", [])
    feed_count = feed_data.get("total_count", len(feed_items))
    feed_titles = [f["title"] for f in feed_items[:3]]

    entry = {
        "term": term,
        "is_recognized": is_recognized,
        "categories_count": len(matched_cats),
        "categories": matched_cats,
        "subcategories_count": len(matched_subs),
        "subcategories": matched_subs,
        "items_count": len(matched_items),
        "items": matched_items,
        "variants_count": len(matched_variants),
        "variants": matched_variants[:6],
        "synonyms_count": len(syns),
        "synonyms": syns[:6],
        "feed_status_code": res_feed.status_code,
        "feed_total_results": feed_count,
        "feed_sample_titles": feed_titles
    }
    audit_results.append(entry)

    print(f"  Recognized: {is_recognized}")
    print(f"  Matched Categories ({len(matched_cats)}): {', '.join(matched_cats)}")
    print(f"  Matched Subcategories ({len(matched_subs)}): {', '.join(matched_subs)}")
    print(f"  Matched Items ({len(matched_items)}): {', '.join(matched_items[:4])}")
    print(f"  Matched Variants ({len(matched_variants)}): {', '.join(matched_variants[:4])}")
    print(f"  Synonyms ({len(syns)}): {', '.join(syns[:5])}")
    print(f"  Feed API Results ({feed_count}): {feed_titles}")

with open("backend/app/db/exact_10_results.json", "w", encoding="utf-8") as f:
    json.dump(audit_results, f, indent=2)

print("\nSaved detailed results to backend/app/db/exact_10_results.json")


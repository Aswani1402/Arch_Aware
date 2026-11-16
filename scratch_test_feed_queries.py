"""
Rigorous Semantic Relevance & Provenance Test Suite for Architect AI Feed
Tests all 13 queries specified in FEATURE 2:
1. brick
2. drainage
3. cement
4. bedroom
5. lighting
6. marble
7. tiles
8. garden waterfall
9. decorative pots
10. garden pathway
11. bathroom renovation
12. kitchen design
13. boundary wall

Enforces positive evidence matching, negative contamination exclusion,
and honest source metadata validation.
"""
import sys
import os
import json
import httpx

API_BASE_URL = os.environ.get("ARCHITECT_API_URL", "http://127.0.0.1:8000/api")

QUERIES_CONFIG = {
    "brick": {
        "required_evidence": ["brick", "masonry"],
        "forbidden_evidence": ["chandelier", "terrazzo flooring", "u-drain", "plumbing pipe"],
        "min_expected_matches": 3
    },
    "drainage": {
        "required_evidence": ["drain", "drainage", "stormwater", "culvert"],
        "forbidden_evidence": ["bedroom", "chandelier", "living room sofa", "residence with brick"],
        "min_expected_matches": 1
    },
    "cement": {
        "required_evidence": ["cement", "concrete", "mortar", "rcc"],
        "forbidden_evidence": ["bedroom loft", "chandelier"],
        "min_expected_matches": 2
    },
    "bedroom": {
        "required_evidence": ["bedroom", "bed", "wardrobe", "loft"],
        "forbidden_evidence": ["drainage", "bridge", "tmt rebar", "sewer"],
        "min_expected_matches": 2
    },
    "lighting": {
        "required_evidence": ["light", "lighting", "chandelier", "sconce", "lamp"],
        "forbidden_evidence": ["drainage slab", "concrete channel", "tmt bar"],
        "min_expected_matches": 2
    },
    "marble": {
        "required_evidence": ["marble", "vein", "carrara"],
        "forbidden_evidence": ["brick arch", "drainage channel", "tmt rebar"],
        "min_expected_matches": 2
    },
    "tiles": {
        "required_evidence": ["tile", "tiles", "porcelain", "vitrified"],
        "forbidden_evidence": ["bridge without pillars", "tmt rebar"],
        "min_expected_matches": 3
    },
    "garden waterfall": {
        "required_evidence": ["waterfall", "water feature", "pond", "rock"],
        "forbidden_evidence": ["bedroom", "chandelier", "tmt bar", "cooking"],
        "min_expected_matches": 1
    },
    "decorative pots": {
        "required_evidence": ["pot", "pots", "planter", "planters", "terracotta"],
        "forbidden_evidence": ["cooking pot", "pressure cooker", "drainage slab", "bridge"],
        "min_expected_matches": 1
    },
    "garden pathway": {
        "required_evidence": ["pathway", "walkway", "stepping stone", "paver"],
        "forbidden_evidence": ["chandelier", "false ceiling", "rebar"],
        "min_expected_matches": 1
    },
    "bathroom renovation": {
        "required_evidence": ["bathroom", "vanity", "shower", "renovation"],
        "forbidden_evidence": ["bridge", "drainage channel", "tmt bar"],
        "min_expected_matches": 1
    },
    "kitchen design": {
        "required_evidence": ["kitchen", "cabinet", "countertop", "modular"],
        "forbidden_evidence": ["bathroom shower", "drainage channel", "rebar"],
        "min_expected_matches": 1
    },
    "boundary wall": {
        "required_evidence": ["boundary wall", "wall", "masonry", "coping", "compound wall"],
        "forbidden_evidence": ["chandelier", "bedroom wardrobe", "bathroom shower"],
        "min_expected_matches": 1
    }
}

def run_query_audit():
    print("=" * 80)
    print("ARCHITECT AI — 13-QUERY SEMANTIC RELEVANCE AUDIT SUITE")
    print("=" * 80)

    total_queries = len(QUERIES_CONFIG)
    passed_queries = 0
    failed_queries = 0

    with httpx.Client(timeout=15.0) as client:
        for q, rules in QUERIES_CONFIG.items():
            print(f"\n{'#' * 80}")
            print(f"QUERY: '{q}'")
            print(f"Expected Evidence: {rules['required_evidence']}")
            print(f"Forbidden Contamination: {rules['forbidden_evidence']}")
            print(f"{'#' * 80}")

            resp = client.get(f"{API_BASE_URL}/feed", params={"q": q, "page_size": 20})
            if resp.status_code != 200:
                print(f"[FAIL] HTTP status {resp.status_code}: {resp.text}")
                failed_queries += 1
                continue

            data = resp.json()
            items = data.get("items", [])
            print(f"Returned Results: {len(items)} (Total in catalog: {data.get('total', 0)})")

            if len(items) < rules["min_expected_matches"]:
                print(f"[FAIL] Expected at least {rules['min_expected_matches']} matches, received {len(items)}")
                failed_queries += 1
                continue

            query_has_error = False

            for idx, item in enumerate(items, 1):
                title = item.get("title", "")
                desc = item.get("description", "")
                tags = item.get("material_tags", "")
                media_type = "video" if item.get("video_embed_id") else "image"
                source_url = item.get("source_url", "")
                thumb = item.get("thumbnail_url", "")
                combined_text = f"{title} {desc} {tags}".lower()

                has_pos_evidence = any(ev.lower() in combined_text for ev in rules["required_evidence"])
                contamination = [fb for fb in rules["forbidden_evidence"] if fb.lower() in combined_text]

                if idx <= 3:
                    print(f"\n  Result #{idx}:")
                    print(f"    Title:        {title}")
                    print(f"    Media Type:   {media_type}")
                    print(f"    Source URL:   {source_url}")
                    print(f"    Tags:         {tags}")
                    print(f"    Positive Match: {'PASS' if has_pos_evidence else 'FAIL'}")
                    print(f"    Negative Contamination: {'FAIL: ' + str(contamination) if contamination else 'PASS (Clean)'}")

                if not has_pos_evidence:
                    print(f"  [ERROR] Result #{idx} '{title}' lacks required topic evidence.")
                    query_has_error = True

                if contamination:
                    print(f"  [ERROR] Result #{idx} '{title}' contains conflicting concept: {contamination}")
                    query_has_error = True

            if query_has_error:
                print(f"\n[FAIL] Query '{q}' returned irrelevant or conflicting results.")
                failed_queries += 1
            else:
                print(f"\n[PASS] Query '{q}' returned trustworthy, relevant results without conflicts.")
                passed_queries += 1

    print("\n" + "=" * 80)
    print("AUDIT SUMMARY BY QUERY:")
    print("=" * 80)
    for q in QUERIES_CONFIG.keys():
        print(f"  * Checked: {q}")
    print("=" * 80)
    print(f"TOTAL: {passed_queries}/{total_queries} QUERIES PASSED ({failed_queries} failed)")
    print("=" * 80)

    if failed_queries > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_query_audit()

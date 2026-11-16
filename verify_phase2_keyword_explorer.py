import sys
import os
import json

sys.path.insert(0, os.path.abspath('backend'))
from app.services.keyword_library import (
    get_all_keyword_groups,
    search_keyword_library,
    expand_search_query_with_synonyms,
    MASTER_KEYWORD_CATEGORIES
)
from app.core.database import SessionLocal
from app.models.models import ArchitecturalReference, Supplier, SavedItem

def run_verification():
    print("=" * 60)
    print("PHASE 2: KEYWORD EXPLORER AUDIT & VERIFICATION")
    print("=" * 60)

    # 1. API categories load
    cats = get_all_keyword_groups()
    print(f"Total categories returned: {len(cats)}")
    assert len(cats) == 15, f"Expected 15 categories, got {len(cats)}"

    # 2. Detailed count audit
    total_subcats = 0
    total_items = 0
    total_variants = 0
    breakdown = []

    for c in cats:
        sub_objs = c.get('subcategory_objects', [])
        num_sub = len(sub_objs)
        num_items = 0
        num_vars = 0
        for s in sub_objs:
            items = s.get('items', [])
            num_items += len(items)
            for it in items:
                num_vars += len(it.get('variants', []))
        total_subcats += num_sub
        total_items += num_items
        total_variants += num_vars
        breakdown.append({
            'id': c.get('id'),
            'name': c.get('name'),
            'subcategories': num_sub,
            'items': num_items,
            'variants': num_vars
        })

    print(f"Total Subcategories: {total_subcats}")
    print(f"Total Items: {total_items}")
    print(f"Total Variants: {total_variants}")
    print("\n--- Category-by-Category Audit ---")
    for b in breakdown:
        print(f"Category {b['id']}: {b['name']} -> {b['subcategories']} Subcategories, {b['items']} Items, {b['variants']} Variants")

    # 3. Test searching for exact items, aliases, synonyms and variants
    search_test_queries = [
        "Chandeliers",
        "Teak Wood Doors",
        "TMT Rebar",
        "Athangudi",
        "CPVC",
        "Rammed Earth",
        "Italian Marble",
        "Nalukettu",
        "Kitchen Cabinets",
        "Bathroom Fittings"
    ]
    print("\n--- Search Query Matching Tests ---")
    for q in search_test_queries:
        res = search_keyword_library(q)
        syns = expand_search_query_with_synonyms(q)
        print(f"Query: '{q}' -> Matched in {len(res)} categories. Synonyms ({len(syns)}): {syns[:3]}")
        assert len(res) > 0, f"Search query '{q}' returned 0 matches!"

    # 4. Database Integrity Verification
    db = SessionLocal()
    ref_count = db.query(ArchitecturalReference).count()
    insta_count = db.query(ArchitecturalReference).filter(ArchitecturalReference.source_platform == 'instagram').count()
    supplier_count = db.query(Supplier).count()
    saved_count = db.query(SavedItem).count()
    db.close()

    print("\n--- Database Persistence Check ---")
    print(f"Total Architectural References: {ref_count}")
    print(f"Instagram References: {insta_count}")
    print(f"Total Suppliers: {supplier_count}")
    print(f"Total Saved Items: {saved_count}")

    assert ref_count >= 504, f"Database lost references! Count is {ref_count}"
    assert insta_count >= 120, f"Database lost Instagram references! Count is {insta_count}"
    assert supplier_count >= 78, f"Database lost suppliers! Count is {supplier_count}"

    # 5. Room-wise completeness verification
    print("\n--- Room-Wise Completeness Verification ---")
    rooms_checked = ["Living Room", "Kitchen", "Bathroom", "Bedroom", "Outdoor / Garden", "Facade / Exterior"]
    for r in rooms_checked:
        matched = False
        matched_loc = ""
        for c in cats:
            for s in c.get('subcategory_objects', []):
                sub_name = s.get('name', '')
                item_names = [it.get('name', '') for it in s.get('items', [])]
                all_text = f"{c['name']} {sub_name} {' '.join(item_names)}".lower()
                clean_r = r.lower().replace(" / ", " ")
                if any(part in all_text for part in clean_r.split()):
                    matched = True
                    matched_loc = f"{c['name']} -> {sub_name}"
                    break
            if matched:
                break
        print(f"Room context '{r}' mapped to: {matched_loc}")
        assert matched, f"Room '{r}' not found in taxonomy!"

    # Save audit report to JSON
    report = {
        "status": "VERIFIED",
        "total_categories": len(cats),
        "total_subcategories": total_subcats,
        "total_items": total_items,
        "total_variants": total_variants,
        "breakdown": breakdown,
        "database": {
            "references": ref_count,
            "instagram_references": insta_count,
            "suppliers": supplier_count,
            "saved_items": saved_count
        }
    }
    with open("backend/app/tests/keyword_explorer_audit_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\nAudit report written to backend/app/tests/keyword_explorer_audit_report.json")
    print("VERIFICATION COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
    run_verification()

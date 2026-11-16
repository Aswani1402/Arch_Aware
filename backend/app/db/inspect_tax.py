import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.app.services.keyword_library import MASTER_KEYWORD_CATEGORIES

tax = MASTER_KEYWORD_CATEGORIES
print(f"Total Categories: {len(tax)}")
total_subs = 0
total_items = 0
total_variants = 0

for c in tax:
    subs = c['subcategories']
    sub_count = len(subs)
    item_count = sum(len(s.get('items', [])) for s in subs)
    var_count = sum(sum(len(i.get('variants', [])) for i in s.get('items', [])) for s in subs)
    total_subs += sub_count
    total_items += item_count
    total_variants += var_count
    print(f"{c['id']:2d}. {c['name']:<32} | {sub_count:2d} subs | {item_count:3d} items | {var_count:4d} variants")

print("-" * 65)
print(f"TOTAL: {len(tax)} categories | {total_subs} subcategories | {total_items} items | {total_variants} variants")

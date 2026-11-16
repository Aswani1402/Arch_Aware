import json
import sys
import os

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from app.services.keyword_library import (
    MASTER_KEYWORD_CATEGORIES,
    SYNONYM_DICT,
    STOCK_INVENTORY_SPECS
)

print(f"Exporting complete taxonomy: {len(MASTER_KEYWORD_CATEGORIES)} categories...")

lines = []
lines.append("# NIVORA COMPLETE TAXONOMY EXPORT (PHASE 5A READ-ONLY AUDIT)\n")
lines.append(f"Total Categories: {len(MASTER_KEYWORD_CATEGORIES)}\n")

total_subs = 0
total_items = 0
total_vars = 0

for cat in MASTER_KEYWORD_CATEGORIES:
    cat_id = cat["id"]
    cat_name = cat["name"]
    cat_slug = cat["slug"]
    cat_icon = cat.get("icon", "")
    supplier_cat = cat.get("supplier_category", "Architectural Sourcing")
    desc = cat.get("description", "")

    lines.append(f"\n## Category {cat_id}: {cat_icon} {cat_name} (`{cat_slug}`)")
    lines.append(f"- **Supplier Category:** {supplier_cat}")
    lines.append(f"- **Description:** {desc}")

    for sub in cat.get("subcategories", []):
        sub_name = sub.get("name", "")
        total_subs += 1
        lines.append(f"\n### Subcategory: {sub_name}")
        items = sub.get("items", [])

        for item in items:
            item_name = item.get("name", "")
            total_items += 1
            variants = item.get("variants", [])
            total_vars += len(variants)

            # Find matching synonyms
            item_lower = item_name.lower()
            matched_syns = []
            for k, syn_list in SYNONYM_DICT.items():
                if k in item_lower or any(word in item_lower for word in k.split()):
                    matched_syns.extend(syn_list[:3])
            matched_syns = list(dict.fromkeys(matched_syns))[:5]

            lines.append(f"- **Item:** `{item_name}` ({len(variants)} variants)")
            if matched_syns:
                lines.append(f"  - *Synonyms / Aliases:* {', '.join(matched_syns)}")
            for v in variants:
                lines.append(f"  - Variant: {v}")

lines.append("\n" + "=" * 80)
lines.append(f"\nTOTAL SUMMARY: {len(MASTER_KEYWORD_CATEGORIES)} Categories | {total_subs} Subcategories | {total_items} Items | {total_vars} Variants")

export_path = "backend/app/db/taxonomy_export.md"
with open(export_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Exported {len(lines)} lines to {export_path}")
print(f"Summary: {len(MASTER_KEYWORD_CATEGORIES)} Categories | {total_subs} Subcategories | {total_items} Items | {total_vars} Variants")


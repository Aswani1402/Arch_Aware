import sqlite3
import os
import pytest

def test_catalogue_walk_reaches_all_6319_materials():
    """
    Stage 2 Requirement:
    Walk every category and subcategory in the catalogue and confirm
    that the sum of materials across all subcategories equals exactly 6,319.
    """
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "architect_ai.db")
    assert os.path.exists(db_path), f"Database not found at {db_path}"

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # 1. Total count directly from catalogue_materials
    total_direct = cur.execute("SELECT count(*) FROM catalogue_materials").fetchone()[0]
    assert total_direct == 6319, f"Direct count expected 6319, got {total_direct}"

    # 2. Walk categories -> subcategories -> materials
    categories = cur.execute("SELECT id, name, slug FROM catalogue_categories ORDER BY id").fetchall()
    assert len(categories) == 10, f"Expected 10 physical catalogue categories, got {len(categories)}"

    walked_total = 0
    total_subcategories = 0
    seen_material_ids = set()

    for cat_id, cat_name, cat_slug in categories:
        subcategories = cur.execute(
            "SELECT id, name, slug FROM catalogue_subcategories WHERE category_id = ? ORDER BY id",
            (cat_id,)
        ).fetchall()
        total_subcategories += len(subcategories)

        for sub_id, sub_name, sub_slug in subcategories:
            materials = cur.execute(
                "SELECT id, name FROM catalogue_materials WHERE category_id = ? AND subcategory_id = ?",
                (cat_id, sub_id)
            ).fetchall()

            for mat_id, mat_name in materials:
                assert mat_id not in seen_material_ids, f"Duplicate material {mat_id} ({mat_name}) encountered!"
                seen_material_ids.add(mat_id)
                walked_total += 1

    con.close()

    assert total_subcategories == 184, f"Expected 184 subcategories, got {total_subcategories}"
    assert walked_total == 6319, f"Walked total expected 6319, got {walked_total}"
    assert len(seen_material_ids) == 6319, f"Unique materials count expected 6319, got {len(seen_material_ids)}"

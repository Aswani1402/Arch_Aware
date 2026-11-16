import pytest
from app.services.keyword_library import (
    MASTER_KEYWORD_CATEGORIES,
    SYNONYM_DICT,
    CONTENT_CLASSIFICATIONS,
    SEARCH_EXPANSION_DIMENSIONS,
    INSTAGRAM_DISCOVERY_INTENTS,
    SOURCE_SPECIFIC_QUERY_TEMPLATES,
    FILTER_METADATA_GROUPS,
    STOCK_INVENTORY_SPECS,
    get_all_keyword_groups,
    search_keyword_library,
    expand_search_query_with_synonyms
)

EXPECTED_14_CATEGORIES = [
    (1, "Architecture", "architecture"),
    (2, "Exterior & Facade", "exterior-facade"),
    (3, "Interior Spaces", "interior-spaces"),
    (4, "Construction Materials", "construction-materials"),
    (5, "Plumbing & Sanitaryware", "plumbing-sanitaryware"),
    (6, "Electrical & Lighting", "electrical-lighting"),
    (7, "Flooring & Stone", "flooring-stone"),
    (8, "Doors, Windows & Glass", "doors-windows-glass"),
    (9, "Furniture", "furniture"),
    (10, "Decor & Furnishings", "decor-furnishings"),
    (11, "Ceiling, Walls & Finishes", "ceiling-walls-finishes"),
    (12, "Landscape & Outdoor", "landscape-outdoor"),
    (13, "Manufacturers & Suppliers", "manufacturers-suppliers"),
    (14, "Brands", "brands")
]

def test_14_consolidated_categories_count_and_sequence(client):
    """
    Verify the Master Keyword Explorer exposes exactly 14 consolidated main categories
    in the defined sequence through the API endpoint /api/categories/keywords/library.
    """
    res = client.get("/api/categories/keywords/library")
    assert res.status_code == 200
    groups = res.json()
    assert len(groups) == 14

    for idx, (exp_id, exp_name, exp_slug) in enumerate(EXPECTED_14_CATEGORIES):
        grp = groups[idx]
        assert grp["id"] == exp_id
        assert grp["name"] == exp_name
        assert grp["slug"] == exp_slug
        assert grp["icon"] is not None
        assert grp["supplier_category"] is not None
        assert len(grp["subcategories"]) > 0
        assert len(grp["subcategory_objects"]) > 0
        assert grp["count"] > 0

def test_taxonomy_hierarchy_depth_and_metrics():
    """
    Verify 4-level progressive disclosure metrics:
    Main Category (14) -> Subcategory (>=70) -> Item (>=180) -> Variant (>=800).
    """
    assert len(MASTER_KEYWORD_CATEGORIES) == 14
    total_subs = sum(len(c["subcategories"]) for c in MASTER_KEYWORD_CATEGORIES)
    total_items = sum(sum(len(s.get("items", [])) for s in c["subcategories"]) for c in MASTER_KEYWORD_CATEGORIES)
    total_variants = sum(sum(sum(len(i.get("variants", [])) for i in s.get("items", [])) for s in c["subcategories"]) for c in MASTER_KEYWORD_CATEGORIES)

    assert total_subs >= 70, f"Expected at least 70 subcategories, got {total_subs}"
    assert total_items >= 180, f"Expected at least 180 items, got {total_items}"
    assert total_variants >= 800, f"Expected at least 800 variants, got {total_variants}"

    # Verify every subcategory has items and variants
    for cat in MASTER_KEYWORD_CATEGORIES:
        for sub in cat["subcategories"]:
            items = sub.get("items", [])
            assert len(items) > 0, f"Subcategory {sub['name']} in {cat['name']} has no items"
            for it in items:
                assert "name" in it and len(it["name"]) > 0
                variants = it.get("variants", [])
                assert len(variants) > 0, f"Item {it['name']} in {sub['name']} has no variants"

def test_10_required_audit_keywords_search_api(client):
    """
    Verify end-to-end lookup and search on all 10 required audit keywords via API:
    1. Staircase
    2. Chandelier
    3. Kerala House Elevation
    4. Marble Flooring
    5. Modular Kitchen
    6. TMT Bars
    7. Athangudi Tiles
    8. Landscape Stones
    9. Wooden Doors
    10. Decorative Wall Panels
    """
    required_keywords = [
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

    for q in required_keywords:
        res = client.get(f"/api/categories/keywords/search?q={q}")
        assert res.status_code == 200
        data = res.json()
        assert data["query"] == q
        assert len(data["synonyms"]) >= 1
        results = data["results"]
        assert len(results) > 0, f"Search for required keyword '{q}' returned zero matches"

        # Check matched structure
        first_match = results[0]
        assert "category_id" in first_match
        assert "category_name" in first_match
        assert "matches" in first_match
        assert len(first_match["matches"]) > 0
        match_obj = first_match["matches"][0]
        assert "subcategory" in match_obj
        assert "keywords" in match_obj

def test_catalogue_enrichments_search_api(client):
    """
    Verify representative domain terms from all newly incorporated sections:
    HVAC, CCTV, Fire Extinguisher, Office Furniture, Rammed Earth,
    Precast Concrete, Excavator, Water Storage Tank, Architectural Drawings, Brands.
    """
    enrichment_terms = [
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

    for term in enrichment_terms:
        res = client.get(f"/api/categories/keywords/search?q={term}")
        assert res.status_code == 200
        data = res.json()
        assert len(data["results"]) > 0, f"Enrichment search for '{term}' returned zero matches"

def test_metadata_and_specifications_contracts():
    """
    Verify completeness of architectural metadata, stock inventory specs,
    search expansion dimensions, and content classifications.
    """
    # 1. Content Classifications (17 classifications)
    assert len(CONTENT_CLASSIFICATIONS) >= 17
    codes = [c["code"] for c in CONTENT_CLASSIFICATIONS]
    assert "architectural_project" in codes
    assert "detail_drawing" in codes
    assert "material_specification" in codes
    assert "cost_breakdown" in codes
    assert "artisan_craft" in codes

    # 2. Search Expansion Dimensions (40 dimensions across 4 axes)
    assert len(SEARCH_EXPANSION_DIMENSIONS["styles"]) == 10
    assert len(SEARCH_EXPANSION_DIMENSIONS["spaces"]) == 10
    assert len(SEARCH_EXPANSION_DIMENSIONS["materials"]) == 10
    assert len(SEARCH_EXPANSION_DIMENSIONS["stages"]) == 10
    total_dims = sum(len(v) for v in SEARCH_EXPANSION_DIMENSIONS.values())
    assert total_dims == 40

    # 3. Instagram Discovery Intents
    assert len(INSTAGRAM_DISCOVERY_INTENTS) >= 8

    # 4. Source Specific Query Templates
    assert "google_search" in SOURCE_SPECIFIC_QUERY_TEMPLATES
    assert "google_places" in SOURCE_SPECIFIC_QUERY_TEMPLATES
    assert "socialcrawl_instagram" in SOURCE_SPECIFIC_QUERY_TEMPLATES
    assert "catalog_lookup" in SOURCE_SPECIFIC_QUERY_TEMPLATES

    # 5. Filter Metadata Groups
    assert "location_scopes" in FILTER_METADATA_GROUPS
    assert "material_classes" in FILTER_METADATA_GROUPS
    assert "project_typologies" in FILTER_METADATA_GROUPS
    assert "price_tiers" in FILTER_METADATA_GROUPS

    # 6. Stock Inventory Specifications
    assert STOCK_INVENTORY_SPECS["tmt_rebar_sizes_mm"] == [6, 8, 10, 12, 16, 20, 25, 32]
    assert "Fe500D" in STOCK_INVENTORY_SPECS["tmt_grades"]
    assert "OPC 53" in STOCK_INVENTORY_SPECS["cement_grades"]

def test_synonym_expansion_and_alias_mapping():
    """
    Verify synonym expansion resolves related domain terms and aliases.
    """
    stair_syns = expand_search_query_with_synonyms("staircase")
    assert any("steps" in s or "stair" in s for s in stair_syns)

    kerala_syns = expand_search_query_with_synonyms("kerala")
    assert any("nalukettu" in s for s in kerala_syns)

    tmt_syns = expand_search_query_with_synonyms("tmt")
    assert any("rebar" in s or "steel" in s for s in tmt_syns)

    marble_syns = expand_search_query_with_synonyms("marble")
    assert any("italian marble" in s or "statuario" in s for s in marble_syns)


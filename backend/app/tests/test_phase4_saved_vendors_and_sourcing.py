import pytest
from app.services.sourcing_service import CATEGORY_SUPPLIER_RULES, classify_supplier_match
from app.models.models import Supplier


def test_saved_supplier_toggle_and_retrieval(client, db, user_headers):
    """
    Test Phase 4 requirement:
    - User can save a supplier via POST /api/saved/toggle with item_type='supplier'.
    - Supplier is retrieved in GET /api/saved/items.
    - Saved supplier item_data is enriched with full metadata (id, name, business_type, verification_status, city, etc.).
    - Toggling again removes the supplier.
    """
    # 1. Fetch an existing supplier from seed DB
    supplier = db.query(Supplier).first()
    assert supplier is not None, "A seed supplier must exist in test db"
    sup_id = supplier.id

    # 2. Toggle save for supplier
    res = client.post("/api/saved/toggle", json={
        "item_type": "supplier",
        "supplier_id": sup_id
    }, headers=user_headers)
    assert res.status_code == 200
    save_data = res.json()
    assert save_data["saved"] is True
    assert "collection" in save_data["message"]

    # 3. Retrieve saved items
    res = client.get("/api/saved/items", headers=user_headers)
    assert res.status_code == 200
    items = res.json()
    matching = [it for it in items if it.get("supplier_id") == sup_id and it.get("item_type") == "supplier"]
    assert len(matching) == 1, "Saved supplier must be in saved items"

    # 4. Verify enriched item_data metadata
    item_data = matching[0].get("item_data")
    assert item_data is not None
    assert item_data.get("id") == sup_id
    assert item_data.get("name") == supplier.name
    assert item_data.get("business_type") == supplier.business_type
    assert item_data.get("verification_status") == supplier.verification_status
    assert item_data.get("city") == supplier.city
    assert "materials_sold" in item_data

    # 5. Toggle again to unsave
    res = client.post("/api/saved/toggle", json={
        "item_type": "supplier",
        "supplier_id": sup_id
    }, headers=user_headers)
    assert res.status_code == 200
    unsave_data = res.json()
    assert unsave_data["saved"] is False

    # 6. Verify supplier is no longer in saved items
    res = client.get("/api/saved/items", headers=user_headers)
    assert res.status_code == 200
    items_after = res.json()
    matching_after = [it for it in items_after if it.get("supplier_id") == sup_id and it.get("item_type") == "supplier"]
    assert len(matching_after) == 0, "Unsaved supplier must not appear in saved items"


def test_saved_collections_separate_counts_and_isolation(client, db, user_headers):
    """
    Test Phase 4 requirement:
    - Saved Inspiration (item_type='reference') and Saved Vendors (item_type='supplier')
      must maintain strictly isolated counts and collections.
    """
    supplier = db.query(Supplier).first()
    assert supplier is not None

    # Get baseline counts
    res = client.get("/api/saved/counts", headers=user_headers)
    assert res.status_code == 200
    base_counts = res.json()
    base_refs = base_counts["references_count"]
    base_sups = base_counts["suppliers_count"]
    base_total = base_counts["total_count"]

    # Save 1 supplier
    res = client.post("/api/saved/toggle", json={
        "item_type": "supplier",
        "supplier_id": supplier.id
    }, headers=user_headers)
    assert res.status_code == 200
    assert res.json()["saved"] is True

    # Check updated counts
    res = client.get("/api/saved/counts", headers=user_headers)
    assert res.status_code == 200
    updated_counts = res.json()
    assert updated_counts["suppliers_count"] == base_sups + 1
    assert updated_counts["references_count"] == base_refs, "Saving supplier must not alter references_count"
    assert updated_counts["total_count"] == base_total + 1

    # Cleanup: unsave supplier
    client.post("/api/saved/toggle", json={
        "item_type": "supplier",
        "supplier_id": supplier.id
    }, headers=user_headers)


def test_saved_supplier_duplicate_prevention(client, db, user_headers):
    """
    Test Phase 4 requirement:
    - Attempting to save the same supplier repeatedly toggles state cleanly
      and prevents duplicate entries in the database.
    """
    supplier = db.query(Supplier).first()
    assert supplier is not None
    sup_id = supplier.id

    # Toggle 1: Save
    res1 = client.post("/api/saved/toggle", json={"item_type": "supplier", "supplier_id": sup_id}, headers=user_headers)
    assert res1.json()["saved"] is True

    # Toggle 2: Unsave
    res2 = client.post("/api/saved/toggle", json={"item_type": "supplier", "supplier_id": sup_id}, headers=user_headers)
    assert res2.json()["saved"] is False

    # Toggle 3: Re-save
    res3 = client.post("/api/saved/toggle", json={"item_type": "supplier", "supplier_id": sup_id}, headers=user_headers)
    assert res3.json()["saved"] is True

    # Verify only 1 record exists in saved items
    res = client.get("/api/saved/items", headers=user_headers)
    matching = [it for it in res.json() if it.get("supplier_id") == sup_id and it.get("item_type") == "supplier"]
    assert len(matching) == 1

    # Cleanup
    client.post("/api/saved/toggle", json={"item_type": "supplier", "supplier_id": sup_id}, headers=user_headers)


def test_sourcing_search_without_location_does_not_fabricate_kochi(client):
    """
    Test Phase 4 requirement:
    - When no location/city is specified in /api/sourcing/search, the backend must NOT
      fabricate 'Kochi' as the default location.
    - user_location.city must be None and is_set must be False.
    """
    res = client.get("/api/sourcing/search?q=paint")
    assert res.status_code == 200
    data = res.json()

    user_loc = data.get("user_location", {})
    assert user_loc.get("city") is None, "City must be None when not provided"
    assert user_loc.get("is_set") is False, "is_set must be False when no location is provided"
    assert user_loc.get("latitude") is None
    assert user_loc.get("longitude") is None

    # Tier results should still return valid data
    assert "tiers" in data
    assert "total_suppliers_found" in data


def test_sourcing_category_rules_enrichment():
    """
    Test Phase 4 requirement:
    - The 5 newly added sourcing category rules correctly trigger and map categories:
      1. paints_and_waterproofing
      2. roofing_and_ceilings
      3. architectural_hardware
      4. construction_equipment
      5. interior_showrooms
    """
    rule_keys = {rule["category_key"]: rule for rule in CATEGORY_SUPPLIER_RULES}

    # 1. Paints & Waterproofing
    assert "paints_and_waterproofing" in rule_keys
    paint_rule = rule_keys["paints_and_waterproofing"]
    assert "paint" in paint_rule["trigger_words"]
    assert "waterproofing" in paint_rule["trigger_words"]
    assert any("coating" in term for term in paint_rule["supplier_category_terms"])

    # 2. Roofing & Ceilings
    assert "roofing_and_ceilings" in rule_keys
    roof_rule = rule_keys["roofing_and_ceilings"]
    assert "roofing" in roof_rule["trigger_words"]
    assert "gypsum" in roof_rule["trigger_words"]
    assert any("shingle" in term for term in roof_rule["supplier_category_terms"])

    # 3. Architectural Hardware
    assert "architectural_hardware" in rule_keys
    hw_rule = rule_keys["architectural_hardware"]
    assert "hardware" in hw_rule["trigger_words"]
    assert "mortise lock" in hw_rule["trigger_words"]
    assert any("hinges" in term for term in hw_rule["supplier_category_terms"])

    # 4. Construction Equipment
    assert "construction_equipment" in rule_keys
    equip_rule = rule_keys["construction_equipment"]
    assert "scaffolding" in equip_rule["trigger_words"]
    assert "concrete mixer" in equip_rule["trigger_words"]
    assert any("equipment" in term for term in equip_rule["supplier_category_terms"])

    # 5. Interior Material Showrooms
    assert "interior_showrooms" in rule_keys
    show_rule = rule_keys["interior_showrooms"]
    assert "showroom" in show_rule["trigger_words"]
    assert "experience center" in show_rule["trigger_words"]
    assert any("studio" in term for term in show_rule["supplier_category_terms"])


def test_classify_supplier_match_with_new_rules():
    """
    Verify classify_supplier_match successfully classifies a supplier
    matching one of the newly added rules (e.g. paints & waterproofing).
    """
    mock_sup = Supplier(
        id=9999,
        name="Kerala Coatings & Waterproofing Solutions",
        slug="kerala-coatings",
        business_type="authorized_dealer",
        materials_sold="Exterior emulsion paints, Dr Fixit waterproofing chemicals, primers",
        verification_status="verified",
        city="Kochi",
        state="Kerala"
    )

    match_type, match_label, explanation, cat_title = classify_supplier_match(
        mock_sup,
        query_text="waterproofing",
        matched_products_links=[]
    )

    assert cat_title == "Paints, Textures & Waterproofing"
    assert "waterproofing" in explanation.lower() or "dealer" in match_label.lower()

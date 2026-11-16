import pytest
from app.main import app
from app.models.models import ArchitecturalReference, User, SavedItem

def test_save_and_unsave_persistence_with_media_metadata(client, user_headers):
    """
    FEATURE 4 & 5: Save/unsave persistence and metadata richness
    """
    # Unauthenticated request must return 401
    assert client.get("/api/saved").status_code == 401

    # 1. Fetch current saved references
    saved_res = client.get("/api/saved", headers=user_headers)
    assert saved_res.status_code == 200
    saved_ids = {s.get("reference_id") for s in saved_res.json()}

    feed_res = client.get("/api/feed?page_size=20")
    assert feed_res.status_code == 200
    items = feed_res.json()["items"]
    assert len(items) > 0
    # Pick an item that is not currently saved
    target_ref = next((r for r in items if r["id"] not in saved_ids), None)
    if not target_ref:
        # If all 20 are saved, create a reference or unsave one
        target_ref = items[0]
        client.post("/api/saved/toggle", json={"item_type": "reference", "reference_id": target_ref["id"]}, headers=user_headers)
    target_id = target_ref["id"]

    # 2. Toggle save
    save_res = client.post("/api/saved/toggle", json={
        "item_type": "reference",
        "reference_id": target_id
    }, headers=user_headers)
    assert save_res.status_code == 200
    save_data = save_res.json()
    assert save_data["status"] == "saved"
    assert save_data["is_saved"] is True

    # 3. Retrieve saved items and verify full media metadata is preserved
    get_saved = client.get("/api/saved", headers=user_headers)
    assert get_saved.status_code == 200
    saved_items = get_saved.json()
    assert len(saved_items) > 0

    saved_ref = next((s for s in saved_items if s.get("reference_id") == target_id), None)
    assert saved_ref is not None
    assert "item_data" in saved_ref
    item_data = saved_ref["item_data"]
    assert item_data["id"] == target_id
    assert "media_url" in item_data or "thumbnail_url" in item_data

    # 4. Toggle unsave
    unsave_res = client.post("/api/saved/toggle", json={
        "item_type": "reference",
        "reference_id": target_id
    }, headers=user_headers)
    assert unsave_res.status_code == 200
    assert unsave_res.json()["status"] in ["unsaved", "removed"]
    assert unsave_res.json()["is_saved"] is False

    # 5. Verify removed
    verify_get = client.get("/api/saved", headers=user_headers)
    assert verify_get.status_code == 200
    still_saved = [s for s in verify_get.json() if s.get("reference_id") == target_id]
    assert len(still_saved) == 0

def test_ai_material_detection_uncertainty_labels(client):
    """
    FEATURE 7: AI Material Detection provides qualified uncertainty labels,
    distinguishes source-confirmed from AI-inferred materials, and avoids
    inventing manufacturer stock or load ratings.
    """
    # 1. Find a reference with brick or stone or tile
    feed_res = client.get("/api/feed?q=brick&page_size=5")
    assert feed_res.status_code == 200
    items = feed_res.json()["items"]
    assert len(items) > 0
    ref_id = items[0]["id"]

    # 2. Call detect-materials endpoint
    detect_res = client.post(f"/api/references/{ref_id}/detect-materials", json={})
    assert detect_res.status_code == 200
    data = detect_res.json()

    assert "source_confirmed_materials" in data
    assert "ai_inferred_materials" in data
    assert "disclaimer" in data
    assert "Visual AI Identification is an educational inference tool" in data["disclaimer"]

    inferred = data["ai_inferred_materials"]
    assert len(inferred) > 0

    # Verify qualified uncertainty label structure
    first_inferred = inferred[0]
    assert "qualified_label" in first_inferred
    assert "confidence" in first_inferred
    assert first_inferred["is_confirmed"] is False
    assert "uncertainty_note" in first_inferred or len(data.get("uncertainty_notes", [])) > 0

    # Ensure no fabricated pricing or manufacturer stock is invented
    assert "price" not in first_inferred
    assert "stock_quantity" not in first_inferred

def test_ai_material_detection_user_correction(client):
    """
    FEATURE 7: User correction submission updates detection without data loss.
    """
    feed_res = client.get("/api/feed?page_size=3")
    assert feed_res.status_code == 200
    ref_id = feed_res.json()["items"][0]["id"]

    correction_payload = {
        "user_corrections": [
            {
                "name": "Handmade Terrazzo Cladding",
                "category": "Flooring & Cladding",
                "notes": "Verified by project site engineer"
            }
        ]
    }
    res = client.post(f"/api/references/{ref_id}/detect-materials", json=correction_payload)
    assert res.status_code == 200
    data = res.json()
    inferred = data["ai_inferred_materials"]
    
    user_item = next((m for m in inferred if "Handmade Terrazzo Cladding" in m.get("name", "")), None)
    assert user_item is not None
    assert user_item["confidence"] == 0.95
    assert user_item["is_confirmed"] is True

def test_local_vendors_first_india_wide_second(client):
    """
    FEATURE 8: Local Vendors Mode prioritizes city vicinity (<25km / <50km)
    and India-Wide mode provides nationwide suppliers.
    """
    # 1. Search sourcing in Kochi
    kochi_res = client.get("/api/sourcing/search?city=Kochi&radius=25")
    assert kochi_res.status_code == 200
    data = kochi_res.json()
    assert "levels_traversed" in data
    assert "tiers" in data
    
    # Check that tier 1 is Local
    tiers = {t["tier"]: t for t in data["tiers"]}
    assert 1 in tiers
    assert tiers[1]["tier_name"] == "Local"
    
    # Check that tier 4 is India
    assert 4 in tiers
    assert tiers[4]["tier_name"] == "India"

    # 2. Search sourcing in Nagercoil
    nagercoil_res = client.get("/api/sourcing/search?city=Nagercoil&radius=25")
    assert nagercoil_res.status_code == 200
    nag_data = nagercoil_res.json()
    lvl0 = next((lvl for lvl in nag_data["levels_traversed"] if lvl["level"] == 0), None)
    assert lvl0 is not None
    # Cape Precast or Kanyakumari Steels are located in Nagercoil
    assert len(lvl0["suppliers"]) > 0
    assert any("Nagercoil" in s["city"] for s in lvl0["suppliers"])

def test_content_expansion_across_categories(client):
    """
    FEATURE 1: Verify presence of architecture, civil construction,
    interior design, flooring, garden/waterfall, and renovation content.
    """
    # 1. Architecture: Nalukettu or Chettinad
    kerala_res = client.get("/api/feed?q=nalukettu&page_size=5")
    assert kerala_res.status_code == 200
    assert kerala_res.json()["total"] > 0

    # 2. Civil construction: Drainage channels
    drain_res = client.get("/api/feed?q=drainage&page_size=5")
    assert drain_res.status_code == 200
    assert drain_res.json()["total"] > 0
    assert all("drain" in item["title"].lower() or "drain" in item.get("material_tags", "").lower() for item in drain_res.json()["items"])

    # 3. Materials: Marble
    marble_res = client.get("/api/feed?q=marble&page_size=5")
    assert marble_res.status_code == 200
    assert marble_res.json()["total"] > 0

    # 4. Garden Waterfall
    wf_res = client.get("/api/feed?q=garden+waterfall&page_size=5")
    assert wf_res.status_code == 200
    assert wf_res.json()["total"] > 0

    # 5. Bathroom / Kitchen Renovation
    reno_res = client.get("/api/feed?q=bathroom+renovation&page_size=5")
    assert reno_res.status_code == 200
    assert reno_res.json()["total"] > 0

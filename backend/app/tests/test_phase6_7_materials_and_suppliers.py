from app.models.models import ArchitecturalReference
from app.services.catalogue_import_service import import_catalogue_csv


def test_detect_materials_multi_material_separation_and_catalogue(client, db):
    import_catalogue_csv(db)
    ref = ArchitecturalReference(
        title="Brick & Teak Courtyard Residence with Chandeliers & Sanitaryware",
        slug="brick-teak-courtyard-test",
        source_platform="curated",
        source_url="https://example.org/project/brick-teak",
        material_tags="wire-cut brick, teak wood, chandelier, sanitaryware",
        description="Exposed brickwork facade with seasoned teak louvers, pendant chandeliers, and vitreous sanitaryware fittings.",
        verification_status="UNVERIFIED",
    )
    db.add(ref)
    db.commit()
    db.refresh(ref)

    resp = client.post(f"/api/references/{ref.id}/detect-materials")
    assert resp.status_code == 200
    data = resp.json()
    assert data["reference_id"] == ref.id
    assert isinstance(data["source_confirmed_materials"], list)
    inferred_names = [m["name"] for m in data["ai_inferred_materials"]]
    assert len(inferred_names) >= 3
    assert all(m["is_confirmed"] is False for m in data["ai_inferred_materials"])
    assert all("unconfirmed" in m["qualified_label"].lower() for m in data["ai_inferred_materials"])
    assert isinstance(data["independently_discovered_catalogue_materials"], list)
    assert len(data["independently_discovered_catalogue_materials"]) >= 1
    assert all(
        item["provenance"] == "INDEPENDENT_CATALOGUE_MATCH"
        for item in data["independently_discovered_catalogue_materials"]
    )
    # Never invent pricing/stock inside AI material identification
    for m in data["ai_inferred_materials"]:
        assert "price" not in m
        assert "stock_count" not in m


def test_hierarchical_supplier_discovery_preserves_city_and_all_tiers(client):
    # Without city: never fabricate Kochi
    resp_none = client.get("/api/sourcing/search", params={"q": "steel"})
    assert resp_none.status_code == 200
    body_none = resp_none.json()
    assert body_none["user_location"]["city"] is None
    assert body_none["user_location"]["is_set"] is False
    assert len(body_none["levels_traversed"]) == 8  # Levels 0..7
    assert len(body_none["tiers"]) == 5

    # With explicit city Pune: preserves Pune and traverses 7+1 levels
    resp_pune = client.get("/api/sourcing/search", params={"q": "steel", "city": "Pune"})
    assert resp_pune.status_code == 200
    body_pune = resp_pune.json()
    assert body_pune["user_location"]["city"] == "Pune"
    assert body_pune["user_location"]["state"] == "Maharashtra"
    assert body_pune["user_location"]["is_set"] is True
    assert [lvl["level"] for lvl in body_pune["levels_traversed"]] == [0, 1, 2, 3, 4, 5, 6, 7]


def test_hierarchical_sourcing_kochi(client):
    # Searching for Apex Ultima from Kochi, Kerala
    response = client.get("/api/sourcing/search?q=Apex+Ultima&city=Kochi&radius=25")
    assert response.status_code == 200
    data = response.json()
    assert data["total_suppliers_found"] >= 2
    assert "levels_traversed" in data
    assert len(data["levels_traversed"]) == 8  # Level 0 to 7

    # Level 0 (within 25km of Kochi) should include Malabar Paint
    lvl0 = data["levels_traversed"][0]
    assert lvl0["level"] == 0
    assert len(lvl0["suppliers"]) >= 1
    assert any("Malabar Paint" in s["supplier_name"] for s in lvl0["suppliers"])

    # Neighbouring state (Tamil Nadu, Coimbatore) should appear in later level
    lvl4 = data["levels_traversed"][4]
    assert any("Deccan Architectural" in s["supplier_name"] for s in lvl4["suppliers"])

def test_international_sourcing_kyoto(client):
    # Searching for Japanese stone from Kochi
    response = client.get("/api/sourcing/search?q=Japanese+Stepping+Stones&city=Kochi")
    assert response.status_code == 200
    data = response.json()
    # Level 7 is international (Kyoto, Japan)
    lvl7 = data["levels_traversed"][7]
    assert lvl7["level"] == 7
    assert len(lvl7["suppliers"]) >= 1
    assert any(s["country"] == "Japan" for s in lvl7["suppliers"])

def test_deduplication_across_levels(client):
    response = client.get("/api/sourcing/search?city=Kochi")
    assert response.status_code == 200
    data = response.json()
    seen_ids = set()
    for level in data["levels_traversed"]:
        for sup in level["suppliers"]:
            assert sup["supplier_id"] not in seen_ids, f"Duplicate supplier {sup['supplier_name']} found in level {level['level']}"
            seen_ids.add(sup["supplier_id"])

def test_nagercoil_local_sourcing(client):
    # Search for drainage slabs from Nagercoil
    response = client.get("/api/sourcing/search?q=drainage&city=Nagercoil&radius=25")
    assert response.status_code == 200
    data = response.json()
    assert data["total_suppliers_found"] >= 1

    # Level 0 (local Nagercoil within 25km) must include Cape Precast
    lvl0 = data["levels_traversed"][0]
    assert any("Cape Precast" in s["supplier_name"] for s in lvl0["suppliers"])
    cape_sup = next(s for s in lvl0["suppliers"] if "Cape Precast" in s["supplier_name"])
    assert cape_sup["city"] == "Nagercoil"
    assert cape_sup["state"] == "Tamil Nadu"
    assert cape_sup["whatsapp"] is not None
    assert cape_sup["google_maps_url"] is not None


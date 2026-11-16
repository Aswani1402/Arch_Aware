import pytest

def test_geocode_known_preset_locations(client):
    """
    Known architectural hubs (Bengaluru, Kochi, Thiruvananthapuram, Nagercoil)
    must resolve successfully with their real coordinates and preset data.
    """
    # 1. Test Bengaluru
    res = client.get("/api/locations/geocode?q=Bengaluru")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["city"] == "Bengaluru"
    assert data["state"] == "Karnataka"
    assert round(data["latitude"], 2) == 12.97

    # 2. Test alias Thiruvananthapuram for Trivandrum preset
    res = client.get("/api/locations/geocode?q=Thiruvananthapuram")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["city"] in ["Trivandrum", "Thiruvananthapuram"]
    assert data["state"] == "Kerala"
    assert round(data["latitude"], 2) == 8.52

    # 3. Test Nagercoil
    res = client.get("/api/locations/geocode?q=Nagercoil")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["city"] == "Nagercoil"
    assert data["state"] == "Tamil Nadu"


def test_geocode_unknown_query_returns_failure_without_kochi_fallback(client):
    """
    Crucial Phase 3 requirement:
    Unknown locations must NEVER silently substitute Kochi coordinates.
    They must return success=False with clear error detail and null coordinates.
    """
    res = client.get("/api/locations/geocode?q=xyznonexistentcity9999")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert data["city"] is None
    assert data["latitude"] is None
    assert data["longitude"] is None
    assert "detail" in data
    assert "Could not find location" in data["detail"]


def test_geocode_empty_query_fails_gracefully(client):
    """
    Empty query string should fail gracefully.
    """
    res = client.get("/api/locations/geocode?q=%20%20")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert data["city"] is None


def test_location_presets_list(client):
    """
    Verify /api/locations/presets returns the full list of regional architectural hubs.
    """
    res = client.get("/api/locations/presets")
    assert res.status_code == 200
    presets = res.json()
    assert isinstance(presets, list)
    assert len(presets) >= 12
    cities = [h["city"] for h in presets]
    assert "Kochi" in cities
    assert "Bengaluru" in cities
    assert "Chennai" in cities


def test_supplier_discovery_without_location_does_not_fabricate_kochi(client):
    """
    When a user has not selected a location, /api/suppliers/discover must NOT
    silently substitute Kochi. It must report is_set=False and city=None,
    while gracefully returning regional and national verified suppliers.
    """
    res = client.get("/api/suppliers/discover?q=TMT+bar")
    assert res.status_code == 200
    data = res.json()
    user_loc = data.get("user_location", {})
    assert user_loc.get("city") is None
    assert user_loc.get("is_set") is False
    assert data["total_suppliers_found"] > 0
    # Tier structure is present and valid
    assert len(data["tiers"]) == 5
    # Tier 1 (local) has 0 suppliers because no local city was set
    assert len(data["tiers"][0]["suppliers"]) == 0
    # National / Zonal tiers contain matches
    assert any(len(t["suppliers"]) > 0 for t in data["tiers"][2:])


def test_supplier_discovery_with_explicit_location(client):
    """
    When an explicit location is provided, the 7-tier geographic fallback
    hierarchy is populated relative to the specified location.
    """
    res = client.get("/api/suppliers/discover?q=stone&city=Kochi")
    assert res.status_code == 200
    data = res.json()
    user_loc = data.get("user_location", {})
    assert user_loc.get("city") == "Kochi"
    assert user_loc.get("is_set") is True
    assert data["total_suppliers_found"] > 0
    # Immediate vicinity or extended has stone suppliers for Kochi (e.g. Coastal Surfaces & Stone Studio)
    assert len(data["tiers"][0]["suppliers"]) > 0 or len(data["tiers"][1]["suppliers"]) > 0

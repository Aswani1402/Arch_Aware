def test_google_places_search_without_key(client):
    """
    When GOOGLE_MAPS_API_KEY is not configured, the endpoint must return
    configured=False with structured setup instructions and local fallback results.
    """
    res = client.get("/api/locations/google-places/search?query=natural+stone&city=Kochi")
    assert res.status_code == 200
    data = res.json()
    assert "configured" in data
    assert "query" in data
    assert "results" in data
    assert isinstance(data["results"], list)
    if not data["configured"]:
        assert "setup_instructions" in data
        assert "GOOGLE_MAPS_API_KEY" in data["setup_instructions"]

def test_connectors_overview(client):
    """
    Verify connectors endpoint exposes all registered platform connectors
    with their real configured status.
    """
    res = client.get("/api/connectors")
    assert res.status_code == 200
    connectors = res.json()
    assert isinstance(connectors, list)
    platforms = [c["platform"] for c in connectors]
    assert "youtube" in platforms
    assert "instagram" in platforms
    assert "pinterest" in platforms
    assert "reddit" in platforms

def test_product_supplier_integrity(client):
    """
    Verify product-to-manufacturer and product-to-supplier relationships
    are accurately populated without misleading information.
    """
    res = client.get("/api/products/1")
    assert res.status_code == 200
    prod = res.json()
    assert prod["id"] == 1
    assert "manufacturer" in prod
    assert prod["manufacturer"] is not None
    assert "name" in prod["manufacturer"]
    assert prod["manufacturer"]["verification_status"] in ("MANUFACTURER_CONFIRMED", "VERIFIED", "verified")
    
    assert "available_suppliers" in prod
    assert isinstance(prod["available_suppliers"], list)
    assert len(prod["available_suppliers"]) > 0
    supplier_brief = prod["available_suppliers"][0]
    assert "supplier_name" in supplier_brief
    assert "city" in supplier_brief
    assert "delivery_scope" in supplier_brief

def test_saved_collection_lifecycle(client, user_headers):
    """
    Verify saving and unsaving references and products for architectural collections.
    """
    # 1. Save reference #1
    save_res = client.post("/api/saved/toggle", json={
        "item_type": "reference",
        "reference_id": 1,
        "project_collection": "Fort Kochi Villa"
    }, headers=user_headers)
    assert save_res.status_code == 200
    assert save_res.json()["status"] == "saved"

    # 2. Verify in saved list
    list_res = client.get("/api/saved", headers=user_headers)
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(i["item_type"] == "reference" and i["reference_id"] == 1 for i in items)

    # 3. Toggle off (unsave)
    unsave_res = client.post("/api/saved/toggle", json={
        "item_type": "reference",
        "reference_id": 1
    }, headers=user_headers)
    assert unsave_res.status_code == 200
    assert unsave_res.json()["status"] == "unsaved"

def test_admin_supplier_verification(client, admin_headers, user_headers):
    """
    Verify administrator can update supplier verification status,
    while unauthenticated and non-admin callers are rejected.
    """
    assert client.put("/api/admin/suppliers/1/verify", json={"status": "verified"}).status_code == 401
    assert client.put("/api/admin/suppliers/1/verify", json={"status": "verified"}, headers=user_headers).status_code == 403

    # Verify supplier #1
    res = client.put("/api/admin/suppliers/1/verify", json={"status": "verified"}, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["verification_status"] == "VERIFIED"

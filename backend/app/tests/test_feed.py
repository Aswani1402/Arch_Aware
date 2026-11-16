def test_feed_endpoint(client):
    response = client.get("/api/feed?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 5
    assert len(data["items"]) <= 10

def test_feed_category_filter(client):
    response = client.get("/api/feed?category=garden-materials")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["category_name"] in ["Landscape & Garden Materials", "Garden & Landscape Materials"]

def test_feed_platform_filter(client):
    response = client.get("/api/feed?platform=youtube")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    for item in data["items"]:
        assert item["source_platform"] == "youtube"
        assert item["video_embed_id"] is not None

def test_reference_detail(client):
    response = client.get("/api/references/japanese-garden-natural-stone-stepping-path")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] is not None
    assert "product_matches" in data
    assert len(data["product_matches"]) >= 1
    # Check that product match has manufacturer and match type
    match = data["product_matches"][0]
    assert match["match_type"] == "verified_exact"

import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_image_search_endpoint(client):
    response = client.get("/api/feed/image-search?q=modern+facade&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "images" in data
    assert len(data["images"]) > 0
    img = data["images"][0]
    assert "original_image_url" in img
    assert "source_page_url" in img
    assert "title" in img
    assert "attribution" in img
    assert "usage_license" in img
    assert "provider" in img
    assert data["provider_status"]["places_api_isolated"] is True

def test_mixed_feed_contains_images_and_videos(client):
    response = client.get("/api/feed?page=1&page_size=30")
    assert response.status_code == 200
    data = response.json()
    items = data["items"]
    assert len(items) > 0

    has_video = any(bool(item.get("video_embed_id")) for item in items)
    has_image = any(not item.get("video_embed_id") for item in items)
    assert has_video, "Feed must contain architectural videos"
    assert has_image, "Feed must contain architectural photographs/images"

def test_shorts_and_longer_videos(client):
    response = client.get("/api/feed?page=1&page_size=40")
    assert response.status_code == 200
    data = response.json()
    items = data["items"]

    shorts = [item for item in items if item.get("is_short") is True and item.get("video_embed_id")]
    long_videos = [item for item in items if item.get("is_short") is False and item.get("video_embed_id")]

    assert len(shorts) > 0, "Feed must discover architectural YouTube Shorts"
    assert len(long_videos) > 0, "Feed must discover longer architectural videos"
    
    # Confirm Shorts have duration formatted
    for s in shorts:
        assert s.get("video_duration") is not None

def test_similar_references_endpoint(client):
    # Fetch first item
    feed_res = client.get("/api/feed?page=1&page_size=1")
    assert feed_res.status_code == 200
    items = feed_res.json()["items"]
    assert len(items) > 0
    ref_id = items[0]["id"]

    sim_res = client.get(f"/api/feed/similar/{ref_id}?limit=4")
    assert sim_res.status_code == 200
    sim_items = sim_res.json()
    assert isinstance(sim_items, list)
    assert len(sim_items) > 0
    for s in sim_items:
        assert s["id"] != ref_id

def test_relevance_query_filtering(client):
    response = client.get("/api/feed?q=brick&page=1&page_size=10")
    assert response.status_code == 200
    items = response.json()["items"]
    for item in items:
        text = f"{item['title']} {item.get('material_tags', '')} {item.get('description', '')}".lower()
        assert "brick" in text or "masonry" in text or "jaali" in text

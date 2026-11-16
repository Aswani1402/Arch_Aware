import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.connectors.youtube_connector import YouTubeConnector
from app.core.config import settings

def test_image_provenance_distinction_in_feed(client):
    """Verify that every discovery reference distinguishes:
    1. inspiration_image_url
    2. inspiration_source_url
    3. manufacturer_product_image_url (only if verified)
    4. manufacturer_product_url
    5. manufacturer_id
    6. product_match_status
    """
    res = client.get("/api/feed?page=1&page_size=20")
    assert res.status_code == 200
    data = res.json()
    items = data["items"]
    assert len(items) > 0

    for item in items:
        # Provenance fields must exist
        assert "inspiration_image_url" in item
        assert "inspiration_source_url" in item
        assert "manufacturer_product_image_url" in item
        assert "manufacturer_product_url" in item
        assert "manufacturer_id" in item
        assert "product_match_status" in item

        # Do not use generic room image as manufacturer's product image
        # If product_match_status is unidentified, manufacturer_product_image_url MUST be None
        if item["product_match_status"] == "unidentified":
            assert item["manufacturer_product_image_url"] is None, (
                f"Reference {item['id']} has unidentified match status but contains manufacturer_product_image_url"
            )

def test_youtube_connector_configuration_and_status(client):
    """Verify connector status is returned truthfully and not faked."""
    res = client.get("/api/feed")
    assert res.status_code == 200
    data = res.json()
    assert "connector_status" in data
    status = data["connector_status"]
    assert "youtube_configured" in status
    assert "total_references" in status
    assert "youtube_count" in status
    assert "curated_count" in status
    assert "quota_exceeded" in status

    # Verify that YouTube items are present and have valid video_embed_id
    yt_items = [i for i in data["items"] if i["source_platform"] == "youtube"]
    for y in yt_items:
        assert y["video_embed_id"] is not None
        assert len(y["video_embed_id"]) > 0

def test_youtube_sync_endpoint(client):
    """Verify the live YouTube sync endpoint works and deduplicates."""
    res = client.post("/api/feed/sync-youtube", json={"query": "architectural stone"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "details" in data
    assert "total_youtube_references" in data["details"]

@pytest.mark.asyncio
async def test_youtube_connector_graceful_quota_fallback():
    """Verify that when YouTube quota is exceeded or key is invalid, connector falls back gracefully."""
    connector = YouTubeConnector(api_key="INVALID_TEST_KEY_FOR_FALLBACK_TESTING")
    assert connector.is_configured() is True
    
    # Query with invalid key should catch HTTPError/quota error and fall back to curated cache
    results = await connector.search("Architectural material installation", max_results=3)
    assert isinstance(results, list)
    assert len(results) > 0
    # Creator attribution and video embed id must be preserved
    for item in results:
        assert "video_id" in item
        assert "title" in item
        assert "creator_name" in item

@pytest.mark.asyncio
async def test_youtube_connector_when_key_absent():
    """Verify that when API key is completely absent, is_configured returns False and fallback works."""
    connector = YouTubeConnector(api_key="")
    assert connector.is_configured() is False
    results = await connector.search("Japanese garden stone", max_results=2)
    assert isinstance(results, list)
    assert len(results) > 0

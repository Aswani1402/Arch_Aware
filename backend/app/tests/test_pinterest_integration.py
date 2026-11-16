import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.pinterest_service import (
    backoff,
    socialcrawl,
    normalize_pinterest_pin,
    search_pinterest_page,
    search_pinterest,
    is_socialcrawl_configured,
    PINTEREST_CATEGORIES,
    _CACHE
)

client = TestClient(app)


def test_pinterest_categories_completeness():
    """Verify all 28 Architect AI categories are defined with focused search queries."""
    res = client.get("/api/pinterest/categories")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 28
    categories = data["categories"]
    assert len(categories) == 28

    category_names = [c["name"] for c in categories]
    # Verify core required categories
    assert "Architecture and Building Design" in category_names
    assert "Exterior and Facade Design" in category_names
    assert "Interior Design" in category_names
    assert "Living Rooms" in category_names
    assert "Bedrooms" in category_names
    assert "Kitchens" in category_names
    assert "Bathrooms" in category_names
    assert "Building Materials" in category_names
    assert "Stone and Marble" in category_names
    assert "Wood and Timber" in category_names
    assert "Bricks and Blocks" in category_names
    assert "Cement and Concrete" in category_names
    assert "Tiles and Flooring" in category_names
    assert "Glass and Metal" in category_names
    assert "Paint and Colour Combinations" in category_names
    assert "Walls and Ceiling Finishes" in category_names
    assert "Doors and Windows" in category_names
    assert "Staircases" in category_names
    assert "Lighting and Electrical Fixtures" in category_names
    assert "Furniture" in category_names
    assert "Landscaping and Gardens" in category_names
    assert "Construction Techniques" in category_names
    assert "Architectural Details" in category_names
    assert "Architectural Styles" in category_names
    assert "Commercial Spaces" in category_names
    assert "Products and Manufacturers" in category_names
    assert "Sustainable Architecture" in category_names
    assert "Indian and Kerala Architecture" in category_names

    # Verify every category has a focused search query
    for cat in categories:
        assert cat["query"] and len(cat["query"]) > 3
        assert cat["section"]


def test_pinterest_status_unconfigured(monkeypatch):
    """Verify status reports configured=False when key is not present and never leaks keys."""
    monkeypatch.delenv("SOCIALCRAWL_API_KEY", raising=False)
    with patch("app.services.pinterest_service.get_socialcrawl_api_key", return_value=""), \
         patch("app.api.pinterest.is_socialcrawl_configured", return_value=False), \
         patch("app.services.pinterest_service.is_socialcrawl_configured", return_value=False):
        res = client.get("/api/pinterest/status")
        assert res.status_code == 200
        data = res.json()
        assert data["configured"] is False
        assert "provider" in data
        assert "api_key" not in data
        assert "key" not in data


def test_pinterest_status_configured(monkeypatch):
    """Verify status reports configured=True when key is set without printing the secret."""
    with patch("app.services.pinterest_service.get_socialcrawl_api_key", return_value="test_secret_key_12345"), \
         patch("app.api.pinterest.is_socialcrawl_configured", return_value=True), \
         patch("app.services.pinterest_service.is_socialcrawl_configured", return_value=True):
        res = client.get("/api/pinterest/status")
        assert res.status_code == 200
        data = res.json()
        assert data["configured"] is True
        assert "test_secret_key_12345" not in str(data)  # Crucial: key itself is never exposed!


def test_search_missing_api_key_handling(monkeypatch):
    """Verify search returns 400 Bad Request if SOCIALCRAWL_API_KEY is not configured."""
    monkeypatch.delenv("SOCIALCRAWL_API_KEY", raising=False)
    with patch("app.services.pinterest_service.get_socialcrawl_api_key", return_value=""), \
         patch("app.api.pinterest.is_socialcrawl_configured", return_value=False), \
         patch("app.services.pinterest_service.is_socialcrawl_configured", return_value=False):
        res = client.get("/api/pinterest/search?query=kerala+architecture")
        assert res.status_code == 400
        assert "SOCIALCRAWL_API_KEY" in res.json()["detail"]


def test_search_query_validation():
    """Verify empty query is rejected with 422."""
    res = client.get("/api/pinterest/search?query=")
    assert res.status_code == 422


def test_backoff_and_jitter():
    """Verify exponential backoff calculation increases with attempts."""
    b0 = backoff(0)
    b1 = backoff(1)
    b2 = backoff(2)
    assert 0.5 <= b0 <= 1.0
    assert 1.0 <= b1 <= 2.0
    assert 2.0 <= b2 <= 4.0


def test_idempotency_key_reused_across_retries(monkeypatch):
    """Verify the same Idempotency-Key is reused across all retries of a single request."""
    monkeypatch.setenv("SOCIALCRAWL_API_KEY", "test_key")

    mock_response_fail = MagicMock()
    mock_response_fail.json.side_effect = ValueError("JSON error")

    captured_idempotency_keys = []

    def mock_get(*args, **kwargs):
        headers = kwargs.get("headers", {})
        captured_idempotency_keys.append(headers.get("Idempotency-Key"))
        mock_res = MagicMock()
        mock_res.json.return_value = {
            "success": False,
            "error": {"type": "INTERNAL_SERVER_ERROR", "retryable": True, "message": "temporary"}
        }
        mock_res.headers = {}
        return mock_res

    with patch("requests.get", side_effect=mock_get):
        with patch("time.sleep", return_value=None):
            with pytest.raises(RuntimeError):
                socialcrawl({"query": "doors"})

    # Should have attempted 4 times (attempt 0, 1, 2, 3)
    assert len(captured_idempotency_keys) == 4
    # All retries must have shared the exact same idempotency key
    assert len(set(captured_idempotency_keys)) == 1
    assert captured_idempotency_keys[0] is not None


def test_error_handling_resource_not_found(monkeypatch):
    """Verify RESOURCE_NOT_FOUND returns None safely without raising an exception."""
    monkeypatch.setenv("SOCIALCRAWL_API_KEY", "test_key")

    mock_res = MagicMock()
    mock_res.json.return_value = {
        "success": False,
        "error": {
            "type": "RESOURCE_NOT_FOUND",
            "message": "No search results found"
        }
    }
    with patch("requests.get", return_value=mock_res):
        result = socialcrawl({"query": "nonexistent_query_xyz"})
        assert result is None


def test_dry_run_execution(monkeypatch):
    """Verify dry_run=1 passes dry_run flag to SocialCrawl and does not fetch or charge."""
    monkeypatch.setenv("SOCIALCRAWL_API_KEY", "test_key")

    mock_res = MagicMock()
    mock_res.json.return_value = {
        "success": True,
        "dry_run": True,
        "request_id": "req-dry-run-123",
        "price": 0,
        "estimated_cost": "0 credits",
        "data": {"items": []}
    }

    with patch("requests.get", return_value=mock_res) as mock_get:
        page_res = search_pinterest_page(query="exposed concrete", dry_run=True)
        assert page_res["success"] is True
        assert page_res["dry_run"] is True
        assert len(page_res["items"]) == 0
        assert page_res["total_items"] == 0
        assert "dry_run_details" in page_res

        # Ensure params included dry_run=1
        _, kwargs = mock_get.call_args
        assert kwargs["params"]["dry_run"] == 1


def test_pinterest_pin_normalization():
    """Verify normalization extracts original image, title, description, source, and attribution without fabricating details."""
    raw_item = {
        "id": "pin-987654",
        "title": "Minimalist Teak Louver Verandah",
        "description": "Natural seasoned teak louvers providing cross-ventilation in tropical villa.",
        "images": {
            "orig": {
                "url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format"
            }
        },
        "url": "https://www.pinterest.com/pin/987654/",
        "pinner": {
            "name": "Studio Kerala",
            "username": "studiokerala"
        }
    }

    normalized = normalize_pinterest_pin(raw_item)
    assert normalized["pin_id"] == "pin-987654"
    assert normalized["title"] == "Minimalist Teak Louver Verandah"
    assert normalized["description"] == "Natural seasoned teak louvers providing cross-ventilation in tropical villa."
    assert normalized["image_url"] == "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format"
    assert normalized["source_url"] == "https://www.pinterest.com/pin/987654/"
    assert normalized["creator_name"] == "Studio Kerala"
    assert normalized["creator_url"] == "https://www.pinterest.com/studiokerala/"
    assert normalized["source_platform"] == "pinterest"
    assert normalized["source_label"] == "Pinterest"
    assert normalized["verification_status"] == "UNVERIFIED"

    # Test with minimal data (ensure no fabricated title or creator)
    sparse_item = {
        "id": "pin-111",
        "image_url": "https://example.com/pin.jpg"
    }
    sparse_norm = normalize_pinterest_pin(sparse_item)
    assert sparse_norm["pin_id"] == "pin-111"
    assert sparse_norm["title"] is None
    assert sparse_norm["creator_name"] is None
    assert sparse_norm["image_url"] == "https://example.com/pin.jpg"
    assert sparse_norm["is_video"] is False
    assert sparse_norm["video_duration"] is None

    # Test SocialCrawl canonical nested schema format with video
    nested_item = {
        "post": {
            "id": "pin-video-7788",
            "url": "https://www.pinterest.com/pin/pin-video-7788/",
            "content": {
                "text": "Kerala Monsoon Rain Courtyard Tour",
                "media_urls": ["https://images.unsplash.com/photo-1590381105924-c72589b9ef3f"],
                "thumbnail_url": "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f",
                "duration_seconds": 35.0
            },
            "author": {
                "username": "keralatours",
                "display_name": "Kerala Architecture Tours"
            },
            "ext": {
                "alt_text": "Video walkthrough of courtyard house"
            }
        }
    }
    nested_norm = normalize_pinterest_pin(nested_item)
    assert nested_norm["pin_id"] == "pin-video-7788"
    assert nested_norm["title"] == "Kerala Monsoon Rain Courtyard Tour"
    assert nested_norm["image_url"] == "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f"
    assert nested_norm["creator_name"] == "Kerala Architecture Tours"
    assert nested_norm["creator_url"] == "https://www.pinterest.com/keralatours/"
    assert nested_norm["is_video"] is True
    assert nested_norm["video_duration"] == "0:35"


def test_cursor_based_pagination(monkeypatch):
    """Verify cursor-based pagination is supported and passes cursor parameter."""
    monkeypatch.setenv("SOCIALCRAWL_API_KEY", "test_key")

    mock_res = MagicMock()
    mock_res.json.return_value = {
        "success": True,
        "data": {
            "items": [
                {"id": "pin-1", "title": "Pin 1", "image_url": "https://example.com/1.jpg"},
                {"id": "pin-2", "title": "Pin 2", "image_url": "https://example.com/2.jpg"}
            ]
        },
        "pagination": {
            "has_more": True,
            "next_cursor": "cursor_page_2_xyz"
        }
    }

    with patch("requests.get", return_value=mock_res) as mock_get:
        res = search_pinterest_page(query="terracotta", cursor="cursor_page_1")
        assert res["success"] is True
        assert res["has_more"] is True
        assert res["next_cursor"] == "cursor_page_2_xyz"
        assert len(res["items"]) == 2

        # Verify cursor passed to SocialCrawl
        _, kwargs = mock_get.call_args
        assert kwargs["params"]["cursor"] == "cursor_page_1"


def test_pinterest_save_and_unsave(client, user_headers):
    """Verify saving a Pinterest pin creates an ArchitecturalReference and SavedItem, and toggling unsaves it."""
    payload = {
        "pin_id": "pin-test-save-4455",
        "title": "Athangudi Tile Courtyard Flooring",
        "description": "Handcrafted cement tiles in Chettinad courtyard house.",
        "image_url": "https://example.com/athangudi.jpg",
        "source_url": "https://www.pinterest.com/pin/4455/",
        "creator_name": "Heritage Crafts",
        "material_tags": "athangudi, tiles, courtyard"
    }

    # Unauthenticated must be rejected with 401
    assert client.post("/api/pinterest/save", json=payload).status_code == 401

    # 1. Save pin
    res1 = client.post("/api/pinterest/save", json=payload, headers=user_headers)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["saved"] is True
    assert data1["status"] == "saved"
    ref_id = data1["reference_id"]
    assert ref_id > 0

    # 2. Toggle save again (should unsave)
    res2 = client.post("/api/pinterest/save", json=payload, headers=user_headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["saved"] is False
    assert data2["status"] == "unsaved"
    assert data2["reference_id"] == ref_id

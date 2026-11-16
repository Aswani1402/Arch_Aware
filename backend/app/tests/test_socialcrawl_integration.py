import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.socialcrawl_service import (
    backoff,
    socialcrawl,
    normalize_instagram_reel,
    normalize_youtube_video,
    normalize_reddit_post,
    normalize_google_business,
    normalize_google_shopping,
    search_instagram_reels,
    search_youtube,
    search_reddit,
    search_google_businesses,
    search_google_shopping,
    search_all_sources,
    is_socialcrawl_configured,
    get_socialcrawl_api_key,
    CREDIT_COSTS,
    ARCHITECTURAL_CATEGORIES,
    _SOCIALCRAWL_CACHE,
    MAX_RETRIES,
    INSTAGRAM_TIMEOUT,
    YOUTUBE_TIMEOUT,
    REDDIT_TIMEOUT,
    GOOGLE_BUSINESS_TIMEOUT,
    GOOGLE_SHOPPING_TIMEOUT
)

client = TestClient(app)


# ============================================================
# 1. API KEY CONFIGURATION TESTS
# ============================================================

def test_socialcrawl_status_unconfigured(monkeypatch):
    """Verify status reports configured=False and NEVER leaks the API key."""
    monkeypatch.delenv("SOCIALCRAWL_API_KEY", raising=False)
    with patch("app.services.socialcrawl_service.get_socialcrawl_api_key", return_value=""), \
         patch("app.api.socialcrawl.is_socialcrawl_configured", return_value=False):
        res = client.get("/api/socialcrawl/status")
        assert res.status_code == 200
        data = res.json()
        assert data["configured"] is False
        assert "provider" in data
        assert "endpoints" in data
        assert "api_key" not in data
        assert "key" not in data


def test_socialcrawl_status_configured(monkeypatch):
    """Verify status reports configured=True and never reveals the secret."""
    with patch("app.services.socialcrawl_service.get_socialcrawl_api_key", return_value="sc_secret_test_key_xyz"), \
         patch("app.api.socialcrawl.is_socialcrawl_configured", return_value=True):
        res = client.get("/api/socialcrawl/status")
        assert res.status_code == 200
        data = res.json()
        assert data["configured"] is True
        assert "sc_secret_test_key_xyz" not in str(data)
        assert "credit_pricing" in data


def test_search_missing_api_key_returns_400(monkeypatch):
    """Verify endpoints return 400 Bad Request when API key is missing."""
    monkeypatch.delenv("SOCIALCRAWL_API_KEY", raising=False)
    with patch("app.services.socialcrawl_service.get_socialcrawl_api_key", return_value=""), \
         patch("app.api.socialcrawl.is_socialcrawl_configured", return_value=False):
        for route in ["/api/socialcrawl/instagram?query=villa",
                      "/api/socialcrawl/youtube?query=villa",
                      "/api/socialcrawl/reddit?query=villa",
                      "/api/socialcrawl/businesses?query=tiles",
                      "/api/socialcrawl/shopping?query=tiles"]:
            res = client.get(route)
            assert res.status_code == 400
            assert "SOCIALCRAWL_API_KEY" in res.json()["detail"]


# ============================================================
# 2. DRY-RUN PRICING CHECKS
# ============================================================

def test_dry_run_pricing_checks():
    """Verify dry_run=1 flag returns estimate without billing credits."""
    mock_estimate = {
        "kind": "estimate",
        "valid": True,
        "hold": 1,
        "unit": "credits",
        "pricing": "metered"
    }
    with patch("app.services.socialcrawl_service.socialcrawl", return_value={
        "success": True,
        "credits_used": 0,
        "request_id": "req-dry-run-123",
        "data": {"estimate": mock_estimate}
    }):
        res = client.get("/api/socialcrawl/instagram?query=architecture&dry_run=true")
        assert res.status_code == 200
        data = res.json()
        assert data["dry_run"] is True
        assert data["credits_used"] == 0
        assert "estimate" in data


# ============================================================
# 3. SUCCESSFUL RESPONSES & NORMALIZATION TESTS (ALL 5 ENDPOINTS)
# ============================================================

def test_instagram_reels_success():
    """Verify Instagram search returns normalized reels with video, captions, creator."""
    mock_item = {
        "post": {
            "id": "123456789",
            "url": "https://www.instagram.com/reel/123456789/",
            "content": {
                "text": "Kerala courtyard modern architecture\n#kerala #courtyard",
                "media_urls": "https://example.com/video.mp4",
                "thumbnail_url": "https://example.com/thumb.jpg",
                "duration_seconds": 18.5
            },
            "author": {
                "username": "kerala_architect",
                "display_name": "Kerala Architect",
                "avatar_url": "https://example.com/avatar.jpg"
            },
            "engagement": {
                "views": 50000,
                "likes": 4200,
                "comments": 120
            },
            "ext": {
                "hashtags": ["kerala", "courtyard"]
            }
        }
    }

    with patch("app.services.socialcrawl_service.paginated_search", return_value=[mock_item]):
        res = client.get("/api/socialcrawl/instagram?query=kerala+courtyard")
        assert res.status_code == 200
        data = res.json()
        assert data["total_items"] == 1
        reel = data["items"][0]
        assert reel["reel_id"] == "123456789"
        assert reel["video_url"] == "https://example.com/video.mp4"
        assert reel["thumbnail_url"] == "https://example.com/thumb.jpg"
        assert reel["creator_name"] == "@kerala_architect"
        assert reel["source_platform"] == "instagram"


def test_youtube_videos_success():
    """Verify YouTube search returns normalized videos with embed IDs and durations."""
    mock_item = {
        "post": {
            "id": "txORF1yu6dc",
            "url": "https://www.youtube.com/watch?v=txORF1yu6dc",
            "content": {
                "text": "Modern House Walkthrough Interior Design",
                "thumbnail_url": "https://i.ytimg.com/vi/txORF1yu6dc/hqdefault.jpg",
                "duration_seconds": 125
            },
            "author": {
                "username": "ArchiDesign",
                "display_name": "Archi Design Studio"
            },
            "engagement": {"views": 15000, "likes": 500}
        }
    }

    with patch("app.services.socialcrawl_service.paginated_search", return_value=[mock_item]):
        res = client.get("/api/socialcrawl/youtube?query=modern+house")
        assert res.status_code == 200
        data = res.json()
        assert data["total_items"] == 1
        video = data["items"][0]
        assert video["video_id"] == "txORF1yu6dc"
        assert video["video_embed_id"] == "txORF1yu6dc"
        assert video["video_duration"] == "2:05"
        assert video["creator_name"] == "Archi Design Studio"


def test_reddit_discussions_success():
    """Verify Reddit search returns normalized discussions with subreddit and upvotes."""
    mock_item = {
        "post": {
            "id": "abc123z",
            "url": "https://www.reddit.com/r/architecture/comments/abc123z/clay_bricks_vs_aac/",
            "content": {
                "text": "Detailed comparison between wirecut clay bricks and AAC blocks.",
                "thumbnail_url": "https://example.com/reddit_thumb.jpg"
            },
            "author": {"username": "ArchitectPro"},
            "engagement": {"likes": 340, "comments": 85},
            "ext": {
                "title": "Clay Bricks vs AAC Blocks Comparison",
                "subreddit": "architecture",
                "flair": "Discussion"
            }
        }
    }

    with patch("app.services.socialcrawl_service.paginated_search", return_value=[mock_item]):
        res = client.get("/api/socialcrawl/reddit?query=bricks+aac")
        assert res.status_code == 200
        data = res.json()
        assert data["total_items"] == 1
        post = data["items"][0]
        assert post["post_id"] == "abc123z"
        assert post["subreddit"] == "r/architecture"
        assert post["upvotes"] == 340
        assert post["comments"] == 85


def test_twitter_ai_search_success():
    """Verify Twitter (X) AI-Search returns normalized tweet, creator, engagement, and media."""
    mock_item = {
        "post": {
            "id": "1892837461019283741",
            "url": "https://x.com/ArchDaily/status/1892837461019283741",
            "text": "The Red Concrete Pavilion by Studio KO. Monolithic red concrete cast on-site.",
            "author": {
                "username": "ArchDaily",
                "display_name": "ArchDaily",
                "avatar_url": "https://pbs.twimg.com/profile_images/archdaily.jpg"
            },
            "content": {
                "text": "The Red Concrete Pavilion by Studio KO. Monolithic red concrete cast on-site.",
                "media_urls": ["https://images.unsplash.com/photo-1600585154340-be6161a56a0c"]
            },
            "engagement": {
                "likes": 420,
                "retweets": 85,
                "replies": 19
            }
        }
    }

    with patch("app.services.socialcrawl_service.socialcrawl", return_value={
        "success": True,
        "credits_used": 5,
        "data": {"items": [mock_item]}
    }):
        res = client.get("/api/socialcrawl/twitter?query=Pavilion+Architecture")
        assert res.status_code == 200
        data = res.json()
        assert data["total_items"] == 1
        tweet = data["items"][0]
        assert tweet["tweet_id"] == "1892837461019283741"
        assert tweet["creator_name"] == "@ArchDaily"
        assert tweet["creator_username"] == "ArchDaily"
        assert tweet["likes"] == 420
        assert tweet["source_platform"] == "x"
        assert "photo-1600585154340" in tweet["media_url"]


def test_google_business_search_success():
    """Verify Google Business search returns verified status, ratings, phone, and maps URL."""
    mock_item = {
        "place": {
            "id": "987654321",
            "name": "Kochi Marble & Granite Traders",
            "category": "Marble supplier",
            "rating": {"value": 4.8, "max": 5},
            "reviews_count": 95,
            "address": "NH 66, Edappally, Kochi, Kerala 682024",
            "phone": "+91 98470 12345",
            "latitude": 10.0261,
            "longitude": 76.3125,
            "verified": True,
            "ext": {
                "maps_url": "https://maps.google.com/?cid=987654321",
                "city": "Kochi",
                "region": "Kerala"
            }
        }
    }

    with patch("app.services.socialcrawl_service.socialcrawl", return_value={
        "success": True,
        "credits_used": 5,
        "data": {"items": [mock_item]}
    }):
        res = client.get("/api/socialcrawl/businesses?query=marble&location=Kochi,+Kerala,+India")
        assert res.status_code == 200
        data = res.json()
        assert data["total_items"] == 1
        biz = data["items"][0]
        assert biz["name"] == "Kochi Marble & Granite Traders"
        assert biz["rating"] == 4.8
        assert biz["phone"] == "+91 98470 12345"
        assert biz["verified"] is True
        assert biz["verification_status"] == "SUPPLIER_CONFIRMED"


def test_google_shopping_product_success():
    """Verify Google Shopping returns actual prices, merchant, brand and links without fabricating."""
    mock_prod = {
        "product": {
            "id": "prod_7788",
            "title": "Asian Paints Apex Ultima Exterior Emulsion 20L",
            "seller": "PaintMart India",
            "brand": "Asian Paints",
            "price": {"current": 5400.0, "currency": "INR", "original": 6200.0},
            "rating": {"average": 4.6, "count": 180},
            "url": "https://example.com/buy-apex-ultima",
            "ext": {"gid": "gid_9999"}
        }
    }

    with patch("app.services.socialcrawl_service.socialcrawl", return_value={
        "success": True,
        "credits_used": 5,
        "data": {"items": [mock_prod]}
    }):
        res = client.get("/api/socialcrawl/shopping?query=Asian+Paints+Apex")
        assert res.status_code == 200
        data = res.json()
        assert data["total_items"] == 1
        prod = data["items"][0]
        assert prod["brand"] == "Asian Paints"
        assert prod["price"] == 5400.0
        assert prod["currency"] == "INR"
        assert prod["seller"] == "PaintMart India"


# ============================================================
# 4. EMPTY RESPONSES & RESOURCE_NOT_FOUND TESTS
# ============================================================

def test_empty_results_handling():
    """Verify empty response returns cleanly with items=[] and total_items=0."""
    with patch("app.services.socialcrawl_service.paginated_search", return_value=[]):
        res = client.get("/api/socialcrawl/instagram?query=nonexistentqueryxyz")
        assert res.status_code == 200
        data = res.json()
        assert data["total_items"] == 0
        assert data["items"] == []


def test_resource_not_found_handling():
    """Verify RESOURCE_NOT_FOUND (404) returns gracefully without error."""
    with patch("app.services.socialcrawl_service.socialcrawl", return_value=None):
        res = client.get("/api/socialcrawl/shopping?gid=non_existent_gid_999")
        assert res.status_code == 200
        data = res.json()
        assert data["items"] == []


# ============================================================
# 5. RETRY, BACKOFF & ERROR HANDLING TESTS
# ============================================================

def test_backoff_timing():
    """Verify backoff exponential multiplier."""
    b0 = backoff(0)
    assert 0.5 <= b0 <= 1.0
    b1 = backoff(1)
    assert 1.0 <= b1 <= 2.0
    b2 = backoff(2)
    assert 2.0 <= b2 <= 4.0


def test_permanent_service_unavailable_error():
    """Verify permanent SERVICE_UNAVAILABLE without Retry-After raises immediately."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "success": False,
        "error": {"type": "SERVICE_UNAVAILABLE", "message": "Cluster down", "retryable": False}
    }
    mock_resp.headers = {}
    mock_resp.status_code = 503

    with patch("requests.get", return_value=mock_resp), \
         patch("app.services.socialcrawl_service.get_socialcrawl_api_key", return_value="test_key"):
        with pytest.raises(RuntimeError) as exc_info:
            socialcrawl("instagram/search/reels", {"query": "test"}, timeout=10)
        assert "SERVICE_UNAVAILABLE" in str(exc_info.value)


def test_retry_after_respected():
    """Verify Retry-After header is parsed and waited upon."""
    mock_resp_fail = MagicMock()
    mock_resp_fail.json.return_value = {
        "success": False,
        "error": {"type": "RATE_LIMIT_EXCEEDED", "message": "Slow down", "retryable": True}
    }
    mock_resp_fail.headers = {"Retry-After": "0.1"}
    mock_resp_fail.status_code = 429

    mock_resp_ok = MagicMock()
    mock_resp_ok.json.return_value = {"success": True, "data": {"items": []}}
    mock_resp_ok.status_code = 200

    with patch("requests.get", side_effect=[mock_resp_fail, mock_resp_ok]), \
         patch("time.sleep") as mock_sleep, \
         patch("app.services.socialcrawl_service.get_socialcrawl_api_key", return_value="test_key"):
        res = socialcrawl("youtube/search", {"query": "test"}, timeout=10)
        assert res is not None
        assert res["success"] is True
        mock_sleep.assert_called_with(0.1)


# ============================================================
# 6. IDEMPOTENCY-KEY REUSE ACROSS RETRIES
# ============================================================

def test_idempotency_key_reused_on_retries():
    """Verify the exact SAME Idempotency-Key is reused across all retries of a request."""
    mock_resp_retry = MagicMock()
    mock_resp_retry.json.return_value = {
        "success": False,
        "error": {"type": "TEMPORARY_ERROR", "message": "Retry me", "retryable": True}
    }
    mock_resp_retry.headers = {}
    mock_resp_retry.status_code = 500

    mock_resp_ok = MagicMock()
    mock_resp_ok.json.return_value = {"success": True, "data": {"items": []}}
    mock_resp_ok.status_code = 200

    with patch("requests.get", side_effect=[mock_resp_retry, mock_resp_ok]) as mock_get, \
         patch("time.sleep"), \
         patch("app.services.socialcrawl_service.get_socialcrawl_api_key", return_value="test_key"):
        socialcrawl("reddit/search", {"query": "test"}, timeout=10)
        assert mock_get.call_count == 2
        key1 = mock_get.call_args_list[0][1]["headers"]["Idempotency-Key"]
        key2 = mock_get.call_args_list[1][1]["headers"]["Idempotency-Key"]
        assert key1 == key2  # Must be identical!


# ============================================================
# 7. SEARCH-ALL INDEPENDENT ERROR ISOLATION
# ============================================================

def test_search_all_independent_isolation():
    """Verify failure in one source does not crash or stop other sources."""
    def fake_instagram(*args, **kwargs):
        raise RuntimeError("Instagram upstream down")

    def fake_youtube(*args, **kwargs):
        return {"success": True, "items": [{"id": "yt1", "title": "YT Video"}], "total_items": 1}

    with patch("app.services.socialcrawl_service.search_instagram_reels", side_effect=fake_instagram), \
         patch("app.services.socialcrawl_service.search_youtube", side_effect=fake_youtube), \
         patch("app.services.socialcrawl_service.is_socialcrawl_configured", return_value=True):
        res = client.get("/api/socialcrawl/search-all?query=courtyard&sources=instagram,youtube")
        assert res.status_code == 200
        data = res.json()
        assert "instagram" in data["errors"]
        assert "youtube" in data["results"]
        assert data["results"]["youtube"]["total_items"] == 1


# ============================================================
# 8. SOURCING SOCIALCRAWL-SUPPLIERS ENDPOINT TEST
# ============================================================

def test_sourcing_socialcrawl_suppliers_endpoint():
    """Verify /api/sourcing/socialcrawl-suppliers returns businesses and products."""
    with patch("app.services.socialcrawl_service.search_google_businesses", return_value={"items": [{"name": "Kerala Stone"}], "total_items": 1}), \
         patch("app.services.socialcrawl_service.search_google_shopping", return_value={"items": [{"title": "Laterite Stone"}], "total_items": 1}):
        res = client.get("/api/sourcing/socialcrawl-suppliers?q=laterite+stone&location=Kochi,+Kerala,+India")
        assert res.status_code == 200
        data = res.json()
        assert data["businesses_count"] == 1
        assert data["products_count"] == 1
        assert data["businesses"][0]["name"] == "Kerala Stone"
        assert data["products"][0]["title"] == "Laterite Stone"


# ============================================================
# 9. INSTAGRAM PROFILES & SPECIFIC PROFILE LOOKUP TESTS
# ============================================================

def test_instagram_profiles_search_success():
    """Verify GET /api/socialcrawl/instagram/profiles returns normalized & classified accounts."""
    mock_profile = {
        "user": {
            "username": "kerala_architects_studio",
            "full_name": "Kerala Architecture Studio",
            "biography": "Award-winning tropical modern architecture studio based in Kochi. Residential houses and villas.",
            "profile_pic_url": "https://example.com/pic.jpg",
            "external_url": "https://keralaarchitects.example.com",
            "is_verified": True,
            "follower_count": 85000,
            "following_count": 420,
            "media_count": 650,
            "category_name": "Architectural Designer"
        }
    }

    with patch("app.services.socialcrawl_service.paginated_search", return_value=[mock_profile]):
        res = client.get("/api/socialcrawl/instagram/profiles?query=kerala+architect")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["total_items"] == 1
        profile = data["items"][0]
        assert profile["username"] == "kerala_architects_studio"
        assert profile["full_name"] == "Kerala Architecture Studio"
        assert profile["classification"] == "Architecture Studio"
        assert profile["is_verified"] is True
        assert profile["follower_count"] == 85000
        assert profile["source_platform"] == "instagram"


def test_instagram_profile_detail_success():
    """Verify GET /api/socialcrawl/instagram/profile returns single detailed profile."""
    mock_profile = {
        "user": {
            "username": "jaquar_lighting",
            "full_name": "Jaquar Lighting Showroom",
            "biography": "Official showroom & manufacturer of luxury chandeliers, pendant lights and architectural lighting.",
            "profile_pic_url": "https://example.com/jaquar.jpg",
            "external_url": "https://jaquar.example.com",
            "is_verified": True,
            "follower_count": 120000,
            "category_name": "Lighting Manufacturer"
        }
    }

    with patch("app.services.socialcrawl_service.socialcrawl", return_value={"success": True, "data": mock_profile, "request_id": "req-1"}):
        res = client.get("/api/socialcrawl/instagram/profile?handle=jaquar_lighting")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["handle"] == "jaquar_lighting"
        p = data["data"]
        assert p["username"] == "jaquar_lighting"
        assert p["classification"] == "Showroom" or p["classification"] == "Manufacturer"


def test_instagram_profile_404_handling():
    """Verify non-existent Instagram handle returns 404 cleanly."""
    with patch("app.services.socialcrawl_service.socialcrawl", return_value=None):
        res = client.get("/api/socialcrawl/instagram/profile?handle=non_existent_account_12345")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()


def test_instagram_professional_classification():
    """Verify accurate role classification from bio/category metadata."""
    from app.services.socialcrawl_service import classify_instagram_account

    assert classify_instagram_account("Principal architect at studio", "John Doe", "Architecture") == "Architect"
    assert classify_instagram_account("Landscape architecture & zen gardens", "Green Spaces", "") == "Landscape Architect"
    assert classify_instagram_account("Luxury home builder & turnkey villa developers", "Apex Homes", "") == "Builder"
    assert classify_instagram_account("Leading tile manufacturer and exporter", "Kajaria", "Tiles") == "Manufacturer"
    assert classify_instagram_account("Authorized distributor & wholesale dealer of CPVC pipes", "Sunil Traders", "") == "Product Distributor"
    assert classify_instagram_account("Experience showroom for designer sanitaryware and faucets", "Bath Lux", "") == "Showroom"
    assert classify_instagram_account("Personal blog and travel enthusiast", "Random User", "") == "Unclassified"


def test_instagram_focused_queries_generation():
    """Verify focused queries generator creates targeted queries without dumping the entire taxonomy."""
    from app.services.socialcrawl_service import generate_focused_instagram_queries

    queries = generate_focused_instagram_queries("Chandelier", target="all")
    assert len(queries) <= 4
    for q in queries:
        assert "chandelier" in q.lower()
        # Verify it's a short focused phrase
        assert len(q.split()) <= 4


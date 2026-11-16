from unittest.mock import patch, MagicMock, AsyncMock

from app.services.discovery_adapters import (
    PinterestAdapter,
    InstagramAdapter,
    YouTubeAdapter,
    RedditAdapter,
    GoogleSearchAdapter,
    GoogleShoppingAdapter,
    GooglePlacesAdapter,
)
from app.services.google_places_service import GooglePlacesService
from app.schemas.discovery import SourceStatusEnum


def test_pinterest_adapter_preserves_pin_fields_and_unverified():
    adapter = PinterestAdapter()
    mock_payload = {
        "items": [
            {
                "pin_id": "pin123",
                "title": "Travertine Courtyard Villa Facade",
                "description": "Exterior stone elevation design",
                "image_url": "https://i.pinimg.com/pin123.jpg",
                "board_name": "Stone Facades",
                "creator_name": "Studio Arc",
                "saves_count": 42,
            }
        ],
        "has_more": True,
        "next_cursor": "cur_2",
    }
    with patch("app.services.pinterest_service.search_pinterest_page", return_value=mock_payload):
        results, status, metrics = adapter.fetch("travertine", dry_run=False)

    assert status.status == SourceStatusEnum.SUCCESS
    assert status.has_more is True
    assert status.next_page_token == "cur_2"
    assert len(results) == 1
    item = results[0]
    assert item.source == "pinterest"
    assert item.source_result_id == "pin123"
    assert item.canonical_url == "https://www.pinterest.com/pin/pin123/"
    assert item.image_url == "https://i.pinimg.com/pin123.jpg"
    assert item.source_metadata["board_name"] == "Stone Facades"
    assert item.verification_status == "UNVERIFIED"


def test_instagram_adapter_preserves_reel_fields_and_unverified():
    adapter = InstagramAdapter()
    mock_payload = {
        "items": [
            {
                "shortcode": "REEL99",
                "caption": "Completed project walkthrough of terrazzo flooring",
                "thumbnail_url": "https://cdn.example.com/thumb.jpg",
                "video_url": "https://cdn.example.com/video.mp4",
                "creator_handle": "arch_studio",
                "likes_count": 120,
            }
        ],
        "has_more": False,
    }
    with patch("app.services.socialcrawl_service.search_instagram_reels", return_value=mock_payload):
        results, status, _ = adapter.fetch("terrazzo", dry_run=False)

    assert status.status == SourceStatusEnum.SUCCESS
    assert len(results) == 1
    assert results[0].source == "instagram"
    assert results[0].source_result_id == "REEL99"
    assert results[0].video_url == "https://cdn.example.com/video.mp4"
    assert results[0].verification_status == "UNVERIFIED"


def test_youtube_adapter_and_feed_endpoint_never_verify_channels(client):
    adapter = YouTubeAdapter()
    mock_payload = {
        "items": [
            {
                "video_id": "yt_abc",
                "title": "How to install porcelain slabs",
                "channel_title": "Verified Pro Channel",
                "channel_url": "https://youtube.com/@pro",
                "thumbnail_url": "https://img.youtube.com/vi/yt_abc/hqdefault.jpg",
                "duration": "12:04",
            }
        ],
        "has_more": False,
    }
    with patch("app.services.socialcrawl_service.search_youtube", return_value=mock_payload):
        results, status, _ = adapter.fetch("porcelain slab", dry_run=False)

    assert status.status == SourceStatusEnum.SUCCESS
    assert results[0].creator_name == "Verified Pro Channel"
    assert results[0].verification_status == "UNVERIFIED"

    # Also test /api/feed/youtube-search never emits VERIFIED (curated fallback or live items)
    with patch("app.services.socialcrawl_service.search_youtube", return_value={"items": [
        {
            "title": "How to install porcelain slabs",
            "source_url": "https://www.youtube.com/watch?v=yt_abc",
            "creator_name": "Pro Builder Channel",
            "video_embed_id": "yt_abc",
        }
    ]}):
        resp = client.get("/api/feed/youtube-search", params={"q": "porcelain slab"})
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    assert all(it["verification_status"] == "UNVERIFIED" for it in items)


def test_reddit_adapter_preserves_discussion_fields():
    adapter = RedditAdapter()
    mock_payload = {
        "items": [
            {
                "post_id": "rd_101",
                "title": "AAC block vs red brick cost comparison",
                "selftext": "Real site numbers from our G+2 project",
                "subreddit": "architecture",
                "author": "builder42",
                "source_url": "https://reddit.com/r/architecture/comments/rd_101",
                "score": 88,
                "num_comments": 19,
            }
        ],
        "has_more": False,
    }
    with patch("app.services.socialcrawl_service.search_reddit", return_value=mock_payload):
        results, status, _ = adapter.fetch("aac block", dry_run=False)

    assert status.status == SourceStatusEnum.SUCCESS
    assert results[0].source_attribution == "Reddit (r/architecture)"
    assert results[0].verification_status in ["UNVERIFIED", "COMMUNITY_REVIEW"]
    assert results[0].source_metadata["num_comments"] == 19


def test_google_search_adapter_unconfigured_and_mocked_configured():
    adapter = GoogleSearchAdapter()

    with patch("app.core.config.settings.get_google_image_search_key", return_value="test_google_key_12345"), \
         patch("app.core.config.settings.get_google_image_search_cx", return_value=None):
        results, status, _ = adapter.fetch("clt timber", dry_run=False)
    assert results == []
    assert status.status == SourceStatusEnum.NOT_CONFIGURED
    assert status.error_code == "CUSTOM_SEARCH_CX_NOT_CONFIGURED"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "items": [
            {
                "title": "Cross Laminated Timber Technical Datasheet",
                "snippet": "Fire and acoustic structural guide",
                "link": "https://example.org/clt-guide",
                "displayLink": "example.org",
            }
        ]
    }
    with patch("app.core.config.settings.get_google_image_search_key", return_value="test_google_key_12345"), \
         patch("app.core.config.settings.get_google_image_search_cx", return_value="cx_123456"), \
         patch("requests.get", return_value=mock_resp):
        results, status, _ = adapter.fetch("clt timber", dry_run=False)

    assert status.status == SourceStatusEnum.SUCCESS
    assert len(results) == 1
    assert results[0].original_url == "https://example.org/clt-guide"
    assert results[0].verification_status == "UNVERIFIED"
    assert results[0].source_attribution == "example.org"


def test_google_shopping_adapter_preserves_price_and_merchant():
    adapter = GoogleShoppingAdapter()
    mock_payload = {
        "items": [
            {
                "product_id": "shop_7",
                "title": "Grohe Wall Hung WC",
                "price": "18500",
                "currency": "INR",
                "merchant_name": "BathWorld India",
                "source_url": "https://bathworld.example/wc",
                "image_url": "https://bathworld.example/wc.jpg",
                "rating": 4.6,
                "reviews_count": 31,
                "availability": "In Stock",
            }
        ]
    }
    with patch("app.services.socialcrawl_service.search_google_shopping", return_value=mock_payload):
        results, status, _ = adapter.fetch("wall hung wc", dry_run=False)

    assert status.status == SourceStatusEnum.SUCCESS
    assert len(results) == 1
    assert results[0].price == 18500.0
    assert results[0].currency == "INR"
    assert results[0].creator_name == "BathWorld India"
    assert results[0].source_attribution == "Google Shopping (BathWorld India)"
    assert results[0].verification_status == "UNVERIFIED"


def test_google_places_adapter_no_hardcoded_kochi_and_upstream_error_surfaced():
    adapter = GooglePlacesAdapter()
    queries_no_city = adapter.build_queries("marble supplier", taxonomy_context={})
    assert all("kochi" not in q.lower() and "kerala" not in q.lower() for q in queries_no_city)

    queries_pune = adapter.build_queries("marble supplier", taxonomy_context={"city": "Pune"})
    assert any("Pune" in q for q in queries_pune)

    mock_places_resp = {
        "configured": True,
        "places": [
            {
                "place_id": "ChIJ_123",
                "name": "Deccan Stone Emporium",
                "address": "Baner Road, Pune",
                "city": "Pune",
                "state": "Maharashtra",
                "phone": "+91-20-55551234",
                "website": "https://deccanstone.example",
                "primary_type": "building_materials_store",
                "types": ["building_materials_store"],
                "rating": 4.4,
                "user_rating_count": 58,
                "google_maps_uri": "https://maps.google.com/?cid=123",
            }
        ],
    }
    with patch("app.services.google_places_service.GooglePlacesService.search_nearby_suppliers", new=AsyncMock(return_value=mock_places_resp)), \
         patch("app.services.google_places_service.GooglePlacesService.is_configured", return_value=True):
        results, status, _ = adapter.fetch("marble supplier", dry_run=False, taxonomy_context={"city": "Pune"})

    assert status.status == SourceStatusEnum.SUCCESS
    assert len(results) == 1
    assert results[0].verification_status == "POTENTIAL_GOOGLE_PLACE"
    assert results[0].source_result_id == "ChIJ_123"
    assert results[0].source_metadata.get("phone") == "+91-20-55551234" or results[0].address == "Baner Road, Pune"

    # Verify GooglePlacesService surfaces upstream error instead of silently returning []
    svc = GooglePlacesService(api_key="fake_key_12345")
    mock_err_resp = MagicMock()
    mock_err_resp.status_code = 403
    mock_err_resp.text = "REQUEST_DENIED: API key expired"
    mock_err_resp.json.return_value = {"error": {"message": "API key expired"}}
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_err_resp)
        import asyncio
        out = asyncio.run(svc.search_nearby_suppliers("marble", city="Pune"))
    err = out.get("error") or out.get("upstream_error")
    assert err is not None
    assert "403" in str(err) or "expired" in str(err)

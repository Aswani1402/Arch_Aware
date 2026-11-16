"""
Nivora — Phase 5B Stage 2 Multi-Source Discovery Orchestration Tests
Tests the 7 source adapters, query generation, normalization, 3D classification,
deduplication, relevance scoring, and all 12 edge and failure cases from Section 9.
Zero live external API calls (100% mock-based fixtures).
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.schemas.discovery import (
    SourceStatusEnum,
    DiscoveryOverallStatusEnum,
    DiscoveryTabEnum,
    ContentTypeEnum,
    DiscoveryClassificationEnum,
    MetadataClassificationEnum,
    SourceStatusReport,
    SourceExecutionMetrics,
    NormalizedDiscoveryResult,
    DiscoveryPagination,
    UnifiedDiscoveryResponse,
)
from app.services.search_orchestration_service import (
    SearchOrchestrationService,
    search_orchestration_service,
)
from app.services.discovery_adapters import (
    BaseSourceAdapter,
    PinterestAdapter,
    InstagramAdapter,
    YouTubeAdapter,
    RedditAdapter,
    GoogleSearchAdapter,
    GoogleShoppingAdapter,
    GooglePlacesAdapter,
)


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def service():
    return SearchOrchestrationService()


@pytest.fixture
def mock_pinterest_items():
    return {
        "success": True,
        "items": [
            {
                "pin_id": "pin_101",
                "id": "pin_101",
                "title": "Athangudi Handcrafted Tiles Verandah",
                "description": "Traditional Chettinad floral pattern handmade floor tiles.",
                "image_url": "https://i.pinimg.com/736x/athangudi_101.jpg",
                "thumbnail_url": "https://i.pinimg.com/236x/athangudi_101.jpg",
                "creator_name": "Heritage Homes Architecture",
                "creator_url": "https://pinterest.com/heritagehomes",
                "board_name": "Flooring Ideas",
                "saves_count": 1420
            },
            {
                "pin_id": "pin_102",
                "id": "pin_102",
                "title": "Modern Cantilever Staircase",
                "description": "Floating teak wood treads on steel spine beam.",
                "image_url": "https://i.pinimg.com/736x/staircase_102.jpg",
                "thumbnail_url": "https://i.pinimg.com/236x/staircase_102.jpg",
                "creator_name": "Studio Minimal",
                "creator_url": "https://pinterest.com/studiominimal",
                "board_name": "Staircases",
                "saves_count": 890
            }
        ],
        "has_more": True,
        "next_cursor": "pin_cursor_page_2"
    }


@pytest.fixture
def mock_instagram_items():
    return {
        "success": True,
        "items": [
            {
                "reel_id": "reel_201",
                "shortcode": "C1xyzReelA",
                "caption": "Site progress: Laying traditional Athangudi cement tiles in the courtyard! #construction #architecture",
                "thumbnail_url": "https://scontent.cdninstagram.com/reel_201_thumb.jpg",
                "video_url": "https://scontent.cdninstagram.com/reel_201_video.mp4",
                "creator_name": "Kochi Build Studio",
                "creator_handle": "kochibuild",
                "likes_count": 3450,
                "views_count": 48000
            }
        ],
        "has_more": True,
        "next_cursor": "insta_cursor_2"
    }


@pytest.fixture
def mock_youtube_items():
    return {
        "success": True,
        "items": [
            {
                "video_embed_id": "yt_301",
                "video_id": "yt_301",
                "title": "How to Install Athangudi Tiles Step by Step Tutorial",
                "description": "Complete masonry and polishing guide for handmade hydraulic tiles.",
                "thumbnail_url": "https://i.ytimg.com/vi/yt_301/hqdefault.jpg",
                "channel_title": "Architectural Craft Guide",
                "channel_url": "https://youtube.com/@archcraft",
                "duration": "14:25",
                "views_count": 89200
            }
        ],
        "has_more": False,
        "next_cursor": None
    }


@pytest.fixture
def mock_reddit_items():
    return {
        "success": True,
        "items": [
            {
                "post_id": "red_401",
                "title": "Athangudi tiles vs Vitrified tiles cost and maintenance in humid climate",
                "selftext": "We are building in Kerala and wondering about the durability of Athangudi tiles...",
                "source_url": "https://reddit.com/r/InteriorDesign/comments/red_401/",
                "media_url": "https://i.redd.it/red_401.jpg",
                "author": "kerala_homebuilder",
                "subreddit": "InteriorDesign",
                "score": 142,
                "num_comments": 38
            }
        ],
        "has_more": False,
        "next_cursor": None
    }


@pytest.fixture
def mock_shopping_items():
    return {
        "success": True,
        "items": [
            {
                "product_id": "shop_501",
                "title": "Athangudi Heritage Cement Floor Tile 8x8 inch Floral",
                "description": "Handmade mineral oxide pigment hydraulic pressed tile.",
                "image_url": "https://shopping.google.com/images/tile_501.jpg",
                "product_url": "https://merchant.example.com/tiles/athangudi-floral-8x8",
                "price": 65.0,
                "currency": "INR",
                "merchant_name": "Heritage Tile Co",
                "rating": 4.7,
                "reviews_count": 28
            }
        ],
        "has_more": False
    }


@pytest.fixture
def mock_places_items():
    return {
        "success": True,
        "places": [
            {
                "place_id": "place_601",
                "google_place_id": "place_601",
                "name": "Chettinad Tile & Stone Depot",
                "address": "Ernakulam South, Kochi, Kerala 682016",
                "phone": "+91 484 235 6789",
                "website": "https://chettinadtiles.example.com",
                "business_type": "Tile Store & Architectural Supplier",
                "rating": 4.6,
                "user_ratings_total": 84,
                "google_maps_url": "https://maps.google.com/?cid=601"
            }
        ]
    }


# ==============================================================================
# 1. ADAPTER REGISTRATION & ALIAS ROUTING
# ==============================================================================

def test_adapter_registry(service):
    """Verify that all 7 adapters are properly registered in the service."""
    assert "pinterest" in service.adapters
    assert "instagram" in service.adapters
    assert "youtube" in service.adapters
    assert "reddit" in service.adapters
    assert "google_search" in service.adapters
    assert "google_shopping" in service.adapters
    assert "google_places" in service.adapters

    assert isinstance(service.adapters["pinterest"], PinterestAdapter)
    assert isinstance(service.adapters["instagram"], InstagramAdapter)
    assert isinstance(service.adapters["youtube"], YouTubeAdapter)
    assert isinstance(service.adapters["reddit"], RedditAdapter)
    assert isinstance(service.adapters["google_search"], GoogleSearchAdapter)
    assert isinstance(service.adapters["google_shopping"], GoogleShoppingAdapter)
    assert isinstance(service.adapters["google_places"], GooglePlacesAdapter)


def test_source_aliases(service):
    """Verify that alias mapping resolves cleanly for all synonyms."""
    assert service.source_alias_map["reels"] == "instagram"
    assert service.source_alias_map["pin"] == "pinterest"
    assert service.source_alias_map["yt"] == "youtube"
    assert service.source_alias_map["shopping"] == "google_shopping"
    assert service.source_alias_map["google_business"] == "google_places"
    assert service.source_alias_map["places"] == "google_places"
    assert service.source_alias_map["suppliers"] == "google_places"
    assert service.source_alias_map["web"] == "google_search"


def test_twitter_is_disabled(service):
    """Verify that X / Twitter is disabled and reports DISABLED status."""
    resp = service.orchestrate_discovery("Modern Villa", sources=["twitter", "x"])
    assert "twitter" in resp.source_statuses
    assert resp.source_statuses["twitter"].status == SourceStatusEnum.DISABLED
    assert resp.source_metrics["twitter"].status == SourceStatusEnum.DISABLED


# ==============================================================================
# 2. QUERY EXPANSION & TAXONOMY CONTEXT RESOLUTION
# ==============================================================================

def test_resolve_taxonomy_context(service):
    """Verify taxonomy context lookup using keyword_library."""
    ctx = service.resolve_taxonomy_context("Athangudi Tiles")
    assert ctx["query"] == "Athangudi Tiles"
    assert isinstance(ctx.get("synonyms"), list)
    assert len(ctx.get("synonyms", [])) > 0
    # Category / subcategory should be populated from taxonomy
    assert "category" in ctx or "synonyms" in ctx


def test_adapter_query_builders():
    """Verify platform-specific query generation across all 7 adapters."""
    p_adapter = PinterestAdapter()
    p_queries = p_adapter.build_queries("Staircase")
    assert any("architectural design" in q for q in p_queries)

    ig_adapter = InstagramAdapter()
    ig_queries = ig_adapter.build_queries("Staircase")
    assert any("walkthrough" in q for q in ig_queries)

    yt_adapter = YouTubeAdapter()
    yt_queries = yt_adapter.build_queries("Staircase")
    assert any("project walkthrough" in q for q in yt_queries)

    r_adapter = RedditAdapter()
    r_queries = r_adapter.build_queries("Staircase")
    assert any("cost review" in q or "materials discussion" in q for q in r_queries)

    gs_adapter = GoogleSearchAdapter()
    gs_queries = gs_adapter.build_queries("Staircase")
    assert "architectural Staircase" in gs_queries

    shop_adapter = GoogleShoppingAdapter()
    shop_queries = shop_adapter.build_queries("Staircase")
    assert any("Staircase" in q for q in shop_queries)
    assert all("material specifications" not in q.lower() for q in shop_queries)

    places_adapter = GooglePlacesAdapter()
    places_queries = places_adapter.build_queries("Staircase", {"city": "Kochi"})
    assert any("Kochi" in q for q in places_queries)


# ==============================================================================
# 3. NORMALIZATION & 3D CLASSIFICATION MAPPING
# ==============================================================================

@patch("app.services.pinterest_service.search_pinterest_page")
@patch("app.services.socialcrawl_service.search_instagram_reels")
@patch("app.services.socialcrawl_service.search_youtube")
@patch("app.services.socialcrawl_service.search_reddit")
@patch("app.services.socialcrawl_service.search_google_shopping")
@patch("app.services.google_places_service.GooglePlacesService.search_nearby_suppliers")
def test_normalization_and_3d_dimensions(
    mock_places, mock_shop, mock_reddit, mock_yt, mock_ig, mock_pin,
    service, mock_pinterest_items, mock_instagram_items, mock_youtube_items,
    mock_reddit_items, mock_shopping_items, mock_places_items
):
    """Verify that all raw items are mapped to 3 independent dimensions correctly."""
    mock_pin.return_value = mock_pinterest_items
    mock_ig.return_value = mock_instagram_items
    mock_yt.return_value = mock_youtube_items
    mock_reddit.return_value = mock_reddit_items
    mock_shop.return_value = mock_shopping_items
    mock_places.return_value = mock_places_items

    resp = service.orchestrate_discovery("Athangudi Tiles", dry_run=False)

    # 1. Pinterest item
    pin_res = next(r for r in resp.results if r.source == "pinterest")
    assert pin_res.content_type == "material_specimen"
    assert pin_res.discovery_classification == DiscoveryClassificationEnum.INSPIRATION
    assert pin_res.metadata_classification == MetadataClassificationEnum.MATERIAL_SPECIFICATION
    assert pin_res.verification_status == "UNVERIFIED"

    # 2. Instagram reel (with 'construction progress' keywords in caption)
    ig_res = next(r for r in resp.results if r.source == "instagram")
    assert ig_res.content_type == "architectural_reel"
    assert ig_res.discovery_classification == DiscoveryClassificationEnum.WORK_IN_PROGRESS
    assert ig_res.metadata_classification == MetadataClassificationEnum.CONSTRUCTION_PROGRESS

    # 3. YouTube tutorial walkthrough
    yt_res = next(r for r in resp.results if r.source == "youtube")
    assert yt_res.content_type == "youtube_walkthrough"
    assert yt_res.discovery_classification == DiscoveryClassificationEnum.TUTORIAL
    assert yt_res.metadata_classification == MetadataClassificationEnum.INSTALLATION_GUIDE
    assert yt_res.verification_status == "UNVERIFIED"

    # 4. Reddit discussion
    red_res = next(r for r in resp.results if r.source == "reddit")
    assert red_res.content_type == "architectural_discussion"
    assert red_res.discovery_classification == DiscoveryClassificationEnum.DISCUSSION
    assert red_res.metadata_classification == MetadataClassificationEnum.COST_BREAKDOWN

    # 5. Google Shopping product
    shop_res = next(r for r in resp.results if r.source == "google_shopping")
    assert shop_res.content_type == "manufacturer_product"
    assert shop_res.discovery_classification == DiscoveryClassificationEnum.PRODUCT
    assert shop_res.metadata_classification == MetadataClassificationEnum.PRODUCT_CATALOG
    assert shop_res.price == 65.0
    assert shop_res.currency == "INR"

    # 6. Google Places business
    place_res = next(r for r in resp.results if r.source == "google_places")
    assert place_res.content_type == "supplier_business"
    assert place_res.discovery_classification == DiscoveryClassificationEnum.SUPPLIER
    assert place_res.metadata_classification == MetadataClassificationEnum.SUPPLIER_PROFILE
    assert place_res.verification_status == "POTENTIAL_GOOGLE_PLACE"


# ==============================================================================
# 4. DEDUPLICATION & PRESERVATION OF DISTINCT PRODUCTS
# ==============================================================================

def test_deduplicate_identical_url_and_id(service):
    """Verify that exact URL or source ID duplicates are removed."""
    items = [
        NormalizedDiscoveryResult(
            source="pinterest",
            source_result_id="pin_999",
            original_url="https://pinterest.com/pin/999/",
            canonical_url="https://pinterest.com/pin/999/",
            title="Modern Villa Elevation"
        ),
        NormalizedDiscoveryResult(
            source="pinterest",
            source_result_id="pin_999",
            original_url="https://pinterest.com/pin/999/?utm_source=test",
            canonical_url="https://pinterest.com/pin/999/",
            title="Modern Villa Elevation"
        )
    ]
    deduped, dups = service.deduplicate_results(items)
    assert len(deduped) == 1
    assert dups == 1


def test_deduplicate_preserves_distinct_products_sharing_image(service):
    """
    Verify requirement:
    Distinguish genuine duplicates from distinct products that share manufacturer imagery.
    """
    items = [
        NormalizedDiscoveryResult(
            source="google_shopping",
            source_result_id="prod_001",
            original_url="https://merchant.example.com/faucet-chrome",
            image_url="https://images.example.com/kohler_faucet_catalog.jpg",
            title="Kohler Purist Single Hole Bathroom Sink Faucet Polished Chrome"
        ),
        NormalizedDiscoveryResult(
            source="google_shopping",
            source_result_id="prod_002",
            original_url="https://merchant.example.com/faucet-matte-black",
            image_url="https://images.example.com/kohler_faucet_catalog.jpg",
            title="Kohler Purist Single Hole Bathroom Sink Faucet Matte Black 2.5GPM"
        )
    ]
    deduped, dups = service.deduplicate_results(items)
    # Distinct variants sharing catalog image MUST be preserved!
    assert len(deduped) == 2
    assert dups == 0


def test_deduplicate_removes_composite_duplicate_image_and_title(service):
    """Verify that items with identical image AND identical title tokens are removed."""
    items = [
        NormalizedDiscoveryResult(
            source="pinterest",
            source_result_id="pin_1",
            original_url="https://pinterest.com/pin/1",
            image_url="https://images.example.com/house.jpg",
            title="Luxury Minimalist Villa Facade Architecture"
        ),
        NormalizedDiscoveryResult(
            source="instagram",
            source_result_id="ig_1",
            original_url="https://instagram.com/p/1",
            image_url="https://images.example.com/house.jpg",
            title="Luxury Minimalist Villa Facade Architecture"
        )
    ]
    deduped, dups = service.deduplicate_results(items)
    assert len(deduped) == 1
    assert dups == 1


# ==============================================================================
# 5. TAB ROUTING & RELEVANCE SCORING
# ==============================================================================

@patch("app.services.pinterest_service.search_pinterest_page")
@patch("app.services.socialcrawl_service.search_google_shopping")
def test_tab_filtering_products_suppliers(mock_shop, mock_pin, service, mock_pinterest_items, mock_shopping_items):
    """Verify filtering when tab='products_suppliers' is requested."""
    mock_pin.return_value = mock_pinterest_items
    mock_shop.return_value = mock_shopping_items

    resp = service.orchestrate_discovery(
        "Athangudi Tiles",
        sources=["pinterest", "google_shopping"],
        tab=DiscoveryTabEnum.PRODUCTS_SUPPLIERS,
        dry_run=False
    )
    assert resp.active_discovery_tab == DiscoveryTabEnum.PRODUCTS_SUPPLIERS
    assert len(resp.results) > 0
    # Every returned result must have products_suppliers in its relevant_tabs
    for r in resp.results:
        assert DiscoveryTabEnum.PRODUCTS_SUPPLIERS.value in r.relevant_tabs


# ==============================================================================
# 6. THE 12 FAILURE & EDGE CASE SCENARIOS (SECTION 9)
# ==============================================================================

# Scenario 1: All configured sources succeed
@patch("app.services.pinterest_service.search_pinterest_page")
@patch("app.services.socialcrawl_service.search_instagram_reels")
def test_scenario_1_all_configured_sources_succeed(mock_ig, mock_pin, service, mock_pinterest_items, mock_instagram_items):
    mock_pin.return_value = mock_pinterest_items
    mock_ig.return_value = mock_instagram_items

    resp = service.orchestrate_discovery("Villa", sources=["pinterest", "instagram"], dry_run=False)
    assert resp.overall_status == DiscoveryOverallStatusEnum.SUCCESS
    assert resp.source_statuses["pinterest"].status == SourceStatusEnum.SUCCESS
    assert resp.source_statuses["instagram"].status == SourceStatusEnum.SUCCESS
    assert len(resp.results) == 3


# Scenario 2: Pinterest succeeds while Instagram fails
@patch("app.services.pinterest_service.search_pinterest_page")
@patch("app.services.socialcrawl_service.search_instagram_reels")
def test_scenario_2_partial_success_one_source_fails(mock_ig, mock_pin, service, mock_pinterest_items):
    mock_pin.return_value = mock_pinterest_items
    mock_ig.side_effect = TimeoutError("Instagram upstream connection timed out after 46s")

    resp = service.orchestrate_discovery("Villa", sources=["pinterest", "instagram"], dry_run=False)
    assert resp.overall_status == DiscoveryOverallStatusEnum.PARTIAL_SUCCESS
    assert resp.source_statuses["pinterest"].status == SourceStatusEnum.SUCCESS
    assert resp.source_statuses["instagram"].status == SourceStatusEnum.FAILED
    assert len(resp.results) == 2
    assert len(resp.errors) == 1
    assert resp.errors[0]["source"] == "instagram"


# Scenario 3: YouTube returns no results (EMPTY, not FAILED)
@patch("app.services.socialcrawl_service.search_youtube")
def test_scenario_3_youtube_empty_results(mock_yt, service):
    mock_yt.return_value = {"success": True, "items": [], "has_more": False}

    resp = service.orchestrate_discovery("Obscure Material XYZ", sources=["youtube"], dry_run=False)
    assert resp.overall_status == DiscoveryOverallStatusEnum.EMPTY
    assert resp.source_statuses["youtube"].status == SourceStatusEnum.EMPTY
    assert resp.source_statuses["youtube"].result_count == 0


# Scenario 4: Google Search is NOT_CONFIGURED
def test_scenario_4_google_search_not_configured(service):
    resp = service.orchestrate_discovery("Staircase", sources=["google_search"], dry_run=False)
    assert resp.source_statuses["google_search"].status == SourceStatusEnum.NOT_CONFIGURED
    assert resp.source_statuses["google_search"].error_code == "CUSTOM_SEARCH_CX_NOT_CONFIGURED"
    assert any("not configured" in w for w in resp.warnings)


# Scenario 5: Google Shopping returns incomplete product data (missing merchant & price)
@patch("app.services.socialcrawl_service.search_google_shopping")
def test_scenario_5_google_shopping_incomplete_data(mock_shop, service):
    mock_shop.return_value = {
        "success": True,
        "items": [
            {
                "product_id": "incomplete_1",
                "title": "Custom Welded Beam Fitting",
                # No price, no merchant_name
                "product_url": "https://example.com/beam"
            }
        ]
    }
    resp = service.orchestrate_discovery("Steel Beam", sources=["google_shopping"], dry_run=False)
    assert resp.overall_status == DiscoveryOverallStatusEnum.SUCCESS
    prod = resp.results[0]
    assert prod.price is None  # Never fabricated
    assert prod.creator_name is None
    assert prod.title == "Custom Welded Beam Fitting"


# Scenario 6: Google Places returns potential business without contact info
@patch("app.services.google_places_service.GooglePlacesService.search_nearby_suppliers")
def test_scenario_6_places_without_contact_info(mock_places, service):
    mock_places.return_value = {
        "places": [
            {
                "place_id": "place_no_contact",
                "name": "Local Timber Mill",
                "address": "Kochi Industrial Area",
                "phone": None,
                "website": None,
                "business_type": "Timber Supplier"
            }
        ]
    }
    resp = service.orchestrate_discovery("Timber", sources=["google_places"], dry_run=False)
    place = resp.results[0]
    assert place.phone is None
    assert place.website is None
    assert place.verification_status == "POTENTIAL_GOOGLE_PLACE"
    assert place.source_metadata.get("is_potential") is True


# Scenario 7: Reddit returns duplicate content
@patch("app.services.socialcrawl_service.search_reddit")
def test_scenario_7_reddit_duplicate_content(mock_reddit, service):
    mock_reddit.return_value = {
        "success": True,
        "items": [
            {
                "post_id": "dup_post_1",
                "source_url": "https://reddit.com/r/arch/post1",
                "title": "Best cement for coastal homes in Kerala",
                "selftext": "Discussion on salt resistance..."
            },
            {
                "post_id": "dup_post_1",
                "source_url": "https://reddit.com/r/arch/post1",
                "title": "Best cement for coastal homes in Kerala",
                "selftext": "Discussion on salt resistance..."
            }
        ]
    }
    resp = service.orchestrate_discovery("Coastal Cement", sources=["reddit"], dry_run=False)
    assert len(resp.results) == 1
    assert resp.source_metrics["reddit"].duplicate_count == 1
    assert resp.source_metrics["reddit"].unique_result_count == 1


# Scenario 8: One source returns malformed data
@patch("app.services.pinterest_service.search_pinterest_page")
@patch("app.services.socialcrawl_service.search_instagram_reels")
def test_scenario_8_one_source_returns_malformed_data(mock_ig, mock_pin, service, mock_pinterest_items):
    mock_pin.return_value = mock_pinterest_items
    mock_ig.return_value = "This is not a dict or valid JSON response"

    resp = service.orchestrate_discovery("Courtyard", sources=["pinterest", "instagram"], dry_run=False)
    assert resp.overall_status == DiscoveryOverallStatusEnum.PARTIAL_SUCCESS
    assert resp.source_statuses["pinterest"].status == SourceStatusEnum.SUCCESS
    assert resp.source_statuses["instagram"].status in (SourceStatusEnum.EMPTY, SourceStatusEnum.FAILED)
    assert len(resp.results) == 2


# Scenario 9: A provider returns rate-limit error (429)
@patch("app.services.pinterest_service.search_pinterest_page")
def test_scenario_9_provider_rate_limited(mock_pin, service):
    mock_pin.side_effect = Exception("HTTP 429 Too Many Requests: Rate limit exceeded for Pinterest API")

    resp = service.orchestrate_discovery("Staircase", sources=["pinterest"], dry_run=False)
    assert resp.overall_status == DiscoveryOverallStatusEnum.RATE_LIMITED
    assert resp.source_statuses["pinterest"].status == SourceStatusEnum.RATE_LIMITED
    assert resp.source_statuses["pinterest"].error_code == "RATE_LIMITED"


# Scenario 10: A provider returns quota-exhausted error (credits balance)
@patch("app.services.socialcrawl_service.search_instagram_reels")
def test_scenario_10_provider_quota_exhausted(mock_ig, service):
    mock_ig.side_effect = Exception("402 Payment Required: Insufficient credits. Your monthly quota is exhausted.")

    resp = service.orchestrate_discovery("Staircase", sources=["instagram"], dry_run=False)
    assert resp.source_statuses["instagram"].status == SourceStatusEnum.QUOTA_EXHAUSTED
    assert resp.source_statuses["instagram"].error_code == "QUOTA_EXHAUSTED"


# Scenario 11: Provider does not support pagination
@patch("app.services.socialcrawl_service.search_google_shopping")
def test_scenario_11_provider_no_pagination(mock_shop, service, mock_shopping_items):
    mock_shop.return_value = mock_shopping_items

    resp = service.orchestrate_discovery("Tiles", sources=["google_shopping"], dry_run=False)
    assert resp.source_statuses["google_shopping"].has_more is False
    assert resp.source_statuses["google_shopping"].next_page_token is None
    assert resp.source_metrics["google_shopping"].pagination_availability is False


# Scenario 12: Provider returns empty next-page token
@patch("app.services.pinterest_service.search_pinterest_page")
def test_scenario_12_empty_next_page_token(mock_pin, service):
    mock_pin.return_value = {
        "success": True,
        "items": [
            {"pin_id": "p_last", "id": "p_last", "title": "Final Pin", "source_url": "https://pinterest.com/pin/last"}
        ],
        "has_more": False,
        "next_cursor": ""
    }

    resp = service.orchestrate_discovery("Minimal", sources=["pinterest"], dry_run=False)
    assert resp.source_statuses["pinterest"].has_more is False
    assert not resp.source_statuses["pinterest"].next_page_token


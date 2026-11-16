"""
Nivora — Phase 5B Stage 2.1 Acceptance Corrections Test Suite
Covers:
1. YouTube verification-status correction (strictly UNVERIFIED).
2. Pinterest content-type classification (8 specific architectural evidence cases).
3. Async discovery orchestration:
   - All sources succeed
   - Partial success when one source fails
   - Google Places native async direct await
   - Per-source timeout handling
   - Cancellation handling
   - Semaphore concurrency bounding
   - Sync vs async orchestration parity
4. Interactive Request Safety & Provider Budget Manager:
   - Dual-tier sliding-window rate limiting (User: 60/hr, Anon: 15/hr)
   - Salted SHA-256 IP anonymization (no raw PII/IP stored)
   - Untrusted client header protection
   - Source count & per-request credit budget enforcement
   - Zero credit burn invariant on blocked requests
"""

import asyncio
import time
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from starlette.requests import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    classify_pinterest_pin,
)
from app.services.discovery_guard import (
    DiscoveryRequestGuard,
    ProviderBudgetManager,
    discovery_request_guard,
    provider_budget_manager,
    GuardDecision,
    resolve_client_ip,
    extract_verified_client_ip,
)
from app.api.auth import get_optional_current_user
from app.core.security import create_access_token
from app.core.database import Base
from app.models.models import User


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def service():
    return SearchOrchestrationService()


@pytest.fixture
def fresh_guard():
    return DiscoveryRequestGuard(
        user_rate_limit=60,
        anon_rate_limit=15,
        window_seconds=3600,
        salt="test_salt_secret_123"
    )


@pytest.fixture
def fresh_budget():
    return ProviderBudgetManager(
        max_sources_per_request=7,
        max_credits_per_request=20,
        daily_interactive_credit_cap=500
    )


@pytest.fixture
def mock_common_results():
    return {
        "pin": {
            "success": True,
            "items": [{
                "pin_id": "pin_test_1",
                "title": "Minimalist Teak Wood Staircase",
                "description": "Cantilever staircase with timber treads and glass railing detail.",
                "image_url": "https://i.pinimg.com/736x/pin_test_1.jpg",
                "creator_name": "ModernWoodStudio",
                "board_name": "Architectural Details",
                "source_url": "https://pinterest.com/pin/pin_test_1/"
            }]
        },
        "ig": {
            "success": True,
            "items": [{
                "reel_id": "reel_test_1",
                "caption": "Site inspection of cantilever steel staircase framing #architecture #construction",
                "media_url": "https://instagram.example.com/reel1.mp4",
                "creator_name": "kerala_architects",
                "post_url": "https://instagram.com/reel/reel_test_1/"
            }]
        },
        "yt": {
            "success": True,
            "items": [{
                "video_embed_id": "yt_test_1",
                "title": "How to Build a Floating Staircase Step by Step Walkthrough",
                "description": "Architectural fabrication and installation tutorial.",
                "thumbnail_url": "https://i.ytimg.com/vi/yt_test_1/hqdefault.jpg",
                "channel_title": "ArchCraft",
                "duration": "12:30",
                "views_count": 45000
            }]
        },
        "red": {
            "success": True,
            "items": [{
                "post_id": "red_test_1",
                "title": "Cantilever staircase structural safety and cost comparison",
                "selftext": "Looking for advice on steel spine versus wall embedment.",
                "source_url": "https://reddit.com/r/architecture/comments/red_test_1/",
                "author": "homeowner_kerala"
            }]
        },
        "shop": {
            "success": True,
            "items": [{
                "product_id": "shop_test_1",
                "title": "Tempered Glass Staircase Railing System 12mm",
                "description": "Frameless architectural railing hardware kit.",
                "image_url": "https://shopping.google.com/images/shop_test_1.jpg",
                "product_url": "https://store.example.com/railing-kit",
                "price": 4500.0,
                "currency": "INR",
                "merchant_name": "Toughened Glass Direct"
            }]
        },
        "places": {
            "success": True,
            "places": [{
                "place_id": "places_test_1",
                "google_place_id": "places_test_1",
                "name": "Kochi Architectural Hardware & Stairs",
                "address": "MG Road, Kochi, Kerala 682016",
                "phone": "+91 484 238 9000",
                "website": "https://kochihardware.example.com",
                "business_type": "Architectural Hardware Supplier",
                "rating": 4.8,
                "user_ratings_total": 112,
                "google_maps_url": "https://maps.google.com/?cid=places_test_1"
            }]
        }
    }


# ==============================================================================
# 1. YOUTUBE VERIFICATION-STATUS CORRECTION
# ==============================================================================

def test_youtube_results_are_strictly_unverified(mock_common_results):
    """
    Architectural Integrity Invariant:
    Video creator or channel provenance does NOT constitute verified professional status.
    YouTubeAdapter must strictly output verification_status='UNVERIFIED'.
    """
    adapter = YouTubeAdapter()
    with patch("app.services.socialcrawl_service.is_socialcrawl_configured", return_value=True), \
         patch("app.services.socialcrawl_service.search_youtube", return_value=mock_common_results["yt"]):

        items, status, metrics = adapter.fetch("Staircase")
        assert len(items) == 1
        yt_item = items[0]
        assert yt_item.verification_status == "UNVERIFIED"
        assert yt_item.verification_status != "VERIFIED"


# ==============================================================================
# 2. PINTEREST CONTENT-TYPE CLASSIFICATION (8 CASES)
# ==============================================================================

def test_pinterest_case1_architectural_project():
    """Case 1: Architectural project / completed residence / villa."""
    ct, disc, meta = classify_pinterest_pin(
        title="Modern Tropical Villa Architecture",
        description="Contemporary residence designed by Studio Arch, completed in Bangalore.",
        board="Villa Architecture"
    )
    assert ct == "architectural_project"
    assert disc in (DiscoveryClassificationEnum.ARCHITECT_PORTFOLIO, DiscoveryClassificationEnum.INSPIRATION)
    assert meta == MetadataClassificationEnum.ARCHITECTURAL_PROJECT


def test_pinterest_case2_interior_design():
    """Case 2: Interior design / room styling."""
    ct, disc, meta = classify_pinterest_pin(
        title="Minimalist Scandinavian Living Room Interior",
        description="Warm wood furniture and neutral false ceiling design styling.",
        board="Living Room Decor"
    )
    assert ct == "architectural_project"
    assert disc == DiscoveryClassificationEnum.INTERIOR_DESIGN_PROJECT
    assert meta == MetadataClassificationEnum.INTERIOR_DESIGN


def test_pinterest_case3_facade_design():
    """Case 3: Facade design / exterior elevation."""
    ct, disc, meta = classify_pinterest_pin(
        title="Parametric Brick Facade Exterior Elevation",
        description="Perforated jali facade design creating light and shade patterns on building exterior.",
        board="Building Facades"
    )
    assert ct == "architectural_project"
    assert disc == DiscoveryClassificationEnum.INSPIRATION
    assert meta == MetadataClassificationEnum.FACADE_DETAIL


def test_pinterest_case4_architectural_drawing():
    """Case 4: Architectural drawing / floor plan / section."""
    ct, disc, meta = classify_pinterest_pin(
        title="Duplex House Ground Floor Plan CAD Blueprint",
        description="Technical architectural drawing layout with dimension lines and room schedule.",
        board="Floor Plans"
    )
    assert ct == "architectural_project"
    assert disc == DiscoveryClassificationEnum.INSPIRATION
    assert meta == MetadataClassificationEnum.DETAIL_DRAWING


def test_pinterest_case5_product_photo():
    """Case 5: Product photograph / furniture / fixture."""
    ct, disc, meta = classify_pinterest_pin(
        title="Solid Teak Dining Table Furniture",
        description="Handcrafted wooden dining table with brass inlay product catalogue piece.",
        board="Designer Furniture"
    )
    assert ct == "manufacturer_product"
    assert disc == DiscoveryClassificationEnum.PRODUCT
    assert meta == MetadataClassificationEnum.PRODUCT_CATALOG


def test_pinterest_case6_material_specimen():
    """Case 6: Material specimen / swatch / tile sample."""
    ct, disc, meta = classify_pinterest_pin(
        title="Calacatta Gold Marble Slab Material Specimen",
        description="Natural Italian marble texture sample swatch for countertop specification.",
        board="Material Swatches"
    )
    assert ct == "material_specimen"
    assert disc == DiscoveryClassificationEnum.INSPIRATION
    assert meta == MetadataClassificationEnum.MATERIAL_SPECIFICATION


def test_pinterest_case7_installation_guide():
    """Case 7: Construction / installation guide / technical tutorial."""
    ct, disc, meta = classify_pinterest_pin(
        title="How to Install Cantilever Floating Staircase Step-by-Step",
        description="Complete structural fabrication and installation guide for concealed stringer stairs.",
        board="Construction Guides"
    )
    assert ct == "installation_demo"
    assert disc == DiscoveryClassificationEnum.TUTORIAL
    assert meta == MetadataClassificationEnum.INSTALLATION_GUIDE


def test_pinterest_case8_insufficient_evidence_fallback():
    """Case 8: Insufficient evidence fallback -> returns None."""
    ct, disc, meta = classify_pinterest_pin(
        title="Aesthetic Vibes",
        description="Just pure mood inspiration.",
        board="General Ideas"
    )
    assert ct is None
    assert disc == DiscoveryClassificationEnum.INSPIRATION
    assert meta is None


# ==============================================================================
# 3. ASYNC DISCOVERY ORCHESTRATION
# ==============================================================================

@pytest.mark.asyncio
async def test_orchestrate_discovery_async_all_sources_succeed(service, mock_common_results):
    """
    Tests async orchestration when all configured sources succeed.
    Verifies concurrent execution, tab interleaving, and overall SUCCESS status.
    """
    with patch("app.services.pinterest_service.search_pinterest_page", return_value=mock_common_results["pin"]), \
         patch("app.services.socialcrawl_service.search_instagram_reels", return_value=mock_common_results["ig"]), \
         patch("app.services.socialcrawl_service.search_youtube", return_value=mock_common_results["yt"]), \
         patch("app.services.socialcrawl_service.search_reddit", return_value=mock_common_results["red"]), \
         patch("app.services.socialcrawl_service.search_google_shopping", return_value=mock_common_results["shop"]), \
         patch("app.services.google_places_service.GooglePlacesService.search_nearby_suppliers", new_callable=AsyncMock) as mock_places:

        mock_places.return_value = mock_common_results["places"]

        resp = await service.orchestrate_discovery_async(
            query="Staircase",
            sources=["pinterest", "instagram", "youtube", "reddit", "google_shopping", "google_places"],
            dry_run=False
        )

        assert resp.overall_status == DiscoveryOverallStatusEnum.SUCCESS
        assert resp.total_results == 6
        assert len(resp.results) == 6
        # Confirm YouTube item is UNVERIFIED in async path
        yt_item = next(r for r in resp.results if r.source == "youtube")
        assert yt_item.verification_status == "UNVERIFIED"
        # Confirm Places item is POTENTIAL_GOOGLE_PLACE
        pl_item = next(r for r in resp.results if r.source == "google_places")
        assert pl_item.verification_status == "POTENTIAL_GOOGLE_PLACE"


@pytest.mark.asyncio
async def test_orchestrate_discovery_async_one_source_fails(service, mock_common_results):
    """
    Tests fault isolation in async orchestrator:
    When one source raises an exception, other sources succeed and PARTIAL_SUCCESS is returned.
    """
    with patch("app.services.pinterest_service.search_pinterest_page", return_value=mock_common_results["pin"]), \
         patch("app.services.socialcrawl_service.search_instagram_reels", side_effect=RuntimeError("Instagram Upstream 503")), \
         patch("app.services.socialcrawl_service.search_youtube", return_value=mock_common_results["yt"]), \
         patch("app.services.socialcrawl_service.search_reddit", return_value=mock_common_results["red"]), \
         patch("app.services.socialcrawl_service.search_google_shopping", return_value=mock_common_results["shop"]), \
         patch("app.services.google_places_service.GooglePlacesService.search_nearby_suppliers", new_callable=AsyncMock) as mock_places:

        mock_places.return_value = mock_common_results["places"]

        resp = await service.orchestrate_discovery_async(
            query="Staircase",
            sources=["pinterest", "instagram", "youtube", "reddit", "google_shopping", "google_places"],
            dry_run=False
        )

        assert resp.overall_status == DiscoveryOverallStatusEnum.PARTIAL_SUCCESS
        assert resp.source_statuses["instagram"].status == SourceStatusEnum.FAILED
        assert "instagram" in [e["source"] for e in resp.errors]
        assert resp.source_statuses["pinterest"].status == SourceStatusEnum.SUCCESS
        assert resp.source_statuses["youtube"].status == SourceStatusEnum.SUCCESS


@pytest.mark.asyncio
async def test_google_places_native_fetch_async(mock_common_results):
    """
    Verifies that GooglePlacesAdapter.fetch_async natively awaits the async
    GooglePlacesService without ThreadPoolExecutor or event loop nesting.
    """
    adapter = GooglePlacesAdapter()
    with patch.object(adapter, "is_configured", return_value=True), \
         patch("app.services.google_places_service.GooglePlacesService.search_nearby_suppliers", new_callable=AsyncMock) as mock_search:

        mock_search.return_value = mock_common_results["places"]

        items, status, metrics = await adapter.fetch_async("Staircase")

        assert status.status == SourceStatusEnum.SUCCESS
        assert len(items) == 1
        assert items[0].source == "google_places"
        assert items[0].verification_status == "POTENTIAL_GOOGLE_PLACE"
        mock_search.assert_awaited_once()


@pytest.mark.asyncio
async def test_orchestrate_discovery_async_timeout_handling(service, mock_common_results):
    """
    Verifies per-source timeout handling:
    An adapter exceeding source_timeout is terminated cleanly, marked FAILED with
    SOURCE_TIMEOUT, and does not block the search response.
    """
    async def slow_fetch(*args, **kwargs):
        await asyncio.sleep(0.5)
        return [], SourceStatusReport(source_name="slow", status=SourceStatusEnum.SUCCESS), SourceExecutionMetrics(source_name="slow")

    with patch("app.services.pinterest_service.search_pinterest_page", return_value=mock_common_results["pin"]), \
         patch.object(service.adapters["instagram"], "fetch_async", side_effect=slow_fetch):

        t0 = time.time()
        resp = await service.orchestrate_discovery_async(
            query="Staircase",
            sources=["pinterest", "instagram"],
            source_timeout=0.08  # Strict 80ms timeout
        )
        elapsed = time.time() - t0

        # Should finish well under 0.5s
        assert elapsed < 0.4
        assert resp.source_statuses["instagram"].status == SourceStatusEnum.FAILED
        assert resp.source_statuses["instagram"].error_code == "SOURCE_TIMEOUT"
        assert resp.source_statuses["pinterest"].status == SourceStatusEnum.SUCCESS


@pytest.mark.asyncio
async def test_orchestrate_discovery_async_concurrency_bounding(service):
    """
    Verifies that asyncio.Semaphore(max_concurrency) strictly bounds simultaneous tasks.
    """
    concurrent_calls = 0
    max_observed_concurrency = 0

    async def counted_fetch(*args, **kwargs):
        nonlocal concurrent_calls, max_observed_concurrency
        concurrent_calls += 1
        max_observed_concurrency = max(max_observed_concurrency, concurrent_calls)
        await asyncio.sleep(0.05)
        concurrent_calls -= 1
        return [], SourceStatusReport(source_name="test", status=SourceStatusEnum.SUCCESS), SourceExecutionMetrics(source_name="test")

    with patch.object(service.adapters["pinterest"], "fetch_async", side_effect=counted_fetch), \
         patch.object(service.adapters["instagram"], "fetch_async", side_effect=counted_fetch), \
         patch.object(service.adapters["youtube"], "fetch_async", side_effect=counted_fetch), \
         patch.object(service.adapters["reddit"], "fetch_async", side_effect=counted_fetch), \
         patch.object(service.adapters["google_shopping"], "fetch_async", side_effect=counted_fetch):

        await service.orchestrate_discovery_async(
            query="Staircase",
            sources=["pinterest", "instagram", "youtube", "reddit", "google_shopping"],
            max_concurrency=2
        )

        assert max_observed_concurrency <= 2


@pytest.mark.asyncio
async def test_sync_and_async_parity(service, mock_common_results):
    """
    Verifies that synchronous and asynchronous orchestration produce identical
    normalized schemas, field mappings, and tab routing.
    """
    with patch("app.services.pinterest_service.search_pinterest_page", return_value=mock_common_results["pin"]), \
         patch("app.services.socialcrawl_service.search_instagram_reels", return_value=mock_common_results["ig"]), \
         patch("app.services.socialcrawl_service.search_youtube", return_value=mock_common_results["yt"]), \
         patch("app.services.socialcrawl_service.search_reddit", return_value=mock_common_results["red"]), \
         patch("app.services.socialcrawl_service.search_google_shopping", return_value=mock_common_results["shop"]), \
         patch("app.services.google_places_service.GooglePlacesService.search_nearby_suppliers", new_callable=AsyncMock) as mock_places:

        mock_places.return_value = mock_common_results["places"]

        sources = ["pinterest", "instagram", "youtube", "reddit", "google_shopping", "google_places"]
        sync_resp = service.orchestrate_discovery("Staircase", sources=sources)
        async_resp = await service.orchestrate_discovery_async("Staircase", sources=sources)

        assert sync_resp.overall_status == async_resp.overall_status
        assert sync_resp.total_results == async_resp.total_results
        assert len(sync_resp.results) == len(async_resp.results)
        assert [r.source for r in sync_resp.results] == [r.source for r in async_resp.results]


# ==============================================================================
# 4. INTERACTIVE REQUEST SAFETY & BUDGET ENFORCEMENT
# ==============================================================================

def test_authenticated_user_rate_limit(fresh_guard):
    """
    Authenticated user limit: 60 requests per window.
    Request 61 must be blocked with status_code=429.
    """
    user_id = "test_architect_99"
    # Execute 60 permitted requests
    for i in range(60):
        decision = fresh_guard.check_request(user_id=user_id, is_authenticated=True)
        assert decision.allowed is True
        assert decision.status_code == 200

    # Request 61 must be rejected
    blocked = fresh_guard.check_request(user_id=user_id, is_authenticated=True)
    assert blocked.allowed is False
    assert blocked.status_code == 429
    assert blocked.retry_after_seconds is not None
    assert blocked.retry_after_seconds > 0


def test_anonymous_client_rate_limit(fresh_guard):
    """
    Anonymous client limit: 15 requests per window.
    Request 16 must be blocked with status_code=429.
    """
    client_ip = "192.168.1.100"
    for i in range(15):
        decision = fresh_guard.check_request(client_ip=client_ip, is_authenticated=False)
        assert decision.allowed is True

    blocked = fresh_guard.check_request(client_ip=client_ip, is_authenticated=False)
    assert blocked.allowed is False
    assert blocked.status_code == 429
    assert blocked.remaining_quota == 0


def test_anonymous_ip_salted_hashing(fresh_guard):
    """
    Privacy & Security Invariant:
    Raw IP addresses are never exposed or stored in history keys.
    Must produce salted SHA-256 identifier starting with 'anon_'.
    """
    raw_ip = "203.0.113.195"
    key, is_auth = fresh_guard.derive_client_identifier(client_ip=raw_ip, is_authenticated=False)
    assert is_auth is False
    assert key.startswith("anon_")
    assert raw_ip not in key
    assert len(key) == 5 + 16  # 'anon_' + 16-hex chars


def test_untrusted_client_headers_protection(fresh_guard):
    """
    Untrusted Client Invariant:
    - User passing client_supplied user_id without verified authentication is treated as anonymous.
    - Multi-hop IP headers (e.g. '198.51.100.1, 10.0.0.1') only use the leftmost client IP.
    """
    # 1. Unverified user_id
    key1, is_auth1 = fresh_guard.derive_client_identifier(
        user_id="spoofed_admin_id",
        client_ip="198.51.100.1",
        is_authenticated=False
    )
    assert is_auth1 is False
    assert key1.startswith("anon_")

    # 2. Multi-hop IP
    key2, _ = fresh_guard.derive_client_identifier(
        client_ip="198.51.100.1, 10.0.0.1, 172.16.0.1",
        is_authenticated=False
    )
    assert key1 == key2  # Leftmost hop is identical


def test_provider_budget_manager_source_cap(fresh_budget):
    """
    Enforces maximum sources per request (default: 7).
    """
    too_many_sources = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"]
    allowed, reason, proj = fresh_budget.check_budget(too_many_sources)
    assert allowed is False
    assert "exceeding maximum limit" in reason


def test_provider_budget_manager_credit_cap(fresh_budget):
    """
    Enforces maximum projected credits per request (default: 20).
    5 shopping queries = 25 credits > 20 cap.
    """
    heavy_sources = ["google_shopping"] * 5
    allowed, reason, proj = fresh_budget.check_budget(heavy_sources)
    assert allowed is False
    assert proj > fresh_budget.max_credits_per_request
    assert "exceeds max per-request limit" in reason


@pytest.mark.asyncio
async def test_pre_execution_blocking_burns_zero_credits(service):
    """
    Critical Invariant:
    When a request is rejected by rate limit or budget manager,
    ZERO provider adapters are executed, and ZERO provider credits are consumed.
    """
    discovery_request_guard.reset()
    provider_budget_manager.reset()

    # Fill anonymous quota (15 requests)
    for _ in range(15):
        discovery_request_guard.check_request(client_ip="10.20.30.40", is_authenticated=False)

    with patch.object(service.adapters["pinterest"], "fetch_async") as mock_pin_fetch:
        # Request 16 with enforce_guard=True
        resp = await service.orchestrate_discovery_async(
            query="Staircase",
            sources=["pinterest"],
            client_ip="10.20.30.40",
            is_authenticated=False,
            enforce_guard=True
        )

        assert resp.overall_status == DiscoveryOverallStatusEnum.RATE_LIMITED
        assert len(resp.results) == 0
        assert resp.errors[0]["guard"] == "rate_limit"
        # Invariant: Adapter was never called!
        mock_pin_fetch.assert_not_called()
        # Invariant: Zero credits consumed!
        assert provider_budget_manager._daily_credits_used == 0

    discovery_request_guard.reset()
    provider_budget_manager.reset()


# ==============================================================================
# 5. SECURITY, PROXY VALIDATION, AUTH & CONCURRENCY HARDENING TESTS (STAGE 2.1 FINAL)
# ==============================================================================

def _make_asgi_request(peer_host: str, headers: dict = None) -> Request:
    raw_headers = [
        (k.lower().encode("latin-1"), v.encode("latin-1"))
        for k, v in (headers or {}).items()
    ]
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/discovery/search",
        "headers": raw_headers,
        "client": (peer_host, 54321),
    }
    return Request(scope)


def test_forged_xff_ignored_from_untrusted_peer():
    """
    Security Test 1:
    A client connecting directly (or via untrusted peer) cannot spoof X-Forwarded-For.
    Even when TRUSTED_PROXIES is configured for another network, untrusted peers' XFF is ignored.
    """
    req = _make_asgi_request(
        peer_host="198.51.100.77",
        headers={"X-Forwarded-For": "203.0.113.5, 198.51.100.1"}
    )
    # Default empty trusted proxies
    assert extract_verified_client_ip(req, trusted_proxies=[]) == "198.51.100.77"
    # Non-matching trusted proxy range
    assert extract_verified_client_ip(req, trusted_proxies=["10.0.0.0/8"]) == "198.51.100.77"


def test_valid_xff_accepted_from_trusted_proxy_cidr():
    """
    Security Test 2:
    When peer matches configured TRUSTED_PROXIES CIDR/IP, X-Forwarded-For is parsed
    right-to-left skipping trusted proxy hops and extracting the origin client IP.
    """
    req = _make_asgi_request(
        peer_host="10.10.1.5",
        headers={"X-Forwarded-For": "203.0.113.88, 10.10.2.9"}
    )
    verified_ip = extract_verified_client_ip(req, trusted_proxies=["10.0.0.0/8"])
    assert verified_ip == "203.0.113.88"


def test_malformed_xff_falls_back_safely_to_peer_ip():
    """
    Security Test 3:
    Malformed X-Forwarded-For values from a trusted peer must be rejected safely
    and fall back to the verified immediate peer address.
    """
    req_garbage = _make_asgi_request(
        peer_host="10.10.1.5",
        headers={"X-Forwarded-For": "not-an-ip, 10.10.2.9"}
    )
    assert extract_verified_client_ip(req_garbage, trusted_proxies=["10.0.0.0/8"]) == "10.10.1.5"

    req_empty_hop = _make_asgi_request(
        peer_host="10.10.1.5",
        headers={"X-Forwarded-For": "203.0.113.88, "}
    )
    assert extract_verified_client_ip(req_empty_hop, trusted_proxies=["10.0.0.0/8"]) == "10.10.1.5"


def test_get_optional_current_user_strict_no_demo_fallback():
    """
    Security Test 4:
    Missing, malformed, or expired JWTs resolve strictly to None (anonymous),
    NEVER falling back to architect@studio.com even when present in DB.
    Valid tokens resolve the corresponding real User.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()
    try:
        demo_user = User(email="architect@studio.com", hashed_password="x", role="architect")
        real_user = User(email="real.architect@example.com", hashed_password="x", role="architect")
        db.add_all([demo_user, real_user])
        db.commit()
        db.refresh(real_user)

        # Missing token -> None (must NOT return demo_user)
        assert get_optional_current_user(token=None, db=db) is None
        # Garbage/invalid token -> None
        assert get_optional_current_user(token="invalid.jwt.token", db=db) is None
        # Expired token -> None
        expired_tok = create_access_token(
            subject="real.architect@example.com",
            role="architect",
            expires_delta=timedelta(minutes=-5)
        )
        assert get_optional_current_user(token=expired_tok, db=db) is None
        # Valid token -> returns real_user
        valid_tok = create_access_token(
            subject="real.architect@example.com",
            role="architect",
            expires_delta=timedelta(minutes=15)
        )
        resolved = get_optional_current_user(token=valid_tok, db=db)
        assert resolved is not None
        assert resolved.email == "real.architect@example.com"
    finally:
        db.close()
        engine.dispose()


def test_arbitrary_x_user_id_header_cannot_impersonate_authenticated_tier(fresh_guard):
    """
    Security Test 5:
    Sending X-User-Id or X-Authenticated headers without a verified user object
    cannot elevate anonymous requests to the authenticated 60/hr quota.
    """
    req = _make_asgi_request(
        peer_host="198.51.100.44",
        headers={"X-User-Id": "admin_user_1", "X-Authenticated": "true"}
    )
    # 15 requests allowed under anonymous tier; 16th blocked regardless of X-User-Id
    for _ in range(15):
        dec = fresh_guard.check_http_request(req, current_user=None)
        assert dec.allowed is True
        assert dec.client_identifier.startswith("anon_")

    blocked = fresh_guard.check_http_request(req, current_user=None)
    assert blocked.allowed is False
    assert blocked.status_code == 429


@pytest.mark.asyncio
async def test_concurrent_budget_race_prevents_overspending(service):
    """
    Concurrency Test 6:
    Simultaneous async discovery requests racing for the final credits in the daily budget
    must enforce the cap atomically without overspending or executing excess adapters.
    """
    discovery_request_guard.reset()
    provider_budget_manager.reset()
    provider_budget_manager._daily_credits_used = provider_budget_manager.daily_interactive_credit_cap - 2  # 2 credits left

    async def fake_fetch_async(*args, **kwargs):
        await asyncio.sleep(0.01)
        return (
            [],
            SourceStatusReport(source_name="pinterest", status=SourceStatusEnum.EMPTY, requested=True, duration_ms=10.0),
            SourceExecutionMetrics(source_name="pinterest", requested_result_count=15, status=SourceStatusEnum.EMPTY, duration_ms=10.0),
        )

    try:
        with patch.object(service.adapters["pinterest"], "fetch_async", side_effect=fake_fetch_async) as mock_pin:
            responses = await asyncio.gather(*[
                service.orchestrate_discovery_async(
                    query="Terracotta facade",
                    sources=["pinterest"],
                    client_ip=f"198.51.100.{10 + i}",
                    enforce_guard=True,
                )
                for i in range(5)
            ])

        allowed_resps = [r for r in responses if r.overall_status != DiscoveryOverallStatusEnum.FAILED]
        blocked_resps = [
            r for r in responses
            if r.overall_status == DiscoveryOverallStatusEnum.FAILED
            and any(e.get("guard") == "budget_exceeded" for e in r.errors)
        ]
        assert len(allowed_resps) == 2
        assert len(blocked_resps) == 3
        assert mock_pin.call_count == 2
        assert provider_budget_manager._daily_credits_used == provider_budget_manager.daily_interactive_credit_cap
    finally:
        discovery_request_guard.reset()
        provider_budget_manager.reset()


def test_concurrent_rate_limit_race_atomic_enforcement(fresh_guard):
    """
    Concurrency Test 7:
    20 parallel threads hitting check_request for the same anonymous IP (limit=15)
    must allow strictly 15 and block strictly 5 with status 429.
    """
    def hit_once(_idx):
        return fresh_guard.check_request(client_ip="203.0.113.77", is_authenticated=False)

    with ThreadPoolExecutor(max_workers=10) as pool:
        decisions = list(pool.map(hit_once, range(20)))

    allowed = [d for d in decisions if d.allowed]
    blocked = [d for d in decisions if not d.allowed]
    assert len(allowed) == 15
    assert len(blocked) == 5
    assert all(d.status_code == 429 for d in blocked)


@pytest.mark.asyncio
async def test_pagination_depth_limit_enforced_pre_execution(service):
    """
    Safety Test 8:
    Requesting page > max_pagination_depth (e.g. page=3 > 2) or page < 1
    is rejected pre-execution with zero adapter invocations and zero credit burn.
    """
    discovery_request_guard.reset()
    provider_budget_manager.reset()

    try:
        with patch.object(service.adapters["pinterest"], "fetch_async") as mock_pin:
            resp = await service.orchestrate_discovery_async(
                query="Brickwork",
                sources=["pinterest"],
                page=3,
                client_ip="198.51.100.90",
                enforce_guard=True,
            )
            assert resp.overall_status == DiscoveryOverallStatusEnum.FAILED
            assert resp.errors[0]["guard"] == "budget_exceeded"
            mock_pin.assert_not_called()
            assert provider_budget_manager._daily_credits_used == 0

            resp_zero = await service.orchestrate_discovery_async(
                query="Brickwork",
                sources=["pinterest"],
                page=0,
                client_ip="198.51.100.91",
                enforce_guard=True,
            )
            assert resp_zero.overall_status == DiscoveryOverallStatusEnum.FAILED
            assert resp_zero.errors[0]["guard"] == "budget_exceeded"
            mock_pin.assert_not_called()
            assert provider_budget_manager._daily_credits_used == 0
    finally:
        discovery_request_guard.reset()
        provider_budget_manager.reset()


@pytest.mark.asyncio
async def test_query_expansion_limit_enforced_pre_execution(service):
    """
    Safety Test 9:
    Requesting query_expansions > max_expansions_per_source (4 > 3)
    is rejected pre-execution with zero adapter invocations and zero credit burn.
    """
    discovery_request_guard.reset()
    provider_budget_manager.reset()

    try:
        with patch.object(service.adapters["pinterest"], "fetch_async") as mock_pin:
            resp = await service.orchestrate_discovery_async(
                query="Staircase",
                sources=["pinterest"],
                query_expansions=4,
                client_ip="198.51.100.92",
                enforce_guard=True,
            )
            assert resp.overall_status == DiscoveryOverallStatusEnum.FAILED
            assert resp.errors[0]["guard"] == "budget_exceeded"
            mock_pin.assert_not_called()
            assert provider_budget_manager._daily_credits_used == 0
    finally:
        discovery_request_guard.reset()
        provider_budget_manager.reset()


@pytest.mark.asyncio
async def test_explicit_task_cancel_propagates_and_cancels_children(service):
    """
    Async Cancellation Test 10:
    Cancelling an active orchestrate_discovery_async task mid-flight propagates CancelledError
    and cancels in-flight sibling adapter tasks cleanly.
    """
    started = asyncio.Event()
    cancelled_sources = []

    async def slow_adapter(source_name: str):
        async def _inner(*args, **kwargs):
            started.set()
            try:
                await asyncio.sleep(5.0)
            except asyncio.CancelledError:
                cancelled_sources.append(source_name)
                raise
        return _inner

    pin_fn = await slow_adapter("pinterest")
    yt_fn = await slow_adapter("youtube")

    with patch.object(service.adapters["pinterest"], "fetch_async", side_effect=pin_fn), \
         patch.object(service.adapters["youtube"], "fetch_async", side_effect=yt_fn):
        task = asyncio.create_task(
            service.orchestrate_discovery_async(
                query="Timber roof",
                sources=["pinterest", "youtube"],
            )
        )
        await started.wait()
        await asyncio.sleep(0.01)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    assert set(cancelled_sources) == {"pinterest", "youtube"}


def test_stale_client_key_eviction_over_500_clients():
    """
    Memory Hygiene Test 11:
    When more than 500 tracked clients accumulate with expired sliding-window timestamps,
    DiscoveryRequestGuard evicts stale keys while retaining active clients.
    """
    guard = DiscoveryRequestGuard(anon_rate_limit=15, window_seconds=60, salt="evict_salt")
    now = time.time()
    expired_ts = now - 120.0

    # Seed 520 stale entries
    for idx in range(520):
        octet3 = idx // 250
        octet4 = (idx % 250) + 1
        key, _ = guard.derive_client_identifier(client_ip=f"192.0.{octet3}.{octet4}", is_authenticated=False)
        from collections import deque
        guard._request_history[key] = deque([expired_ts])

    assert len(guard._request_history) == 520

    # Trigger check for an active client -> triggers eviction because len > 500
    dec = guard.check_request(client_ip="203.0.113.200", is_authenticated=False)
    assert dec.allowed is True
    assert len(guard._request_history) == 1
    assert dec.client_identifier in guard._request_history


@pytest.mark.asyncio
async def test_billing_semantics_dry_run_disabled_and_failed_calls(service):
    """
    Budget Billing Test 12:
    - dry_run=True consumes 0 credits.
    - Disabled source ('x') consumes 0 credits.
    - Executed provider call that fails/errors retains conservative credit debit (1 credit for pinterest),
      because failed upstream requests may still be billed by providers.
    """
    discovery_request_guard.reset()
    provider_budget_manager.reset()

    try:
        async def dry_fetch(*args, **kwargs):
            return (
                [],
                SourceStatusReport(source_name="pinterest", status=SourceStatusEnum.EMPTY, requested=True),
                SourceExecutionMetrics(source_name="pinterest", requested_result_count=15, status=SourceStatusEnum.EMPTY),
            )

        # 1. dry_run=True -> 0 credits
        with patch.object(service.adapters["pinterest"], "fetch_async", side_effect=dry_fetch):
            resp_dry = await service.orchestrate_discovery_async(
                query="Stone cladding",
                sources=["pinterest"],
                dry_run=True,
                client_ip="198.51.100.1",
                enforce_guard=True,
            )
        assert resp_dry.overall_status == DiscoveryOverallStatusEnum.EMPTY
        assert provider_budget_manager._daily_credits_used == 0

        # 2. Disabled source ('x') -> 0 credits
        resp_disabled = await service.orchestrate_discovery_async(
            query="Stone cladding",
            sources=["x"],
            dry_run=False,
            client_ip="198.51.100.2",
            enforce_guard=True,
        )
        assert resp_disabled.source_statuses["x"].status == SourceStatusEnum.DISABLED
        assert provider_budget_manager._daily_credits_used == 0

        # 3. Executed source that fails upstream -> keeps conservative credit debit (1)
        async def failing_fetch(*args, **kwargs):
            return (
                [],
                SourceStatusReport(source_name="pinterest", status=SourceStatusEnum.FAILED, requested=True, error_code="UPSTREAM_502"),
                SourceExecutionMetrics(source_name="pinterest", requested_result_count=15, status=SourceStatusEnum.FAILED, error_code="UPSTREAM_502"),
            )

        with patch.object(service.adapters["pinterest"], "fetch_async", side_effect=failing_fetch):
            resp_fail = await service.orchestrate_discovery_async(
                query="Stone cladding",
                sources=["pinterest"],
                dry_run=False,
                client_ip="198.51.100.3",
                enforce_guard=True,
            )
            assert resp_fail.overall_status == DiscoveryOverallStatusEnum.FAILED
            assert provider_budget_manager._daily_credits_used == 1
    finally:
        discovery_request_guard.reset()
        provider_budget_manager.reset()


def test_provider_budget_daily_window_reset(fresh_budget):
    """
    Budget Window Test 13:
    Daily credit usage resets to 0 once 86400 seconds elapse.
    """
    ok, _, proj = fresh_budget.check_budget(["google_shopping"], reserve=True)
    assert ok is True
    assert proj == 5
    assert fresh_budget._daily_credits_used == 5

    # Simulate 25 hours elapsed
    fresh_budget._daily_reset_timestamp -= 90000
    status_info = fresh_budget.get_status()
    assert status_info["daily_credits_used"] == 0
    assert status_info["daily_credits_remaining"] == fresh_budget.daily_interactive_credit_cap


def test_sync_orchestration_no_double_credit_charging(service):
    """
    Parity & Atomic Accounting Test 14:
    Sync orchestrate_discovery(..., enforce_guard=True) charges projected credits once (via atomic
    pre-execution reservation) and does not double-charge post-execution.
    """
    discovery_request_guard.reset()
    provider_budget_manager.reset()

    try:
        with patch.object(
            service.adapters["pinterest"],
            "fetch",
            return_value=(
                [],
                SourceStatusReport(source_name="pinterest", status=SourceStatusEnum.EMPTY, requested=True),
                SourceExecutionMetrics(source_name="pinterest", requested_result_count=15, status=SourceStatusEnum.EMPTY),
            ),
        ):
            service.orchestrate_discovery(
                query="Pergola wood",
                sources=["pinterest"],
                client_ip="198.51.100.120",
                enforce_guard=True,
            )
            assert provider_budget_manager._daily_credits_used == 1
    finally:
        discovery_request_guard.reset()
        provider_budget_manager.reset()


def test_get_current_user_strict_401_and_public_routes_anonymous(client, user_headers, admin_headers):
    """
    Phase 1 Security Test 15:
    - Protected endpoints MUST return 401 when no valid bearer token is supplied (no demo user fallback).
    - Admin endpoints MUST return 401 without token and 403 for non-admin users.
    - Public discovery endpoints remain accessible to anonymous users (200).
    - Public registration cannot elevate role to 'admin'.
    """
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/saved").status_code == 401
    assert client.get("/api/saved/counts").status_code == 401
    assert client.get("/api/quotations").status_code == 401
    assert client.get("/api/admin/stats").status_code == 401
    assert client.get("/api/admin/quality-audit").status_code == 401

    assert client.get("/api/auth/me", headers=user_headers).status_code == 200
    assert client.get("/api/admin/stats", headers=user_headers).status_code == 403
    assert client.get("/api/admin/stats", headers=admin_headers).status_code == 200

    # Public discovery stays anonymous-friendly
    assert client.get("/api/feed?page_size=2").status_code == 200
    assert client.get("/api/categories").status_code == 200
    assert client.get("/api/suppliers").status_code == 200

    # Privilege escalation prevention on /register
    reg = client.post("/api/auth/register", json={
        "email": "attacker_role_test@example.com",
        "password": "Password123!",
        "full_name": "Test User",
        "role": "admin",
    })
    assert reg.status_code == 200
    assert reg.json()["user"]["role"] == "user"


def test_provider_budget_cached_request_zero_credits(fresh_budget):
    """
    Phase 1 Budget Test 16:
    Cached hits and dry runs charge 0 credits even with reserve=True, while live execution reserves credits.
    """
    # Cached hit -> 0 credits
    ok_cached, _, proj_cached = fresh_budget.check_budget(
        ["pinterest", "instagram", "google_shopping"],
        cached=True,
        reserve=True,
    )
    assert ok_cached is True
    assert proj_cached == 0
    assert fresh_budget._daily_credits_used == 0

    # Dry run -> 0 credits
    ok_dry, _, proj_dry = fresh_budget.check_budget(
        ["google_shopping"],
        dry_run=True,
        reserve=True,
    )
    assert ok_dry is True
    assert proj_dry == 0
    assert fresh_budget._daily_credits_used == 0

    # Live call -> reserves 1 (pinterest) + 5 (google_shopping) = 6
    ok_live, _, proj_live = fresh_budget.check_budget(
        ["pinterest", "google_shopping"],
        cached=False,
        dry_run=False,
        reserve=True,
    )
    assert ok_live is True
    assert proj_live == 6
    assert fresh_budget._daily_credits_used == 6

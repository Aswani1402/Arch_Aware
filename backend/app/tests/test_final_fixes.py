"""
Nivora — Approved Final Fixes Regression Test Suite
Covers:
1. GoogleShoppingAdapter query cleanup, seller extraction & nested product handling
2. Authenticated vs unauthenticated /api/saved & real verification_status propagation
3. Multi-source YouTube non-dominance & Google Search NOT_CONFIGURED partial-success isolation
4. Render SQLite persistent disk safe one-time copy helper (never overwrites existing DB)
5. Frontend auth-guard & discovery-wiring static code contracts
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from app.core.database import _ensure_sqlite_persistent_target
from app.models.models import (
    ArchitecturalReference,
    Product,
    SavedItem,
    Supplier,
    User,
)
from app.schemas.discovery import (
    DiscoveryOverallStatusEnum,
    DiscoveryTabEnum,
    NormalizedDiscoveryResult,
    SourceStatusEnum,
    SourceStatusReport,
)
from app.core.security import create_access_token
from app.services.discovery_adapters import GooglePlacesAdapter, GoogleShoppingAdapter
from app.services.search_orchestration_service import SearchOrchestrationService


REPO_ROOT = Path(__file__).resolve().parents[3]


# ==============================================================================
# 1. GOOGLE SHOPPING ADAPTER REGRESSIONS
# ==============================================================================

def test_google_shopping_query_builder_and_country_region_passing():
    adapter = GoogleShoppingAdapter()
    queries = adapter.build_queries("TMT bars")
    assert any("TMT bars" in q for q in queries)
    for q in queries:
        assert "material specifications" not in q.lower()
        assert "hardware fittings" not in q.lower()

    captured = {}

    def fake_search(**kwargs):
        captured.update(kwargs)
        return {"items": []}

    with (
        patch.object(adapter, "is_configured", return_value=True),
        patch("app.services.socialcrawl_service.search_google_shopping", side_effect=fake_search),
    ):
        adapter.fetch("Athangudi tiles", taxonomy_context={"country": "in", "state": "Tamil Nadu"})

    assert "Athangudi tiles" in captured["query"]
    assert captured["country"] == "IN"


def test_google_shopping_fetch_extracts_seller_and_nested_product():
    adapter = GoogleShoppingAdapter()
    mock_payload = {
        "items": [
            {
                "product_id": "shp_1",
                "product": {
                    "title": "Fe 550D TMT Steel Bar 12mm",
                    "url": "https://shopping.example.com/item/1",
                    "image_urls": ["https://cdn.example.com/tmt.jpg"],
                    "price": {"current": 54000, "currency": "INR"},
                },
                "seller": "Sri Murugan Steels",
                "rating": {"average": 4.6, "count": 32},
            },
            {
                # Missing seller, image, and price -> kept cleanly without fabrication
                "id": "shp_2",
                "title": "Athangudi Terracotta Floor Tile 8x8",
                "url": "https://shopping.example.com/item/2",
            },
            {
                # Completely empty item with no title, url or id -> skipped safely
                "description": "Orphan entry",
            },
        ],
    }

    with (
        patch.object(adapter, "is_configured", return_value=True),
        patch("app.services.socialcrawl_service.search_google_shopping", return_value=mock_payload),
    ):
        results, status_report, _metrics = adapter.fetch("TMT bars", limit=20)

    assert status_report.status == SourceStatusEnum.SUCCESS
    assert len(results) == 2

    first = results[0]
    assert first.title == "Fe 550D TMT Steel Bar 12mm"
    assert first.creator_name == "Sri Murugan Steels"
    assert first.price == 54000.0
    assert first.currency == "INR"
    assert first.original_url == "https://shopping.example.com/item/1"
    assert first.image_url == "https://cdn.example.com/tmt.jpg"
    assert first.source_result_id == "shp_1"
    assert first.source_attribution == "Google Shopping (Sri Murugan Steels)"
    assert first.verification_status == "UNVERIFIED"
    assert first.source_metadata["country"] == "IN"

    second = results[1]
    assert second.title == "Athangudi Terracotta Floor Tile 8x8"
    assert second.creator_name is None
    assert second.price is None
    assert second.currency is None
    assert second.image_url is None
    assert second.thumbnail_url is None


def test_google_shopping_handles_empty_invalid_and_error_responses():
    adapter = GoogleShoppingAdapter()

    with patch.object(adapter, "is_configured", return_value=True):
        # Empty response
        with patch("app.services.socialcrawl_service.search_google_shopping", return_value={"items": []}):
            res, rep, _ = adapter.fetch("laterite block")
        assert res == []
        assert rep.status == SourceStatusEnum.EMPTY

        # Invalid malformed response shape
        with patch("app.services.socialcrawl_service.search_google_shopping", return_value=["not-a-dict"]):
            res, rep, _ = adapter.fetch("laterite block")
        assert res == []
        assert rep.status == SourceStatusEnum.FAILED
        assert rep.error_code == "MALFORMED_UPSTREAM_RESPONSE"

        # Upstream error payload
        with patch("app.services.socialcrawl_service.search_google_shopping", return_value={"error": "Upstream quota exceeded"}):
            res, rep, _ = adapter.fetch("laterite block")
        assert res == []
        assert rep.status in (SourceStatusEnum.FAILED, SourceStatusEnum.QUOTA_EXHAUSTED)

        with patch("app.services.socialcrawl_service.search_google_shopping", return_value={"error": "Upstream gateway error"}):
            res, rep, _ = adapter.fetch("laterite block")
        assert res == []
        assert rep.status == SourceStatusEnum.FAILED

        # Raised network exception
        with patch("app.services.socialcrawl_service.search_google_shopping", side_effect=RuntimeError("Upstream connection failure")):
            res, rep, _ = adapter.fetch("laterite block")
        assert res == []
        assert rep.status == SourceStatusEnum.FAILED


# ==============================================================================
# 2. /api/saved & /api/quotations AUTH & REAL VERIFICATION STATUS
# ==============================================================================

def test_private_endpoints_reject_unauthenticated_and_expired_jwt(client):
    assert client.get("/api/saved").status_code == 401
    assert client.get("/api/saved/counts").status_code == 401
    assert client.post("/api/saved/toggle", json={"item_type": "reference", "reference_id": 1}).status_code == 401
    assert client.get("/api/quotations").status_code == 401

    from datetime import timedelta
    expired = create_access_token({"sub": "architect@studio.com"}, expires_delta=timedelta(minutes=-5))
    expired_headers = {"Authorization": f"Bearer {expired}"}
    assert client.get("/api/saved", headers=expired_headers).status_code == 401
    assert client.get("/api/quotations", headers=expired_headers).status_code == 401


def test_saved_endpoint_preserves_all_verification_statuses(client, db, user_headers):
    user = db.query(User).filter(User.email == "architect@studio.com").first()
    if not user:
        user = db.query(User).first()
    assert user is not None

    ref_unverified = ArchitecturalReference(
        title="Unverified Courtyard Pavilion",
        slug="unverified-courtyard-pavilion-test",
        source_platform="youtube",
        source_url="https://youtube.com/watch?v=test_unverified",
        verification_status="UNVERIFIED",
        content_type="architectural_project",
    )
    prod_verified = Product(
        name="Verified Italian Calacatta Slab",
        slug="verified-calacatta-slab-test",
        verification_status="VERIFIED",
    )
    sup_potential = Supplier(
        name="Potential Local Depot",
        slug="potential-local-depot-test",
        address="MG Road, Chennai",
        city="Chennai",
        state="Tamil Nadu",
        verification_status="POTENTIAL",
    )
    sup_unknown = Supplier(
        name="Unknown Status Trader",
        slug="unknown-status-trader-test",
        address="Race Course Road, Coimbatore",
        city="Coimbatore",
        state="Tamil Nadu",
        verification_status="UNKNOWN",
    )
    sup_missing = Supplier(
        name="Missing Status Stockist",
        slug="missing-status-stockist-test",
        address="Anna Salai, Madurai",
        city="Madurai",
        state="Tamil Nadu",
        verification_status=None,
    )
    db.add_all([ref_unverified, prod_verified, sup_potential, sup_unknown, sup_missing])
    db.flush()

    db.add_all([
        SavedItem(user_id=user.id, item_type="reference", reference_id=ref_unverified.id, project_collection="Test"),
        SavedItem(user_id=user.id, item_type="product", product_id=prod_verified.id, project_collection="Test"),
        SavedItem(user_id=user.id, item_type="supplier", supplier_id=sup_potential.id, project_collection="Test"),
        SavedItem(user_id=user.id, item_type="supplier", supplier_id=sup_unknown.id, project_collection="Test"),
        SavedItem(user_id=user.id, item_type="supplier", supplier_id=sup_missing.id, project_collection="Test"),
    ])
    db.commit()

    resp = client.get("/api/saved", headers=user_headers)
    assert resp.status_code == 200
    payload = resp.json()

    by_title = {}
    for entry in payload:
        data = entry.get("item_data") or {}
        label = data.get("title") or data.get("name")
        if label:
            by_title[label] = data

    assert by_title["Unverified Courtyard Pavilion"]["verification_status"] == "UNVERIFIED"
    assert by_title["Verified Italian Calacatta Slab"]["verification_status"] == "VERIFIED"
    assert by_title["Potential Local Depot"]["verification_status"] == "POTENTIAL"
    assert by_title["Unknown Status Trader"]["verification_status"] == "UNKNOWN"
    assert by_title["Missing Status Stockist"]["verification_status"] != "VERIFIED"


def test_google_places_potential_business_never_marked_verified():
    adapter = GooglePlacesAdapter()
    mock_places = {
        "places": [{
            "name": "Sri Lakshmi Marble Co",
            "address": "GST Road, Chennai",
            "google_place_id": "ChIJ_test_123",
            "google_maps_url": "https://maps.google.com/?cid=123",
            "verification_status": "VERIFIED",  # Even if raw dict hints otherwise, adapter forces POTENTIAL_GOOGLE_PLACE
        }]
    }
    with (
        patch.object(adapter, "is_configured", return_value=True),
        patch("app.services.google_places_service.GooglePlacesService.search_nearby_suppliers", return_value=mock_places),
    ):
        results, status_report, _ = adapter.fetch("marble", limit=5, taxonomy_context={"city": "Chennai"})

    assert status_report.status == SourceStatusEnum.SUCCESS
    assert len(results) == 1
    assert results[0].verification_status == "POTENTIAL_GOOGLE_PLACE"
    assert results[0].verification_status != "VERIFIED"


# ==============================================================================
# 3. YOUTUBE NON-DOMINANCE & PARTIAL PROVIDER ISOLATION
# ==============================================================================

def _make_norm_item(source: str, idx: int) -> NormalizedDiscoveryResult:
    return NormalizedDiscoveryResult(
        source=source,
        source_result_id=f"{source}_{idx}",
        original_url=f"https://example.com/{source}/{idx}",
        canonical_url=f"https://example.com/{source}/{idx}",
        title=f"{source.title()} Architectural Sample {idx}",
        verification_status="UNVERIFIED",
        content_type="youtube_walkthrough" if source == "youtube" else "architectural_project",
    )


def test_youtube_non_dominance_in_multi_source_assembly():
    service = SearchOrchestrationService()
    yt_items = [_make_norm_item("youtube", i) for i in range(20)]
    pin_items = [_make_norm_item("pinterest", i) for i in range(4)]
    shop_items = [_make_norm_item("google_shopping", i) for i in range(2)]

    per_source_items = {
        "youtube": yt_items,
        "pinterest": pin_items,
        "google_shopping": shop_items,
    }
    source_statuses = {
        src: SourceStatusReport(
            source_name=src,
            status=SourceStatusEnum.SUCCESS,
            requested=True,
            result_count=len(items),
            unique_result_count=len(items),
        )
        for src, items in per_source_items.items()
    }

    resp = service._assemble_discovery_response(
        clean_q="terracotta",
        norm_q="terracotta",
        active_tab=DiscoveryTabEnum.ALL,
        resolved_tax={},
        active_sources=["youtube", "pinterest", "google_shopping"],
        source_statuses=source_statuses,
        source_metrics={},
        source_buckets=per_source_items,
        pooled_results=yt_items + pin_items + shop_items,
        warnings=[],
        errors=[],
        page=1,
        page_size=28,
        req_id="req_test_yt_cap",
    )

    yt_returned = [r for r in resp.results if r.source == "youtube"]
    non_yt_returned = [r for r in resp.results if r.source != "youtube"]
    # 6 non-YouTube items -> cap is max(2, 6 // 2) = 3 YouTube items
    assert len(non_yt_returned) == 6
    assert len(yt_returned) <= 3


def test_partial_provider_not_configured_does_not_block_other_sources():
    service = SearchOrchestrationService()
    pin_items = [_make_norm_item("pinterest", i) for i in range(3)]
    source_statuses = {
        "pinterest": SourceStatusReport(
            source_name="pinterest",
            status=SourceStatusEnum.SUCCESS,
            requested=True,
            result_count=3,
            unique_result_count=3,
        ),
        "google_search": SourceStatusReport(
            source_name="google_search",
            status=SourceStatusEnum.NOT_CONFIGURED,
            requested=True,
            error_code="MISSING_CREDENTIALS",
            error_message="GOOGLE_CUSTOM_SEARCH_CX missing.",
        ),
    }

    resp = service._assemble_discovery_response(
        clean_q="laterite stone",
        norm_q="laterite stone",
        active_tab=DiscoveryTabEnum.ALL,
        resolved_tax={},
        active_sources=["pinterest", "google_search"],
        source_statuses=source_statuses,
        source_metrics={},
        source_buckets={"pinterest": pin_items, "google_search": []},
        pooled_results=pin_items,
        warnings=[],
        errors=[],
        page=1,
        page_size=28,
        req_id="req_test_partial",
    )

    assert resp.overall_status == DiscoveryOverallStatusEnum.PARTIAL_SUCCESS
    assert len(resp.results) == 3
    assert resp.source_statuses["google_search"].status == SourceStatusEnum.NOT_CONFIGURED


# ==============================================================================
# 4. RENDER SQLITE PERSISTENT TARGET SAFETY
# ==============================================================================

def test_ensure_sqlite_persistent_target_copies_once_without_overwrite(tmp_path):
    import sqlite3
    seed_db = tmp_path / "seed.db"
    sconn = sqlite3.connect(seed_db)
    sconn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, label TEXT)")
    sconn.execute("INSERT INTO items (label) VALUES ('seed_row')")
    sconn.commit()
    sconn.close()

    target_db = tmp_path / "persistent.db"
    target_url = f"sqlite:///{target_db}"

    _ensure_sqlite_persistent_target(target_url, seed_path=str(seed_db))
    assert target_db.exists()
    tconn = sqlite3.connect(target_db)
    rows = tconn.execute("SELECT label FROM items").fetchall()
    tconn.execute("INSERT INTO items (label) VALUES ('user_created')")
    tconn.commit()
    tconn.close()
    assert rows == [("seed_row",)]

    # Second call with existing valid DB MUST preserve user_created and never overwrite
    _ensure_sqlite_persistent_target(target_url, seed_path=str(seed_db))
    tconn = sqlite3.connect(target_db)
    rows_after = tconn.execute("SELECT label FROM items ORDER BY id").fetchall()
    tconn.close()
    assert rows_after == [("seed_row",), ("user_created",)]


def test_ensure_sqlite_persistent_target_rejects_partial_db_and_empty_prod_disk(tmp_path, monkeypatch):
    from app.core.config import Settings, settings

    # 1. Partial / truncated DB at target must fail validation and never be overwritten
    partial_db = tmp_path / "partial.db"
    partial_db.write_bytes(b"SQLite format 3\x00truncated_partial_copy")
    with pytest.raises(RuntimeError, match="invalid or partially copied"):
        _ensure_sqlite_persistent_target(f"sqlite:///{partial_db}")
    assert partial_db.read_bytes() == b"SQLite format 3\x00truncated_partial_copy"

    # 2. Production mode (DEMO_MODE=False) with missing target & missing seed must fail loudly
    missing_target = tmp_path / "prod_empty" / "architect_ai.db"
    missing_seed = tmp_path / "missing_seed.db"
    monkeypatch.setattr(settings, "DEMO_MODE", False)
    with pytest.raises(RuntimeError, match="Refusing to silently create an empty production database"):
        _ensure_sqlite_persistent_target(
            f"sqlite:///{missing_target}",
            seed_path=str(missing_seed),
            allow_empty_production=False,
        )
    assert not missing_target.exists()

    # 3. Comma-separated TRUSTED_PROXIES parses cleanly in Settings
    s = Settings(TRUSTED_PROXIES="10.0.0.1, 10.0.0.2")
    assert s.TRUSTED_PROXIES == ["10.0.0.1", "10.0.0.2"]


def test_google_shopping_seller_pipeline_does_not_fabricate_seller():
    from app.services.socialcrawl_service import normalize_google_shopping

    norm_missing = normalize_google_shopping({"product": {"id": "p1", "title": "Ceramic Sink", "brand": "Kohler"}})
    assert norm_missing["seller"] is None
    assert norm_missing["currency"] is None
    assert norm_missing["verification_status"] == "UNVERIFIED"

    adapter = GoogleShoppingAdapter()
    mock_payload = {
        "items": [
            {
                "id": "p_brand_only",
                "title": "Brass Wall Mixer",
                "brand": "Kohler",
                "url": "https://shopping.example.com/mixer",
                "price": {"current": 4500, "currency": "INR"},
            }
        ]
    }
    with (
        patch.object(adapter, "is_configured", return_value=True),
        patch("app.services.socialcrawl_service.search_google_shopping", return_value=mock_payload),
    ):
        results, status_report, _ = adapter.fetch("brass mixer")

    assert status_report.status == SourceStatusEnum.SUCCESS
    assert len(results) == 1
    assert results[0].creator_name is None
    assert results[0].source_metadata["seller"] is None
    assert results[0].source_metadata["brand"] == "Kohler"
    assert results[0].source_attribution == "Google Shopping"
    assert results[0].verification_status == "UNVERIFIED"


# ==============================================================================
# 5. FRONTEND STATIC SECURITY & INTEGRATION CONTRACTS
# ==============================================================================

def test_frontend_saved_calls_are_guarded_and_verification_not_hardcoded():
    saved_caller_files = [
        REPO_ROOT / "frontend" / "app" / "page.tsx",
        REPO_ROOT / "frontend" / "app" / "saved" / "page.tsx",
        REPO_ROOT / "frontend" / "app" / "sourcing" / "page.tsx",
        REPO_ROOT / "frontend" / "app" / "suppliers" / "page.tsx",
        REPO_ROOT / "frontend" / "app" / "supplier" / "[id]" / "page.tsx",
        REPO_ROOT / "frontend" / "app" / "reference" / "[id]" / "page.tsx",
        REPO_ROOT / "frontend" / "app" / "quotations" / "page.tsx",
        REPO_ROOT / "frontend" / "components" / "SavedItemsDrawer.tsx",
        REPO_ROOT / "frontend" / "components" / "ContextualDetailsDrawer.tsx",
        REPO_ROOT / "frontend" / "components" / "SwipeDiscoveryFeed.tsx",
        REPO_ROOT / "frontend" / "components" / "ReferenceModal.tsx",
        REPO_ROOT / "frontend" / "components" / "FeedCard.tsx",
        REPO_ROOT / "frontend" / "components" / "SaveToBoardModal.tsx",
        REPO_ROOT / "frontend" / "lib" / "navigationContext.tsx",
    ]
    for path in saved_caller_files:
        text = path.read_text(encoding="utf-8")
        assert "hasAuthToken" in text, f"Missing hasAuthToken auth guard in {path}"

    api_ts = (REPO_ROOT / "frontend" / "lib" / "api.ts").read_text(encoding="utf-8")
    assert "isJwtExpired" in api_ts
    assert "nivora:auth-expired" in api_ts

    saved_page = (REPO_ROOT / "frontend" / "app" / "saved" / "page.tsx").read_text(encoding="utf-8")
    assert "verification_status: 'VERIFIED'" not in saved_page
    assert 'verification_status: "VERIFIED"' not in saved_page

    drawer = (REPO_ROOT / "frontend" / "components" / "ContextualDetailsDrawer.tsx").read_text(encoding="utf-8")
    assert "vendor.verification_status || 'VERIFIED'" not in drawer
    assert "Commercial Listing Details" in drawer
    assert "Not provided by listing" in drawer

    feed_cmp = (REPO_ROOT / "frontend" / "components" / "PinterestMasonryFeed.tsx").read_text(encoding="utf-8")
    assert "ref.source_platform === 'google_shopping'" in feed_cmp

    badge_cmp = (REPO_ROOT / "frontend" / "components" / "VerificationBadge.tsx").read_text(encoding="utf-8")
    for state in ["POTENTIAL", "VERIFIED", "UNVERIFIED", "UNKNOWN"]:
        assert f'data-verification-state="{state}"' in badge_cmp

    home_page = (REPO_ROOT / "frontend" / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "discoverySearch(" in home_page
    assert "creator_name: item.creator_name || undefined" in home_page
    for label in [
        "Pinterest",
        "Instagram",
        "YouTube",
        "Reddit",
        "Google Shopping",
    ]:
        assert label in home_page

    keyword_panel = (REPO_ROOT / "frontend" / "components" / "KeywordExplorerPanel.tsx").read_text(encoding="utf-8")
    assert "useState<'taxonomy' | 'catalogue'>('catalogue')" in keyword_panel


def test_render_yaml_and_requirements_persistent_sqlite_contract():
    render_yaml = (REPO_ROOT / "render.yaml").read_text(encoding="utf-8")
    assert "mountPath: /var/data" in render_yaml
    assert "sqlite:////var/data/architect_ai.db" in render_yaml
    assert "TRUSTED_PROXIES" in render_yaml
    assert "NIVORA_CORS_ORIGINS" in render_yaml
    assert "GOOGLE_CUSTOM_SEARCH_CX" in render_yaml
    assert "YOUTUBE_API_KEY" not in render_yaml

    reqs = (REPO_ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")
    assert "psycopg2" not in reqs



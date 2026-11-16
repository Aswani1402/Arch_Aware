"""
Phase 3 Tests — Stage 3 Unified Discovery API (/api/discovery/search & /api/discovery/status)
Uses mocked adapters cleanly so zero live external API calls or provider credits are spent.
"""

from unittest.mock import patch

import pytest

from app.schemas.discovery import (
    ContentTypeEnum,
    DiscoveryClassificationEnum,
    MetadataClassificationEnum,
    NormalizedDiscoveryResult,
    SourceExecutionMetrics,
    SourceStatusEnum,
    SourceStatusReport,
)
from app.services.catalogue_import_service import import_catalogue_csv
from app.services.discovery_cache import discovery_cache
from app.services.discovery_guard import discovery_request_guard, provider_budget_manager
from app.services.search_orchestration_service import search_orchestration_service


@pytest.fixture(autouse=True)
def reset_discovery_guards():
    discovery_request_guard.reset()
    provider_budget_manager.reset()
    discovery_cache.clear()
    yield
    discovery_request_guard.reset()
    provider_budget_manager.reset()
    discovery_cache.clear()


def _mock_adapter_success(source_name: str, title: str, url: str):
    item = NormalizedDiscoveryResult(
        source=source_name,
        source_result_id=f"{source_name}_1",
        original_url=url,
        title=title,
        description="Architectural material specification sample",
        content_type=ContentTypeEnum.ARCHITECTURAL_PROJECT.value,
        discovery_classification=DiscoveryClassificationEnum.INSPIRATION,
        metadata_classification=MetadataClassificationEnum.ARCHITECTURAL_PROJECT,
        verification_status="UNVERIFIED",
        relevance_score=0.92,
    )
    status_rep = SourceStatusReport(
        source_name=source_name,
        status=SourceStatusEnum.SUCCESS,
        requested=True,
        results_returned=1,
        duration_ms=12.0,
    )
    mets = SourceExecutionMetrics(
        source_name=source_name,
        requested_result_count=15,
        collected_count=1,
        unique_count=1,
        status=SourceStatusEnum.SUCCESS,
        duration_ms=12.0,
    )
    return ([item], status_rep, mets)


def test_discovery_status_endpoint(client):
    res = client.get("/api/discovery/status")
    assert res.status_code == 200
    data = res.json()
    assert data["engine"] == "Nivora Multi-Source Discovery Engine"
    assert "pinterest" in data["sources"]
    assert data["sources"]["x"]["disabled"] is True
    assert "rate_guard" in data
    assert "budget" in data
    assert "cache" in data


def test_discovery_search_get_and_cache_zero_credit_hit(client, db):
    import_catalogue_csv(db)
    call_counter = {"count": 0}

    async def mock_pin_fetch(*args, **kwargs):
        call_counter["count"] += 1
        return _mock_adapter_success("pinterest", "Teak Timber Louvers", "https://pinterest.com/pin/1001")

    with patch.object(search_orchestration_service.adapters["pinterest"], "fetch_async", side_effect=mock_pin_fetch):
        res1 = client.get("/api/discovery/search?q=Teak+Wood&sources=pinterest&category=Exterior&city=Chennai")
        assert res1.status_code == 200
        d1 = res1.json()
        assert d1["overall_status"] == "SUCCESS"
        assert d1["total_results"] == 1
        assert d1["results"][0]["title"] == "Teak Timber Louvers"
        assert d1["selected_taxonomy_context"]["city"] == "Chennai"
        assert d1["selected_taxonomy_context"]["filter_category"] == "Exterior"
        assert call_counter["count"] == 1
        assert provider_budget_manager._daily_credits_used == 1

        # Second identical call -> cache hit! 0 adapter calls, 0 extra credits
        res2 = client.get("/api/discovery/search?q=Teak+Wood&sources=pinterest&category=Exterior&city=Chennai")
        assert res2.status_code == 200
        d2 = res2.json()
        assert d2["total_results"] == 1
        assert any("bounded discovery cache" in w for w in d2["warnings"])
        assert call_counter["count"] == 1
        assert provider_budget_manager._daily_credits_used == 1


def test_discovery_search_post_and_partial_success_isolation(client, user_headers):
    async def mock_pin_ok(*args, **kwargs):
        return _mock_adapter_success("pinterest", "Athangudi Floor Tiles", "https://pinterest.com/pin/2002")

    async def mock_yt_fail(*args, **kwargs):
        raise RuntimeError("Upstream 502 error")

    with (
        patch.object(search_orchestration_service.adapters["pinterest"], "fetch_async", side_effect=mock_pin_ok),
        patch.object(search_orchestration_service.adapters["youtube"], "fetch_async", side_effect=mock_yt_fail),
    ):
        res = client.post(
            "/api/discovery/search",
            json={
                "q": "Athangudi Tiles",
                "sources": ["pinterest", "youtube", "x"],
                "tab": "all",
                "page": 1,
                "page_size": 20,
            },
            headers=user_headers,
        )
        assert res.status_code == 200
        body = res.json()
        assert body["overall_status"] == "PARTIAL_SUCCESS"
        assert body["total_results"] == 1
        assert body["source_statuses"]["pinterest"]["status"] == "SUCCESS"
        assert body["source_statuses"]["youtube"]["status"] == "FAILED"
        assert body["source_statuses"]["x"]["status"] == "DISABLED"


def test_discovery_search_empty_query_rejected_422(client):
    assert client.get("/api/discovery/search?q=   ").status_code == 422


def test_discovery_search_anonymous_xff_spoof_cannot_bypass_rate_limit(client):
    async def mock_pin_dry(*args, **kwargs):
        return _mock_adapter_success("pinterest", "Dry Run Pin", "https://pinterest.com/pin/dry")

    with patch.object(search_orchestration_service.adapters["pinterest"], "fetch_async", side_effect=mock_pin_dry):
        # 15 allowed anonymous requests even if attacker cycles forged X-Forwarded-For values
        for idx in range(15):
            r = client.get(
                f"/api/discovery/search?q=Marble+{idx}&sources=pinterest&dry_run=true",
                headers={"X-Forwarded-For": f"198.51.100.{idx + 1}"},
            )
            assert r.status_code == 200

        # Request 16 from same peer must be blocked with 429 and Retry-After
        blocked = client.get(
            "/api/discovery/search?q=Marble+16&sources=pinterest&dry_run=true",
            headers={"X-Forwarded-For": "198.51.100.250"},
        )
        assert blocked.status_code == 429
        assert "Retry-After" in blocked.headers

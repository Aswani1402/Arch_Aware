"""
Nivora — Phase 5B Stage 1 Regression & Schema Validation Tests
Tests the normalized discovery response architecture, 3 independent classification dimensions,
per-source status and execution metrics, pagination contracts, and backward compatibility.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

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
    determine_relevant_discovery_tabs,
)
from app.schemas.schemas import FeedResponse, ReferenceOut, SupplierOut


# ==============================================================================
# 1. NORMALIZED RESULT & FIELD VALIDATION
# ==============================================================================

def test_normalized_discovery_result_minimal_valid():
    """Verify that a discovery result can be constructed with only mandatory fields."""
    res = NormalizedDiscoveryResult(
        source="pinterest",
        original_url="https://www.pinterest.com/pin/123456789/",
        title="Minimal Modern Staircase Inspiration"
    )
    assert res.source == "pinterest"
    assert res.title == "Minimal Modern Staircase Inspiration"
    assert res.original_url == "https://www.pinterest.com/pin/123456789/"
    assert res.id is None
    assert res.description is None
    assert res.image_url is None
    assert res.creator_name is None
    assert res.content_type is None
    assert res.discovery_classification is None
    assert res.metadata_classification is None
    assert res.verification_status == "UNVERIFIED"
    assert res.price is None
    assert res.phone is None


def test_missing_optional_fields_allowed():
    """
    Verify:
    - Product results can exist without business information.
    - Business results can exist without product prices.
    - Architectural inspiration can exist without a creator name.
    """
    # 1. Product without business info
    prod = NormalizedDiscoveryResult(
        source="google_shopping",
        original_url="https://shopping.google.com/p/123",
        title="Astral CPVC Pipe 1 inch",
        price=450.0,
        currency="INR"
    )
    assert prod.phone is None
    assert prod.address is None
    assert prod.business_category is None
    assert prod.price == 450.0

    # 2. Business without product price
    biz = NormalizedDiscoveryResult(
        source="google_business",
        original_url="https://maps.google.com/?cid=987",
        title="Kochi Tile Emporium",
        phone="+91 98460 12345",
        address="MG Road, Kochi, Kerala",
        business_category="Tile Dealer"
    )
    assert biz.price is None
    assert biz.phone == "+91 98460 12345"

    # 3. Inspiration without creator name
    insp = NormalizedDiscoveryResult(
        source="curated",
        original_url="https://nivora.internal/curated/101",
        title="Double Height Tropical Living Courtyard",
        image_url="https://images.unsplash.com/photo-1512917774080"
    )
    assert insp.creator_name is None
    assert insp.creator_url is None


# ==============================================================================
# 2. THE THREE CLASSIFICATION DIMENSIONS
# ==============================================================================

def test_three_classification_dimensions_are_independent():
    """
    Ensure Dimension A (content_type), Dimension B (discovery_classification),
    and Dimension C (metadata_classification) are completely independent and not merged.
    """
    result = NormalizedDiscoveryResult(
        source="youtube",
        original_url="https://www.youtube.com/watch?v=abc123xyz",
        title="Laying Athangudi Handmade Tiles on Site",
        content_type="youtube_walkthrough",                                   # Dimension A
        discovery_classification=DiscoveryClassificationEnum.INSTALLATION,     # Dimension B
        metadata_classification=MetadataClassificationEnum.CONSTRUCTION_PROGRESS # Dimension C
    )
    assert result.content_type == "youtube_walkthrough"
    assert result.discovery_classification == DiscoveryClassificationEnum.INSTALLATION
    assert result.metadata_classification == MetadataClassificationEnum.CONSTRUCTION_PROGRESS


def test_dimension_b_17_canonical_classifications():
    """Verify that all 17 Discovery Classification roles are valid and supported."""
    roles = [
        "Inspiration", "Completed Project", "Work in Progress", "Architect Portfolio",
        "Builder Portfolio", "Contractor Work", "Interior Design Project", "Product",
        "Product Demonstration", "Manufacturer", "Supplier", "Wholesaler",
        "Retailer", "Showroom", "Installation", "Tutorial", "Discussion"
    ]
    for r in roles:
        item = NormalizedDiscoveryResult(
            source="test",
            original_url="https://example.com",
            title="Test Item",
            discovery_classification=r
        )
        assert item.discovery_classification is not None
        assert item.discovery_classification.value == r


def test_dimension_c_17_metadata_classifications():
    """Verify that all 17 Metadata Classification types are valid and supported."""
    domains = [
        "architectural_project", "interior_design", "construction_progress",
        "detail_drawing", "material_specification", "product_catalog",
        "installation_guide", "supplier_profile", "cost_breakdown",
        "structural_engineering", "mep_system", "landscape_design",
        "facade_detail", "sustainable_building", "renovation_before_after",
        "artisan_craft", "smart_home_tech"
    ]
    for d in domains:
        item = NormalizedDiscoveryResult(
            source="test",
            original_url="https://example.com",
            title="Test Item",
            metadata_classification=d
        )
        assert item.metadata_classification is not None
        assert item.metadata_classification.value == d


def test_invalid_classification_values_rejected():
    """Verify that invalid/arbitrary classification values are rejected with validation error."""
    with pytest.raises(ValidationError):
        NormalizedDiscoveryResult(
            source="test",
            original_url="https://example.com",
            title="Invalid Classification Test",
            discovery_classification="Completely Arbitrary Non-Architectural Tag"
        )

    with pytest.raises(ValidationError):
        NormalizedDiscoveryResult(
            source="test",
            original_url="https://example.com",
            title="Invalid Metadata Test",
            metadata_classification="unrecognized_taxonomy_domain"
        )


def test_lenient_classification_normalization():
    """Verify that snake_case or lowercase inputs normalize to canonical Title Case enums."""
    res = NormalizedDiscoveryResult(
        source="test",
        original_url="https://example.com",
        title="Normalizer Test",
        discovery_classification="work_in_progress",
        metadata_classification="ARTISAN-CRAFT"
    )
    assert res.discovery_classification == DiscoveryClassificationEnum.WORK_IN_PROGRESS
    assert res.metadata_classification == MetadataClassificationEnum.ARTISAN_CRAFT


# ==============================================================================
# 3. TAB ROUTING RULES
# ==============================================================================

def test_tab_routing_rules():
    """Verify that items map appropriately to the 3 discovery tabs, allowing multiple tabs."""
    # 1. Visual inspiration reel
    reel = NormalizedDiscoveryResult(
        source="instagram",
        original_url="https://instagram.com/reel/1",
        title="Modern Minimalist Villa Facade",
        content_type="architectural_reel",
        discovery_classification=DiscoveryClassificationEnum.INSPIRATION
    )
    tabs = determine_relevant_discovery_tabs(reel)
    assert DiscoveryTabEnum.INSPIRATION.value in tabs

    # 2. Construction walkthrough tutorial (relevant to projects_work and inspiration)
    tutorial = NormalizedDiscoveryResult(
        source="youtube",
        original_url="https://youtube.com/watch?v=2",
        title="How to Cast Athangudi Tiles Step by Step",
        content_type="youtube_walkthrough",
        discovery_classification=DiscoveryClassificationEnum.TUTORIAL,
        metadata_classification=MetadataClassificationEnum.ARTISAN_CRAFT
    )
    tabs_tut = determine_relevant_discovery_tabs(tutorial)
    assert DiscoveryTabEnum.PROJECTS_WORK.value in tabs_tut

    # 3. Product catalog from manufacturer
    prod = NormalizedDiscoveryResult(
        source="google_shopping",
        original_url="https://shopping.google.com/3",
        title="Kohler Rain Shower Diverter 3-Way",
        content_type="manufacturer_product",
        discovery_classification=DiscoveryClassificationEnum.PRODUCT,
        price=8500.0,
        currency="INR"
    )
    tabs_prod = determine_relevant_discovery_tabs(prod)
    assert DiscoveryTabEnum.PRODUCTS_SUPPLIERS.value in tabs_prod

    # 4. Multi-tab demonstration: installation demo of product
    dual = NormalizedDiscoveryResult(
        source="youtube",
        original_url="https://youtube.com/watch?v=4",
        title="Hafele Soft-Close Tandem Box Installation & Sourcing",
        content_type="installation_demo",
        discovery_classification=DiscoveryClassificationEnum.PRODUCT_DEMONSTRATION,
        business_category="Hardware Distributor"
    )
    tabs_dual = determine_relevant_discovery_tabs(dual)
    assert DiscoveryTabEnum.PROJECTS_WORK.value in tabs_dual
    assert DiscoveryTabEnum.PRODUCTS_SUPPLIERS.value in tabs_dual


# ==============================================================================
# 4. SOURCE STATUS REPORT & PER-SOURCE METRICS
# ==============================================================================

def test_source_status_report_and_metrics():
    """Verify creation and accounting of SourceStatusReport and SourceExecutionMetrics."""
    status_report = SourceStatusReport(
        source_name="pinterest",
        status=SourceStatusEnum.SUCCESS,
        requested=True,
        result_count=35,
        unique_result_count=32,
        pages_fetched=2,
        has_more=True,
        next_page_token="cursor_token_abc_123",
        duration_ms=450.5
    )
    assert status_report.status == SourceStatusEnum.SUCCESS
    assert status_report.unique_result_count == 32
    assert status_report.error_code is None

    metrics = SourceExecutionMetrics(
        source_name="instagram",
        requested_result_count=50,
        returned_result_count=28,
        unique_result_count=26,
        duplicate_count=2,
        pages_fetched=2,
        pagination_availability=True,
        request_count=2,
        cache_hit=False,
        duration_ms=820.0,
        status=SourceStatusEnum.SUCCESS
    )
    assert metrics.duplicate_count == 2
    assert metrics.returned_result_count == 28


# ==============================================================================
# 5. UNIFIED DISCOVERY RESPONSE & MULTI-SOURCE SCENARIOS
# ==============================================================================

def test_scenario_a_partial_success():
    """
    Scenario A:
    Pinterest returns results.
    Instagram fails (timeout/error).
    YouTube returns results.
    Unified response must preserve successful results and identify Instagram as failed.
    """
    item_p = NormalizedDiscoveryResult(
        source="pinterest",
        original_url="https://pinterest.com/pin/1",
        title="Pinterest Modern Living Room"
    )
    item_yt = NormalizedDiscoveryResult(
        source="youtube",
        original_url="https://youtube.com/watch?v=2",
        title="YouTube Architecture Tour"
    )

    response = UnifiedDiscoveryResponse(
        query="Modern Living Room",
        normalized_query="modern living room",
        overall_status=DiscoveryOverallStatusEnum.PARTIAL_SUCCESS,
        total_results=2,
        unique_results=2,
        results=[item_p, item_yt],
        source_metrics={
            "pinterest": SourceExecutionMetrics(
                source_name="pinterest",
                returned_result_count=1,
                unique_result_count=1,
                status=SourceStatusEnum.SUCCESS,
                duration_ms=320.0
            ),
            "instagram": SourceExecutionMetrics(
                source_name="instagram",
                returned_result_count=0,
                unique_result_count=0,
                status=SourceStatusEnum.FAILED,
                error_code="UPSTREAM_TIMEOUT",
                error_message="Instagram request timed out after 46s",
                duration_ms=46000.0
            ),
            "youtube": SourceExecutionMetrics(
                source_name="youtube",
                returned_result_count=1,
                unique_result_count=1,
                status=SourceStatusEnum.SUCCESS,
                duration_ms=280.0
            )
        },
        source_statuses={
            "pinterest": SourceStatusReport(source_name="pinterest", status=SourceStatusEnum.SUCCESS, result_count=1),
            "instagram": SourceStatusReport(source_name="instagram", status=SourceStatusEnum.FAILED, error_code="UPSTREAM_TIMEOUT", error_message="Instagram request timed out after 46s"),
            "youtube": SourceStatusReport(source_name="youtube", status=SourceStatusEnum.SUCCESS, result_count=1)
        },
        pagination=DiscoveryPagination(page=1, page_size=30, total_results=2, unique_results=2),
        warnings=["Instagram search temporarily unavailable. Results delivered from Pinterest, YouTube."],
        errors=[{"source": "instagram", "error_code": "UPSTREAM_TIMEOUT", "message": "Instagram request timed out after 46s"}],
        request_id="req_test_partial_success_001"
    )

    assert response.overall_status == DiscoveryOverallStatusEnum.PARTIAL_SUCCESS
    assert len(response.results) == 2
    assert response.source_statuses["instagram"].status == SourceStatusEnum.FAILED
    assert response.source_statuses["pinterest"].status == SourceStatusEnum.SUCCESS
    assert len(response.warnings) == 1
    assert "Instagram search temporarily unavailable" in response.warnings[0]


def test_scenario_b_all_sources_empty():
    """
    Scenario B:
    All external sources return 0 results.
    The response must report EMPTY rather than falsely reporting an error.
    """
    response = UnifiedDiscoveryResponse(
        query="NonExistentArchitecturalMaterialXYZ",
        normalized_query="nonexistentarchitecturalmaterialxyz",
        overall_status=DiscoveryOverallStatusEnum.EMPTY,
        total_results=0,
        unique_results=0,
        results=[],
        source_metrics={
            "pinterest": SourceExecutionMetrics(source_name="pinterest", returned_result_count=0, status=SourceStatusEnum.EMPTY),
            "instagram": SourceExecutionMetrics(source_name="instagram", returned_result_count=0, status=SourceStatusEnum.EMPTY),
            "youtube": SourceExecutionMetrics(source_name="youtube", returned_result_count=0, status=SourceStatusEnum.EMPTY)
        },
        pagination=DiscoveryPagination(page=1, page_size=30, total_results=0, unique_results=0),
        warnings=["No external results discovered for query."],
        request_id="req_test_empty_002"
    )
    assert response.overall_status == DiscoveryOverallStatusEnum.EMPTY
    assert response.total_results == 0
    assert len(response.errors) == 0


def test_scenario_c_unconfigured_source():
    """
    Scenario C:
    One source is NOT_CONFIGURED (e.g. Google Search CX missing).
    Other sources remain completely usable.
    """
    response = UnifiedDiscoveryResponse(
        query="Staircase Railings",
        normalized_query="staircase railings",
        overall_status=DiscoveryOverallStatusEnum.SUCCESS,
        total_results=5,
        unique_results=5,
        results=[
            NormalizedDiscoveryResult(source="pinterest", original_url="https://pin.it/1", title="Staircase Railing 1")
        ],
        source_metrics={
            "pinterest": SourceExecutionMetrics(source_name="pinterest", returned_result_count=1, status=SourceStatusEnum.SUCCESS),
            "google_search": SourceExecutionMetrics(
                source_name="google_search",
                returned_result_count=0,
                status=SourceStatusEnum.NOT_CONFIGURED,
                error_message="Search Engine CX ID is not configured."
            )
        },
        pagination=DiscoveryPagination(page=1, page_size=30, total_results=5, unique_results=5),
        request_id="req_test_unconfigured_003"
    )
    assert response.source_metrics["google_search"].status == SourceStatusEnum.NOT_CONFIGURED
    assert response.source_metrics["pinterest"].status == SourceStatusEnum.SUCCESS
    assert len(response.results) > 0


def test_scenario_d_all_external_sources_fail():
    """
    Scenario D:
    All external sources fail (e.g. total network outage).
    Response clearly represents failure status without unhandled exceptions.
    """
    response = UnifiedDiscoveryResponse(
        query="TMT Steel 550D",
        normalized_query="tmt steel 550d",
        overall_status=DiscoveryOverallStatusEnum.FAILED,
        total_results=0,
        unique_results=0,
        results=[],
        source_metrics={
            "instagram": SourceExecutionMetrics(source_name="instagram", status=SourceStatusEnum.FAILED, error_code="NET_CONN_REFUSED"),
            "youtube": SourceExecutionMetrics(source_name="youtube", status=SourceStatusEnum.FAILED, error_code="NET_CONN_REFUSED")
        },
        pagination=DiscoveryPagination(page=1, page_size=30, total_results=0, unique_results=0),
        errors=[
            {"source": "instagram", "error_code": "NET_CONN_REFUSED", "message": "Connection refused"},
            {"source": "youtube", "error_code": "NET_CONN_REFUSED", "message": "Connection refused"}
        ],
        request_id="req_test_all_fail_004"
    )
    assert response.overall_status == DiscoveryOverallStatusEnum.FAILED
    assert len(response.errors) == 2


# ==============================================================================
# 6. BACKWARD COMPATIBILITY VERIFICATION
# ==============================================================================

def test_backward_compatibility_with_existing_feed_response():
    """
    Verify that existing FeedResponse and ReferenceOut schemas continue to instantiate
    and serialize without any interference from the new discovery models.
    """
    existing_ref = ReferenceOut(
        id=101,
        title="Traditional Kerala Courtyard House",
        slug="traditional-kerala-courtyard-house",
        source_platform="curated",
        source_url="https://architectai.internal/curated/101",
        content_type="architectural_project",
        verification_status="VERIFIED",
        created_at=datetime.utcnow()
    )
    feed = FeedResponse(
        items=[existing_ref],
        total=1,
        page=1,
        page_size=28,
        has_more=False,
        connector_status={"configured": True}
    )
    assert feed.total == 1
    assert feed.items[0].slug == "traditional-kerala-courtyard-house"
    assert feed.items[0].content_type == "architectural_project"


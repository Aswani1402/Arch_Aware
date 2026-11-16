"""
Nivora — Phase 1.7 Keyword-Driven Discovery & Taxonomy Tests

Validates:
1. Exact keyword selection & taxonomy context propagation
2. Provider-specific query engines (Google Places, Google Shopping, YouTube, Pinterest, Instagram, Reddit)
3. Catalogue accessibility (10 categories, 184 subcategories, 6,319 materials, offset 250+ pagination)
4. Result association, deduplication, error isolation, zero paid credit consumption
"""

import sqlite3
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from app.schemas.discovery import (
    SourceStatusEnum,
    DiscoveryOverallStatusEnum,
    ContentTypeEnum,
    NormalizedDiscoveryResult,
)
from app.services.search_orchestration_service import (
    SearchOrchestrationService,
)
from app.services.discovery_adapters import (
    PinterestAdapter,
    InstagramAdapter,
    YouTubeAdapter,
    RedditAdapter,
    GoogleShoppingAdapter,
    GooglePlacesAdapter,
)


SEED_DB_PATH = Path("backend/seed_catalogue.sqlite")


# ==============================================================================
# 1. KEYWORD CONTEXT & PROVIDER PROPAGATION TESTS
# ==============================================================================

def test_google_places_keyword_and_location_propagation():
    adapter = GooglePlacesAdapter()
    tax_ctx = {
        "city": "Kozhikode",
        "state": "Kerala",
        "category": "Masonry & Concrete",
        "subcategory": "Concrete Blocks",
        "exact_keyword": "AAC Blocks",
    }
    queries = adapter.build_queries("AAC Blocks", taxonomy_context=tax_ctx)
    assert len(queries) >= 2
    # Verify exact keyword and location are present in generated queries
    assert any("AAC Blocks" in q for q in queries)
    assert any("Kozhikode, Kerala" in q for q in queries)
    assert any("suppliers" in q for q in queries)
    assert any("dealers and manufacturers" in q for q in queries)


def test_google_places_steel_and_cement_variations():
    adapter = GooglePlacesAdapter()
    tmt_queries = adapter.build_queries("TMT Bars", taxonomy_context={"city": "Chennai"})
    assert any("distributors and dealers" in q for q in tmt_queries)
    assert any("Chennai" in q for q in tmt_queries)

    cement_queries = adapter.build_queries("Cement", taxonomy_context={"city": "Kochi"})
    assert any("dealers and manufacturers" in q for q in cement_queries)
    assert any("Kochi" in q for q in cement_queries)


def test_google_shopping_aac_blocks_expansions():
    adapter = GoogleShoppingAdapter()
    queries = adapter.build_queries("AAC Blocks", taxonomy_context={"category": "Masonry"})
    # Must include concrete blocks, products, manufacturers, construction
    assert any("concrete blocks" in q for q in queries)
    assert any("products" in q for q in queries)
    assert any("manufacturers" in q for q in queries)
    assert any("for construction" in q for q in queries)
    # Must exclude unrelated consumer items
    assert all("-toy" in q or q == "AAC Blocks" for q in queries)
    assert all("-wallpaper" in q or q == "AAC Blocks" for q in queries)


def test_youtube_keyword_query_expansions():
    adapter = YouTubeAdapter()
    queries = adapter.build_queries("AAC Blocks")
    assert "AAC Blocks construction" in queries
    assert "AAC Blocks installation" in queries
    assert "AAC Blocks manufacturing" in queries
    assert "AAC Blocks comparison" in queries
    assert "AAC Blocks building projects" in queries


def test_pinterest_keyword_query_expansions():
    adapter = PinterestAdapter()
    queries = adapter.build_queries("AAC Blocks")
    assert "AAC Blocks architecture" in queries
    assert "AAC Blocks wall design" in queries
    assert "AAC Blocks construction inspiration" in queries
    assert "AAC Blocks house projects" in queries


def test_instagram_keyword_query_expansions():
    adapter = InstagramAdapter()
    queries = adapter.build_queries("AAC Blocks")
    assert "AAC Blocks architecture design" in queries
    assert "AAC Blocks construction projects" in queries
    assert "AAC Blocks design walkthrough" in queries


def test_reddit_keyword_query_expansions():
    adapter = RedditAdapter()
    queries = adapter.build_queries("AAC Blocks")
    assert "AAC Blocks comparisons and construction discussions" in queries
    assert "AAC Blocks cost durability experience" in queries
    assert "AAC Blocks architecture materials review" in queries


# ==============================================================================
# 2. CATALOGUE TAXONOMY AUDIT TESTS (READ-ONLY AGAINST SANITIZED SEED)
# ==============================================================================

def test_catalogue_10_categories_accessible():
    assert SEED_DB_PATH.exists()
    conn = sqlite3.connect(f"file:{SEED_DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("SELECT slug FROM catalogue_categories ORDER BY display_order, id;")
    actual_slugs = {row[0] for row in cur.fetchall()}
    conn.close()

    assert len(actual_slugs) == 10
    expected_slugs = {
        "exterior",
        "interior",
        "machinery-tools",
        "mep-building-services",
        "healthcare-hospital",
        "materials-metals-timber-chemicals",
        "industrial-commercial-institutional",
        "safety-security-site-welfare",
        "doors-windows-hardware-fixtures",
        "water-waste-landscape-external-utilities",
    }
    assert expected_slugs == actual_slugs


def test_catalogue_184_subcategories_accessible():
    conn = sqlite3.connect(f"file:{SEED_DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM catalogue_subcategories;")
    sub_count = cur.fetchone()[0]

    # Every subcategory belongs to a valid category
    cur.execute("""
        SELECT COUNT(*) FROM catalogue_subcategories s
        LEFT JOIN catalogue_categories c ON s.category_id = c.id
        WHERE c.id IS NULL;
    """)
    orphan_subs = cur.fetchone()[0]
    conn.close()

    assert sub_count == 184
    assert orphan_subs == 0


def test_catalogue_6319_materials_accessible():
    conn = sqlite3.connect(f"file:{SEED_DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM catalogue_materials;")
    mat_count = cur.fetchone()[0]

    # No orphan materials
    cur.execute("""
        SELECT COUNT(*) FROM catalogue_materials m
        LEFT JOIN catalogue_categories c ON m.category_id = c.id
        WHERE c.id IS NULL;
    """)
    orphan_cats = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM catalogue_materials m
        LEFT JOIN catalogue_subcategories s ON m.subcategory_id = s.id
        WHERE s.id IS NULL;
    """)
    orphan_subs = cur.fetchone()[0]
    conn.close()

    assert mat_count == 6319
    assert orphan_cats == 0
    assert orphan_subs == 0


def test_catalogue_pagination_beyond_250():
    conn = sqlite3.connect(f"file:{SEED_DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM catalogue_materials ORDER BY id LIMIT 50 OFFSET 250;")
    rows = cur.fetchall()
    conn.close()

    assert len(rows) == 50
    ids = [r[0] for r in rows]
    assert len(set(ids)) == 50
    assert ids[0] == 251
    assert ids[-1] == 300


def test_material_search_aac_blocks():
    conn = sqlite3.connect(f"file:{SEED_DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("""
        SELECT m.name, c.name, s.name FROM catalogue_materials m
        JOIN catalogue_categories c ON m.category_id = c.id
        JOIN catalogue_subcategories s ON m.subcategory_id = s.id
        WHERE m.name LIKE '%AAC%';
    """)
    hits = cur.fetchall()
    conn.close()

    assert len(hits) >= 1
    assert any("aac block" in h[0].lower() for h in hits)


def test_material_categories_distinct_from_catalogue():
    conn = sqlite3.connect(f"file:{SEED_DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM material_categories;")
    mat_cat_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM catalogue_categories;")
    cat_cat_count = cur.fetchone()[0]
    conn.close()

    assert mat_cat_count == 56
    assert cat_cat_count == 10
    assert mat_cat_count != cat_cat_count


# ==============================================================================
# 3. DISCOVERY ORCHESTRATION & ERROR ISOLATION (ZERO LIVE API CALLS)
# ==============================================================================

@pytest.mark.asyncio
async def test_orchestration_associates_keyword_and_isolates_failures():
    service = SearchOrchestrationService()

    # Mock pinterest and instagram returning items, youtube failing
    mock_pin_item = NormalizedDiscoveryResult(
        source="pinterest",
        original_url="https://pinterest.com/pin/101",
        title="AAC Block Wall Design Inspiration",
        content_type=ContentTypeEnum.ARCHITECTURAL_PROJECT,
        creator_name="ArchDesign",
        discovery_query="AAC block architecture",
    )

    with patch.object(PinterestAdapter, "fetch_async") as mock_pin, \
         patch.object(YouTubeAdapter, "fetch_async") as mock_yt, \
         patch.object(InstagramAdapter, "fetch_async") as mock_insta, \
         patch.object(RedditAdapter, "fetch_async") as mock_reddit, \
         patch.object(GoogleShoppingAdapter, "fetch_async") as mock_shop:

        from app.schemas.discovery import SourceStatusReport, SourceExecutionMetrics
        mock_pin.return_value = (
            [mock_pin_item],
            SourceStatusReport(source_name="pinterest", status=SourceStatusEnum.SUCCESS, requested=True, duration_ms=10.0),
            SourceExecutionMetrics(source_name="pinterest", requested_result_count=10, status=SourceStatusEnum.SUCCESS, duration_ms=10.0)
        )
        mock_yt.side_effect = Exception("YouTube upstream simulated failure")
        mock_insta.return_value = (
            [],
            SourceStatusReport(source_name="instagram", status=SourceStatusEnum.EMPTY, duration_ms=5.0),
            SourceExecutionMetrics(source_name="instagram", requested_result_count=10, status=SourceStatusEnum.EMPTY, duration_ms=5.0)
        )
        mock_reddit.return_value = (
            [],
            SourceStatusReport(source_name="reddit", status=SourceStatusEnum.EMPTY, duration_ms=5.0),
            SourceExecutionMetrics(source_name="reddit", requested_result_count=10, status=SourceStatusEnum.EMPTY, duration_ms=5.0)
        )
        mock_shop.return_value = (
            [],
            SourceStatusReport(source_name="google_shopping", status=SourceStatusEnum.EMPTY, duration_ms=5.0),
            SourceExecutionMetrics(source_name="google_shopping", requested_result_count=10, status=SourceStatusEnum.EMPTY, duration_ms=5.0)
        )

        resp = await service.orchestrate_discovery_async(
            query="AAC Blocks",
            sources=["pinterest", "youtube", "instagram", "reddit", "google_shopping"],
            enforce_guard=False,
            dry_run=False,
            target_per_source=10
        )

        assert resp.query == "AAC Blocks"
        # Partial failure does not crash discovery
        assert resp.overall_status in (DiscoveryOverallStatusEnum.PARTIAL_SUCCESS, DiscoveryOverallStatusEnum.SUCCESS)
        assert resp.source_statuses["pinterest"].status == SourceStatusEnum.SUCCESS
        assert resp.source_statuses["youtube"].status == SourceStatusEnum.FAILED
        assert len(resp.results) == 1
        assert resp.results[0].title == "AAC Block Wall Design Inspiration"

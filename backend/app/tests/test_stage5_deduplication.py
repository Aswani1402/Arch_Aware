"""
MATERIQ — Stage 5 Deduplication Test Suite
Tests:
1. Duplicated pin IDs merged
2. Duplicated YouTube IDs across URL formats (watch?v=ID, youtu.be/ID, /shorts/ID) merged
3. Same URL with tracking parameters merged
4. Two different similar houses preserved (both kept)
"""

import pytest
from app.schemas.discovery import (
    NormalizedDiscoveryResult,
    DiscoveryClassificationEnum,
    ContentTypeEnum,
)
from app.services.search_orchestration_service import search_orchestration_service


def make_test_item(
    source="pinterest",
    source_result_id="pin_101",
    original_url="https://www.pinterest.com/pin/101",
    canonical_url=None,
    title="Minimalist exposed brick villa in Kerala",
    creator_name="Kerala Architect Studio",
    image_url="https://i.pinimg.com/originals/12/34/56/image101.jpg"
):
    return NormalizedDiscoveryResult(
        source=source,
        source_result_id=source_result_id,
        original_url=original_url,
        canonical_url=canonical_url or original_url,
        title=title,
        creator_name=creator_name,
        image_url=image_url,
        content_type=ContentTypeEnum.ARCHITECTURAL_PROJECT.value,
        discovery_classification=DiscoveryClassificationEnum.INSPIRATION,
    )


def test_stage5_duplicated_pin_ids():
    """Two items sharing the same Pinterest pin ID are merged into 1."""
    item1 = make_test_item(source="pinterest", source_result_id="998877", title="Exposed brick facade")
    item2 = make_test_item(source="pinterest", source_result_id="998877", title="Exposed brick facade variant")

    deduped, dup_count = search_orchestration_service.deduplicate_results([item1, item2])
    assert len(deduped) == 1
    assert dup_count == 1
    assert deduped[0].source_result_id == "998877"


def test_stage5_duplicated_youtube_ids_across_url_formats():
    """watch?v=ID, youtu.be/ID, and /shorts/ID pointing to the same video ID are merged."""
    video_id = "dQw4w9WgXcQ"
    item_watch = make_test_item(
        source="youtube",
        source_result_id="yt_1",
        original_url=f"https://www.youtube.com/watch?v={video_id}",
        title="Modern Tropical Villa Tour"
    )
    item_short = make_test_item(
        source="youtube",
        source_result_id="yt_2",
        original_url=f"https://www.youtube.com/shorts/{video_id}",
        title="Modern Tropical Villa Tour Quick Short"
    )
    item_share = make_test_item(
        source="youtube",
        source_result_id="yt_3",
        original_url=f"https://youtu.be/{video_id}?feature=shared",
        title="Modern Tropical Villa Tour Share"
    )

    deduped, dup_count = search_orchestration_service.deduplicate_results([item_watch, item_short, item_share])
    assert len(deduped) == 1
    assert dup_count == 2
    assert "dQw4w9WgXcQ" in (deduped[0].canonical_url or deduped[0].original_url)


def test_stage5_same_url_with_tracking_params():
    """Canonical URLs with utm_source, ref, fbclid parameters are stripped and deduped."""
    base_url = "https://www.dezeen.com/2026/01/kerala-brick-residence"
    item_clean = make_test_item(
        source="pinterest",
        source_result_id="pin_201",
        original_url=base_url,
        title="Kerala Brick Residence on Dezeen"
    )
    item_tracking = make_test_item(
        source="pinterest",
        source_result_id="pin_202",
        original_url=f"{base_url}?utm_source=newsletter&utm_medium=email&utm_campaign=daily&fbclid=IwAR123",
        title="Kerala Brick Residence on Dezeen with Trackers"
    )

    deduped, dup_count = search_orchestration_service.deduplicate_results([item_clean, item_tracking])
    assert len(deduped) == 1
    assert dup_count == 1


def test_stage5_pinterest_cdn_size_path_normalization():
    """Images at /236x/ and /736x/ pointing to the same pin image are deduped."""
    item_small = make_test_item(
        source="pinterest",
        source_result_id="pin_301",
        original_url="https://www.pinterest.com/pin/301",
        image_url="https://i.pinimg.com/236x/ab/cd/ef/house_elevation.jpg",
        title="Courtyard residence with laterite stone"
    )
    item_large = make_test_item(
        source="pinterest",
        source_result_id="pin_302",
        original_url="https://www.pinterest.com/pin/302",
        image_url="https://i.pinimg.com/736x/ab/cd/ef/house_elevation.jpg",
        title="Courtyard residence with laterite stone"
    )

    deduped, dup_count = search_orchestration_service.deduplicate_results([item_small, item_large])
    assert len(deduped) == 1
    assert dup_count == 1


def test_stage5_two_different_similar_houses_both_kept():
    """Two different houses (different media IDs, different URLs, different titles) are BOTH preserved."""
    house_a = make_test_item(
        source="pinterest",
        source_result_id="pin_401",
        original_url="https://www.pinterest.com/pin/401",
        title="Contemporary exposed brick home in Bangalore",
        creator_name="Studio A",
        image_url="https://i.pinimg.com/originals/11/22/33/bangalore_house.jpg"
    )
    house_b = make_test_item(
        source="pinterest",
        source_result_id="pin_402",
        original_url="https://www.pinterest.com/pin/402",
        title="Modern clay brick residence in Kochi",
        creator_name="Studio B",
        image_url="https://i.pinimg.com/originals/44/55/66/kochi_residence.jpg"
    )

    deduped, dup_count = search_orchestration_service.deduplicate_results([house_a, house_b])
    assert len(deduped) == 2
    assert dup_count == 0
    assert {it.source_result_id for it in deduped} == {"pin_401", "pin_402"}

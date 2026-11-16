from unittest.mock import patch
from app.services.discovery_cache import BoundedDiscoveryCache
from app.services.daily_collection_service import (
    HIGH_PRIORITY_KEYWORDS,
    MEDIUM_PRIORITY_KEYWORDS,
    MAX_DAILY_API_CALLS,
    get_kolkata_now,
    get_next_9am_ist,
    seconds_until_next_9am_ist,
    execute_daily_collection_task,
    save_supplier_lead,
)


def test_bounded_discovery_cache_lru_and_ttl():
    cache = BoundedDiscoveryCache(max_entries=2, ttl_seconds=60)
    k1 = cache.build_key(query="brick", tab="all", sources=None, page=1, page_size=20)
    k2 = cache.build_key(query="marble", tab="all", sources=None, page=1, page_size=20)
    k3 = cache.build_key(query="steel", tab="all", sources=None, page=1, page_size=20)

    cache.set(k1, {"q": "brick"})
    cache.set(k2, {"q": "marble"})
    # Access k1 so k2 becomes least-recently-used
    assert cache.get(k1) == {"q": "brick"}
    cache.set(k3, {"q": "steel"})

    stats = cache.stats()
    assert stats["entries"] == 2
    assert stats["max_entries"] == 2
    assert cache.get(k2) is None
    assert cache.get(k1) == {"q": "brick"}
    assert cache.get(k3) == {"q": "steel"}


def test_daily_scheduler_no_x_source_and_bounded_budget():
    all_sources = {t["source"] for t in HIGH_PRIORITY_KEYWORDS + MEDIUM_PRIORITY_KEYWORDS}
    assert "x" not in all_sources
    assert "twitter" not in all_sources
    assert 1 <= MAX_DAILY_API_CALLS <= 100

    next_9 = get_next_9am_ist()
    assert next_9.hour == 9 and next_9.minute == 0
    assert seconds_until_next_9am_ist() >= 0.0
    assert get_kolkata_now() is not None


def test_save_supplier_lead_does_not_force_kochi(db):
    ok = save_supplier_lead(
        db,
        {
            "name": "Deccan Timber Depot",
            "category": "Timber Dealer",
            "address": "Shivajinagar",
            "city": "Pune",
            "state": "Maharashtra",
            "phone": "+91-20-12345678",
        },
        keyword="teak",
    )
    assert ok is True
    db.commit()
    from app.models.models import Supplier
    sup = db.query(Supplier).filter_by(name="Deccan Timber Depot").first()
    assert sup is not None
    assert sup.city == "Pune"
    assert sup.state == "Maharashtra"
    assert sup.verification_status == "POTENTIAL_GOOGLE_PLACE"


def test_execute_daily_collection_task_honors_budget_and_non_destructive(db):
    with patch("app.services.daily_collection_service.SessionLocal", return_value=db), \
         patch("app.services.daily_collection_service.is_socialcrawl_configured", return_value=False), \
         patch("app.services.pinterest_service.search_pinterest_page", return_value={"items": []}):
        res = execute_daily_collection_task(force=True, max_items=3)
    assert res["budget_limit"] == 3
    assert res["calls_made"] <= 3
    assert res["status"] in ("Completed", "Partially completed")


import pytest
from app.schemas.schemas import SourcingSearchQuery
from app.services.sourcing_service import execute_hierarchical_sourcing

def test_kochi_local_search_level0(db):
    """Kochi search finds local suppliers in Level 0 with actual km distance display."""
    query = SourcingSearchQuery(query="Apex Ultima", city="Kochi", initial_radius_km=25.0)
    res = execute_hierarchical_sourcing(db, query)
    assert len(res.levels_traversed) == 4

    lvl0 = res.levels_traversed[0]
    assert lvl0.level == 0
    assert len(lvl0.suppliers) >= 1
    assert any("Malabar Paint" in s.supplier_name for s in lvl0.suppliers)

    malabar = next(s for s in lvl0.suppliers if "Malabar Paint" in s.supplier_name)
    assert malabar.city == "Kochi"
    assert "km" in malabar.distance_display

def test_kanyakumari_border_search_level1_includes_trivandrum(db):
    """
    Searching from Kanyakumari includes adjacent border district Trivandrum
    (e.g., Travancore Architectural Clay) in Level 1 because it is within the 60km border corridor.
    """
    query = SourcingSearchQuery(query="Porotherm", city="Kanyakumari", initial_radius_km=25.0)
    res = execute_hierarchical_sourcing(db, query)
    assert len(res.levels_traversed) == 4

    lvl1 = res.levels_traversed[1]
    assert lvl1.level == 1
    found_names = [s.supplier_name for s in lvl1.suppliers]
    assert any("Travancore" in name for name in found_names), f"Travancore not found in Level 1: {found_names}"

    travancore = next(s for s in lvl1.suppliers if "Travancore" in s.supplier_name)
    assert travancore.city in ("Trivandrum", "Thiruvananthapuram")

def test_kyoto_supplier_appears_only_at_level3(db):
    """International suppliers (Kyoto in Japan) appear strictly in Level 3."""
    query = SourcingSearchQuery(query="Japanese Stepping Stones", city="Kochi")
    res = execute_hierarchical_sourcing(db, query)
    assert len(res.levels_traversed) == 4

    # Must NOT be in Level 0, 1, or 2
    for lvl_idx in (0, 1, 2):
        names = [s.supplier_name for s in res.levels_traversed[lvl_idx].suppliers]
        assert not any("Kyoto" in n for n in names), f"Kyoto unexpectedly found in Level {lvl_idx}"

    # Must be in Level 3
    lvl3 = res.levels_traversed[3]
    assert lvl3.level == 3
    assert any("Kyoto" in s.supplier_name for s in lvl3.suppliers)
    kyoto = next(s for s in lvl3.suppliers if "Kyoto" in s.supplier_name)
    assert kyoto.country == "Japan"
    assert "International:" in kyoto.distance_display or "Japan" in kyoto.distance_display

def test_deduplication_across_all_levels(db):
    """Every supplier appears at most once across the 4 fallback levels."""
    query = SourcingSearchQuery(city="Kochi")
    res = execute_hierarchical_sourcing(db, query)
    seen_ids = set()
    for lvl in res.levels_traversed:
        for sup in lvl.suppliers:
            assert sup.supplier_id not in seen_ids, f"Supplier {sup.supplier_name} (ID: {sup.supplier_id}) duplicated in Level {lvl.level}"
            seen_ids.add(sup.supplier_id)

def test_distance_display_format_per_level(db):
    """
    Distance display format:
    - Levels 0-1 show actual distance in km.
    - Level 2+ shows scope label (e.g. 'Neighbouring State: Tamil Nadu' or 'National:' / 'International:').
    """
    query = SourcingSearchQuery(city="Kochi")
    res = execute_hierarchical_sourcing(db, query)

    # Check Level 0 and 1
    for lvl in res.levels_traversed[:2]:
        for sup in lvl.suppliers:
            if sup.distance_km is not None:
                assert "km" in sup.distance_display, f"Level {lvl.level} supplier {sup.supplier_name} lacks km in distance_display: {sup.distance_display}"

    # Check Level 2
    lvl2 = res.levels_traversed[2]
    for sup in lvl2.suppliers:
        assert ("Neighbouring State:" in sup.distance_display) or ("State-wide:" in sup.distance_display), \
            f"Level 2 supplier {sup.supplier_name} has invalid display: {sup.distance_display}"

    # Check Level 3
    lvl3 = res.levels_traversed[3]
    for sup in lvl3.suppliers:
        assert ("National:" in sup.distance_display) or ("International:" in sup.distance_display), \
            f"Level 3 supplier {sup.supplier_name} has invalid display: {sup.distance_display}"

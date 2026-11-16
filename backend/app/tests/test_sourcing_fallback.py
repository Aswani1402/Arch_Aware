import pytest
from app.schemas.schemas import SourcingSearchQuery
from app.services.sourcing_service import execute_hierarchical_sourcing

def test_hierarchical_sourcing_kochi(db):
    # Searching for Apex Ultima from Kochi, Kerala
    query = SourcingSearchQuery(query="Apex Ultima", city="Kochi", initial_radius_km=25.0)
    data = execute_hierarchical_sourcing(db, query)
    assert data.total_suppliers_found >= 2
    assert len(data.levels_traversed) == 4  # Level 0 to 3

    # Level 0 (within 25km of Kochi) should include Malabar Paint
    lvl0 = data.levels_traversed[0]
    assert lvl0.level == 0
    assert len(lvl0.suppliers) >= 1
    assert any("Malabar Paint" in s.supplier_name for s in lvl0.suppliers)

    # Level 2 (Neighbouring state: Tamil Nadu, Coimbatore) should include Deccan Architectural
    lvl2 = data.levels_traversed[2]
    assert lvl2.level == 2
    assert any("Deccan Architectural" in s.supplier_name for s in lvl2.suppliers)

def test_international_sourcing_kyoto(db):
    # Searching for Japanese stone from Kochi
    query = SourcingSearchQuery(query="Japanese Stepping Stones", city="Kochi")
    data = execute_hierarchical_sourcing(db, query)
    # Level 3 is international (Kyoto, Japan)
    lvl3 = data.levels_traversed[3]
    assert lvl3.level == 3
    assert len(lvl3.suppliers) >= 1
    assert any(s.country == "Japan" for s in lvl3.suppliers)

def test_deduplication_across_levels(db):
    query = SourcingSearchQuery(city="Kochi")
    data = execute_hierarchical_sourcing(db, query)
    seen_ids = set()
    for level in data.levels_traversed:
        for sup in level.suppliers:
            assert sup.supplier_id not in seen_ids, f"Duplicate supplier {sup.supplier_name} found in level {level.level}"
            seen_ids.add(sup.supplier_id)

def test_nagercoil_local_sourcing(db):
    # Search for drainage slabs from Nagercoil
    query = SourcingSearchQuery(query="drainage", city="Nagercoil", initial_radius_km=25.0)
    data = execute_hierarchical_sourcing(db, query)
    assert data.total_suppliers_found >= 1

    # Level 0 (local Nagercoil within 25km) must include Cape Precast
    lvl0 = data.levels_traversed[0]
    assert any("Cape Precast" in s.supplier_name for s in lvl0.suppliers)
    cape_sup = next(s for s in lvl0.suppliers if "Cape Precast" in s.supplier_name)
    assert cape_sup.city == "Nagercoil"
    assert cape_sup.state == "Tamil Nadu"
    assert cape_sup.whatsapp is not None
    assert cape_sup.google_maps_url is not None

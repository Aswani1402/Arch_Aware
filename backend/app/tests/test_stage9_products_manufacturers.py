import pytest
from app.services.socialcrawl_service import normalize_google_shopping
from app.models.models import Supplier, Product, CatalogueMaterial
from app.services.sourcing_service import execute_hierarchical_sourcing
from app.schemas.schemas import SourcingSearchQuery

def test_shopping_never_creates_supplier_records(db):
    """Shopping items must strictly remain product listings and never create supplier records."""
    initial_supplier_count = db.query(Supplier).count()
    
    raw_shopping_item = {
        "product": {
            "id": "shop_test_123",
            "title": "UltraTech Super Cement 50kg Bag",
            "brand": "UltraTech",
            "price": {"current": 380, "currency": "INR"},
            "seller": "Cement Kart Online",
            "url": "https://example.com/cement"
        }
    }
    norm = normalize_google_shopping(raw_shopping_item)
    assert norm["title"] == "UltraTech Super Cement 50kg Bag"
    assert norm["brand"] == "UltraTech"
    assert norm["seller"] == "Cement Kart Online"
    assert norm["price"] == 380
    assert norm["currency"] == "INR"
    
    # Assert supplier count has not increased
    final_supplier_count = db.query(Supplier).count()
    assert final_supplier_count == initial_supplier_count, "Shopping normalization must never create supplier rows in DB"

def test_seller_separated_from_manufacturer():
    """Verify that seller/merchant is never confused with manufacturer."""
    raw_item = {
        "product": {
            "id": "p_separate_1",
            "title": "Jaquar Florentine Basin Mixer",
            "brand": "Jaquar",
            "seller": "Sanitary Mall India",
            "manufacturer": "Jaquar & Company Pvt. Ltd."
        }
    }
    norm = normalize_google_shopping(raw_item)
    assert norm["seller"] == "Sanitary Mall India"
    assert norm["brand"] == "Jaquar"
    assert norm["seller"] != raw_item["product"].get("manufacturer")

def test_unknown_product_fields_remain_blank():
    """Unknown specifications, seller, or brand must remain None, never fabricated."""
    minimal_item = {
        "product": {
            "id": "min_1",
            "title": "Custom Wirecut Brick Batch"
        }
    }
    norm = normalize_google_shopping(minimal_item)
    assert norm["title"] == "Custom Wirecut Brick Batch"
    assert norm["brand"] is None
    assert norm["seller"] is None
    assert norm["price"] is None
    assert norm["currency"] is None

def test_shopping_products_never_returned_as_vendors(db):
    """Shopping items should never be surfaced in hierarchical vendor search."""
    query = SourcingSearchQuery(query="Cement", city="Kochi")
    res = execute_hierarchical_sourcing(db, query)
    
    for lvl in res.levels_traversed:
        for s in lvl.suppliers:
            assert "Google Shopping" not in s.supplier_name
            assert "Cement Kart Online" not in s.supplier_name

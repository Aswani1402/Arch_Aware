import pytest
from app.models.models import Supplier, SupplierMaterialEvidence, Product, SupplierProduct
from app.services.sourcing_service import (
    normalize_business_type_label,
    classify_supplier_match,
    execute_hierarchical_sourcing
)
from app.schemas.schemas import SourcingSearchQuery

def test_dealer_never_labeled_manufacturer():
    """Verify that dealer / distributor business types are never labeled manufacturer."""
    assert normalize_business_type_label("dealer") == "Dealer"
    assert normalize_business_type_label("authorized_dealer") == "Dealer"
    assert normalize_business_type_label("retailer") == "Retailer"
    assert normalize_business_type_label("distributor") == "Distributor"
    assert normalize_business_type_label("authorized_distributor") == "Authorized Distributor"
    assert normalize_business_type_label("contractor") == "Contractor / Service"
    assert normalize_business_type_label("manufacturer") == "Manufacturer"
    assert normalize_business_type_label("unknown_type") == "Supplier"

def test_whatsapp_validation_filtering(db):
    """WhatsApp is only provided when a valid 10+ digit number exists."""
    sup_with_valid_wa = Supplier(
        name="Valid WA Supplier",
        slug="valid-wa-supplier-test",
        address="123 Market Road",
        business_type="dealer",
        city="Kochi",
        state="Kerala",
        country="India",
        whatsapp="+91 98460 12345",
        materials_sold="Fly Ash Bricks"
    )
    sup_with_invalid_wa = Supplier(
        name="Invalid WA Supplier",
        slug="invalid-wa-supplier-test",
        address="456 Station Road",
        business_type="dealer",
        city="Kochi",
        state="Kerala",
        country="India",
        whatsapp="123",
        materials_sold="Fly Ash Bricks"
    )
    sup_with_none_wa = Supplier(
        name="None WA Supplier",
        slug="none-wa-supplier-test",
        address="789 Ring Road",
        business_type="dealer",
        city="Kochi",
        state="Kerala",
        country="India",
        whatsapp=None,
        materials_sold="Fly Ash Bricks"
    )
    db.add_all([sup_with_valid_wa, sup_with_invalid_wa, sup_with_none_wa])
    db.commit()

    query = SourcingSearchQuery(query="Fly Ash Bricks", city="Kochi")
    res = execute_hierarchical_sourcing(db, query)
    
    all_sups = []
    for lvl in res.levels_traversed:
        all_sups.extend(lvl.suppliers)

    wa_map = {s.supplier_name: s.whatsapp for s in all_sups}
    assert "Valid WA Supplier" in wa_map
    assert wa_map["Valid WA Supplier"] is not None
    assert "+919846012345" in wa_map["Valid WA Supplier"].replace(" ", "")

    assert "Invalid WA Supplier" in wa_map
    assert wa_map["Invalid WA Supplier"] is None

    assert "None WA Supplier" in wa_map
    assert wa_map["None WA Supplier"] is None

def test_verified_supplier_without_evidence_excluded(db):
    """A verified supplier with NO evidence for the queried material is excluded."""
    # Supplier 1: Verified, but only sells Teak Wood
    sup_verified_wrong_mat = Supplier(
        name="Elite Timber Traders",
        slug="elite-timber-traders-test",
        address="Kaloor Junction",
        verification_status="verified",
        business_type="distributor",
        city="Kochi",
        state="Kerala",
        country="India",
        materials_sold="Teak Wood, Rosewood, Plywood"
    )
    # Supplier 2: Verified, has additive SupplierMaterialEvidence for Concrete Pavers
    sup_with_evidence = Supplier(
        name="Precision Paver Works",
        slug="precision-paver-works-test",
        address="Edappally Industrial Zone",
        verification_status="verified",
        business_type="manufacturer",
        city="Kochi",
        state="Kerala",
        country="India",
        materials_sold="Concrete Pavers, Kerb Stones"
    )
    db.add_all([sup_verified_wrong_mat, sup_with_evidence])
    db.commit()

    ev = SupplierMaterialEvidence(
        supplier_id=sup_with_evidence.id,
        evidence_type="supplier_declared",
        evidence_text="Concrete Pavers interlock 80mm heavy duty",
        source_url="https://precisionpavers.example.com",
        strength=1.0
    )
    db.add(ev)
    db.commit()

    # Search for Concrete Pavers
    query = SourcingSearchQuery(query="Concrete Pavers", city="Kochi")
    res = execute_hierarchical_sourcing(db, query)
    found_names = [s.supplier_name for lvl in res.levels_traversed for s in lvl.suppliers]

    assert "Precision Paver Works" in found_names
    assert "Elite Timber Traders" not in found_names

def test_no_token_splitting_accidental_match(db):
    """Token splitting should not match unrelated materials (e.g. 'Red Clay' vs 'Red Granite')."""
    sup_granite = Supplier(
        name="Ruby Granite World",
        slug="ruby-granite-world-test",
        address="Vyttila Bypass",
        verification_status="verified",
        business_type="dealer",
        city="Kochi",
        state="Kerala",
        country="India",
        materials_sold="Red Granite Slabs, Black Galaxy Granite"
    )
    db.add(sup_granite)
    db.commit()

    # Query: 'Clay Brick' - should NOT match just because 'Red' is common
    query = SourcingSearchQuery(query="Clay Brick", city="Kochi")
    res = execute_hierarchical_sourcing(db, query)
    found_names = [s.supplier_name for lvl in res.levels_traversed for s in lvl.suppliers]
    assert "Ruby Granite World" not in found_names

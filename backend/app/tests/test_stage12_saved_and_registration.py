import pytest
from app.models.models import User, SavedItem, Supplier, SupplierMaterialEvidence, ArchitecturalReference
from app.schemas.schemas import SupplierRegister
from app.api.suppliers import register_supplier

def test_supplier_registration_starts_as_pending_review(db):
    """Supplier registration starts strictly in PENDING_REVIEW status."""
    reg = SupplierRegister(
        name="Horizon Glass & Glazing",
        business_type="contractor",
        contact_person="Ramesh Menon",
        address="34 Marine Drive",
        city="Kochi",
        state="Kerala",
        email="ramesh@horizonglass.example.com",
        phone="+91 98470 11223",
        whatsapp="+91 98470 11223",
        materials_sold="Toughened Glass, Spider Glazing, Aluminium Facades"
    )
    sup = register_supplier(reg, db)
    assert sup.id is not None
    assert sup.verification_status == "PENDING_REVIEW"
    assert sup.name == "Horizon Glass & Glazing"
    assert sup.materials_sold == "Toughened Glass, Spider Glazing, Aluminium Facades"

    # Verify supplier_declared material evidence was created
    evidences = db.query(SupplierMaterialEvidence).filter_by(supplier_id=sup.id).all()
    assert len(evidences) == 3
    for ev in evidences:
        assert ev.evidence_type == "supplier_declared"
        assert ev.strength == 0.7
    ev_texts = [e.evidence_text for e in evidences]
    assert "Toughened Glass" in ev_texts
    assert "Spider Glazing" in ev_texts

def test_saved_inspiration_and_vendor_isolation(db):
    """Saved items store references and suppliers independently, preserving all records."""
    # Find or create a test user
    test_user = db.query(User).first()
    assert test_user is not None

    initial_saved_count = db.query(SavedItem).filter_by(user_id=test_user.id).count()

    # Save a reference
    ref = db.query(ArchitecturalReference).first()
    assert ref is not None
    saved_ref = SavedItem(
        user_id=test_user.id,
        item_type="reference",
        reference_id=ref.id
    )
    db.add(saved_ref)
    db.commit()

    # Save a supplier
    sup = db.query(Supplier).first()
    assert sup is not None
    saved_sup = SavedItem(
        user_id=test_user.id,
        item_type="supplier",
        supplier_id=sup.id
    )
    db.add(saved_sup)
    db.commit()

    user_saved = db.query(SavedItem).filter_by(user_id=test_user.id).all()
    assert len(user_saved) == initial_saved_count + 2

    saved_types = [item.item_type for item in user_saved]
    assert "reference" in saved_types
    assert "supplier" in saved_types

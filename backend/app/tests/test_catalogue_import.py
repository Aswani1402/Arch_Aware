"""
Phase 2 Tests — Master Material Catalogue CSV Import, Idempotency & Reconciliation
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
import app.models.models  # noqa: F401
from app.models.models import (
    ArchitecturalReference,
    CatalogueCategory,
    CatalogueImportRun,
    CatalogueMaterial,
    CatalogueSubcategory,
    Product,
    SavedItem,
    Supplier,
    User,
)
from app.services.catalogue_import_service import (
    DEFAULT_CATALOGUE_CSV_PATH,
    get_catalogue_summary,
    get_catalogue_tree,
    import_catalogue_csv,
    search_catalogue_materials,
    validate_catalogue_csv,
)


def test_csv_source_integrity_and_exact_counts():
    assert DEFAULT_CATALOGUE_CSV_PATH.exists(), f"Missing canonical CSV at {DEFAULT_CATALOGUE_CSV_PATH}"
    rows, summary = validate_catalogue_csv(DEFAULT_CATALOGUE_CSV_PATH)
    assert len(rows) == 6319
    assert summary["total_csv_rows"] == 6319
    assert summary["categories_count"] == 10
    assert summary["subcategories_count"] == 184
    assert summary["distinct_materials_count"] == 5932


def test_catalogue_import_idempotency_and_non_destructive_preservation():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        # Seed existing unrelated records to guarantee non-destructive preservation
        u = User(email="keep@nivora.app", hashed_password="x", role="user")
        sup = Supplier(name="Keep Timber Depot", slug="keep-timber", address="MG Road", city="Kochi", state="Kerala")
        prod = Product(name="Keep Product", slug="keep-prod")
        ref = ArchitecturalReference(
            title="Keep Villa",
            slug="keep-villa",
            source_platform="pinterest",
            source_url="https://example.com/keep-villa",
        )
        db.add_all([u, sup, prod, ref])
        db.commit()
        db.refresh(u)
        db.refresh(ref)
        saved = SavedItem(user_id=u.id, item_type="reference", reference_id=ref.id)
        db.add(saved)
        db.commit()

        # Run 1: Initial import
        report1 = import_catalogue_csv(db)
        assert report1["total_csv_rows"] == 6319
        assert report1["inserted_rows"] == 6319
        assert report1["updated_rows"] == 0
        assert report1["skipped_rows"] == 0
        assert report1["db_categories_count"] == 10
        assert report1["db_subcategories_count"] == 184
        assert report1["db_materials_count"] == 6319
        assert report1["db_distinct_materials_count"] == 5932

        # Run 2: Re-run must be strictly idempotent (0 new inserts, exact same counts)
        report2 = import_catalogue_csv(db)
        assert report2["inserted_rows"] == 0
        assert report2["updated_rows"] == 0
        assert report2["skipped_rows"] == 6319
        assert report2["db_categories_count"] == 10
        assert report2["db_subcategories_count"] == 184
        assert report2["db_materials_count"] == 6319
        assert report2["db_distinct_materials_count"] == 5932
        assert db.query(CatalogueImportRun).count() == 2

        # Existing records untouched
        assert db.query(User).count() == 1
        assert db.query(Supplier).count() == 1
        assert db.query(Product).count() == 1
        assert db.query(ArchitecturalReference).count() == 1
        assert db.query(SavedItem).count() == 1

        # Search and category hierarchy checks
        res = search_catalogue_materials(db, q="AAC", category="Exterior")
        assert res["total"] >= 0
        res_all = search_catalogue_materials(db, q="AAC")
        assert res_all["total"] >= 1

        tree = get_catalogue_tree(db, include_materials=False)
        assert tree["total_categories"] == 10
        assert tree["total_subcategories"] == 184
        assert tree["total_materials"] == 6319
        cat_names = {c["name"] for c in tree["categories"]}
        assert "Healthcare & Hospital" in cat_names
        assert "Machinery & Tools" in cat_names
        assert "MEP & Building Services" in cat_names
    finally:
        db.close()
        engine.dispose()


def test_catalogue_api_endpoints(client, db):
    import_catalogue_csv(db)
    sum_res = client.get("/api/categories/catalogue/summary")
    assert sum_res.status_code == 200
    s = sum_res.json()
    assert s["categories_count"] == 10
    assert s["subcategories_count"] == 184
    assert s["materials_count"] == 6319

    tree_res = client.get("/api/categories/catalogue/tree")
    assert tree_res.status_code == 200
    assert tree_res.json()["total_categories"] == 10

    search_res = client.get("/api/categories/catalogue/search?q=Marble&limit=10")
    assert search_res.status_code == 200
    data = search_res.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


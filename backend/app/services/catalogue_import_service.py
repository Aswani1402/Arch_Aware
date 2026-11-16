"""
Nivora — Master CSV Material Catalogue Import & Search Service (Phase 2)

Safely imports all 6,319 rows (10 categories, 184 subcategories, 5,932 distinct material names)
from Construction_Materials_Products_Machinery_Catalogue_Clean(2).csv into additive SQLite tables
without deleting or mutating existing Seed/Saved/Reference/Supplier records.
"""

import csv
import hashlib
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.models import (
    CatalogueCategory,
    CatalogueImportRun,
    CatalogueMaterial,
    CatalogueSubcategory,
)

DEFAULT_CATALOGUE_CSV_PATH = (
    Path(__file__).resolve().parent.parent
    / "db"
    / "data"
    / "Construction_Materials_Products_Machinery_Catalogue_Clean(2).csv"
)

# Explicit reconciliation map linking the 10 authoritative CSV categories to Nivora Keyword Explorer domains.
CSV_CATEGORY_EXPLORER_MAP: Dict[str, Dict[str, str]] = {
    "Exterior": {
        "explorer_slug": "exterior-architecture",
        "explorer_name": "Exterior & Facade Architecture",
        "description": "Building envelopes, facade systems, roofing, external walls, cladding, and outdoor structures.",
    },
    "Interior": {
        "explorer_slug": "interior-design",
        "explorer_name": "Interior Architecture & Surfaces",
        "description": "Interior finishes, flooring, ceilings, partitions, cabinetry, joinery, and room treatments.",
    },
    "Machinery & Tools": {
        "explorer_slug": "machinery-tools",
        "explorer_name": "Construction Machinery & Tools",
        "description": "Site equipment, earthmoving plant, concreting machinery, cutting tools, scaffolding, and formwork.",
    },
    "MEP & Building Services": {
        "explorer_slug": "mep-building-services",
        "explorer_name": "MEP, Plumbing & Electrical Services",
        "description": "Mechanical, electrical, plumbing, HVAC, fire protection, automation, and building utilities.",
    },
    "Materials, Metals, Timber & Chemicals": {
        "explorer_slug": "construction-materials",
        "explorer_name": "Core Construction Materials, Metals, Timber & Chemicals",
        "description": "Structural steel, cement, aggregates, timber, glass, adhesives, admixtures, and waterproofing.",
    },
    "Industrial, Commercial & Institutional": {
        "explorer_slug": "industrial-commercial",
        "explorer_name": "Industrial, Commercial & Institutional",
        "description": "Specialized assemblies and equipment for warehouses, factories, retail, hospitality, and institutions.",
    },
    "Healthcare & Hospital": {
        "explorer_slug": "healthcare-hospital",
        "explorer_name": "Healthcare & Hospital Infrastructure",
        "description": "Medical gas systems, cleanroom partitions, antibacterial flooring, OT panels, and clinical fixtures.",
    },
    "Water, Waste, Landscape & External Utilities": {
        "explorer_slug": "landscape-external-utilities",
        "explorer_name": "Water, Waste, Landscape & External Utilities",
        "description": "STP/ETP treatment, stormwater drainage, irrigation, softscape, hardscape, and external site networks.",
    },
    "Doors, Windows, Hardware & Fixtures": {
        "explorer_slug": "doors-windows-glass",
        "explorer_name": "Doors, Windows, Hardware & Architectural Fixtures",
        "description": "Door assemblies, fenestration systems, ironmongery, locks, hinges, glazing hardware, and fittings.",
    },
    "Safety, Security & Site Welfare": {
        "explorer_slug": "safety-security-welfare",
        "explorer_name": "Safety, Security & Site Welfare",
        "description": "PPE, fire safety gear, fall protection, access control, site barriers, and worker welfare facilities.",
    },
}


def slugify_label(value: str) -> str:
    """Create a deterministic URL-safe lowercase slug."""
    cleaned = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return cleaned or "item"


def normalize_material_name(value: str) -> str:
    """Normalize material label for case-insensitive matching and deduplication."""
    return re.sub(r"\s+", " ", (value or "").strip()).lower()


def ensure_catalogue_tables(db: Session) -> None:
    """Create additive catalogue tables if missing without touching existing tables."""
    bind = db.get_bind()
    for model_cls in (
        CatalogueCategory,
        CatalogueSubcategory,
        CatalogueMaterial,
        CatalogueImportRun,
    ):
        model_cls.__table__.create(bind=bind, checkfirst=True)


def validate_catalogue_csv(
    csv_path: Optional[Path] = None,
) -> Tuple[List[Tuple[int, str, str, str]], Dict[str, Any]]:
    """
    Read and strictly validate the CSV catalogue rows.
    Rejects missing headers or blank cells cleanly and computes exact metrics.
    """
    resolved_path = Path(csv_path or DEFAULT_CATALOGUE_CSV_PATH)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Catalogue CSV not found at: {resolved_path}")

    raw_bytes = resolved_path.read_bytes()
    file_sha256 = hashlib.sha256(raw_bytes).hexdigest()

    rows: List[Tuple[int, str, str, str]] = []
    categories = set()
    subcat_pairs = set()
    distinct_materials = set()
    blank_rows = 0

    with resolved_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        expected = ["Category", "Subcategory", "Material"]
        if not reader.fieldnames or [c.strip() for c in reader.fieldnames] != expected:
            raise ValueError(
                f"Invalid CSV headers {reader.fieldnames}; expected {expected}"
            )
        for line_num, record in enumerate(reader, start=2):
            cat = (record.get("Category") or "").strip()
            subcat = (record.get("Subcategory") or "").strip()
            mat = (record.get("Material") or "").strip()
            if not cat or not subcat or not mat:
                blank_rows += 1
                continue
            rows.append((line_num, cat, subcat, mat))
            categories.add(cat)
            subcat_pairs.add((cat, subcat))
            distinct_materials.add(mat)

    if blank_rows > 0:
        raise ValueError(f"Catalogue CSV contains {blank_rows} row(s) with blank fields.")

    summary = {
        "source_filename": resolved_path.name,
        "file_sha256": file_sha256,
        "total_csv_rows": len(rows),
        "categories_count": len(categories),
        "subcategories_count": len(subcat_pairs),
        "distinct_materials_count": len(distinct_materials),
    }
    return rows, summary


def import_catalogue_csv(
    db: Session,
    csv_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Idempotently import/reconcile all CSV catalogue rows into SQLite.
    Safe to run multiple times without creating duplicate records or mutating unrelated tables.
    """
    ensure_catalogue_tables(db)
    rows, summary = validate_catalogue_csv(csv_path)

    existing_cats: Dict[str, CatalogueCategory] = {
        c.name: c for c in db.query(CatalogueCategory).all()
    }
    existing_subcats: Dict[Tuple[int, str], CatalogueSubcategory] = {
        (s.category_id, s.name): s for s in db.query(CatalogueSubcategory).all()
    }
    seen_subcat_keys = {s.category_subcategory_key for s in existing_subcats.values()}
    existing_materials: Dict[Tuple[int, str], CatalogueMaterial] = {
        (m.subcategory_id, m.name): m for m in db.query(CatalogueMaterial).all()
    }

    inserted_rows = 0
    updated_rows = 0
    skipped_rows = 0
    cat_order_counter = len(existing_cats)
    seen_slugs_cat = {c.slug for c in existing_cats.values()}

    for line_num, cat_name, subcat_name, mat_name in rows:
        cat_obj = existing_cats.get(cat_name)
        meta = CSV_CATEGORY_EXPLORER_MAP.get(cat_name, {})
        if not cat_obj:
            cat_order_counter += 1
            base_slug = slugify_label(cat_name)
            cat_slug = base_slug
            suffix = 2
            while cat_slug in seen_slugs_cat:
                cat_slug = f"{base_slug}-{suffix}"
                suffix += 1
            seen_slugs_cat.add(cat_slug)
            cat_obj = CatalogueCategory(
                name=cat_name,
                slug=cat_slug,
                explorer_category_slug=meta.get("explorer_slug"),
                explorer_category_name=meta.get("explorer_name"),
                description=meta.get("description"),
                display_order=cat_order_counter,
            )
            db.add(cat_obj)
            db.flush()
            existing_cats[cat_name] = cat_obj
        else:
            if meta.get("explorer_slug") and cat_obj.explorer_category_slug != meta.get("explorer_slug"):
                cat_obj.explorer_category_slug = meta.get("explorer_slug")
                cat_obj.explorer_category_name = meta.get("explorer_name")
                cat_obj.description = meta.get("description")

        sub_key = (cat_obj.id, subcat_name)
        sub_obj = existing_subcats.get(sub_key)
        if not sub_obj:
            sub_slug = slugify_label(subcat_name)
            composite_key = f"{cat_obj.slug}::{sub_slug}"
            suffix = 2
            while composite_key in seen_subcat_keys:
                composite_key = f"{cat_obj.slug}::{sub_slug}-{suffix}"
                suffix += 1
            seen_subcat_keys.add(composite_key)
            sub_obj = CatalogueSubcategory(
                category_id=cat_obj.id,
                name=subcat_name,
                slug=sub_slug,
                category_subcategory_key=composite_key,
            )
            db.add(sub_obj)
            db.flush()
            existing_subcats[sub_key] = sub_obj

        mat_key = (sub_obj.id, mat_name)
        norm_name = normalize_material_name(mat_name)
        mat_obj = existing_materials.get(mat_key)
        if not mat_obj:
            mat_obj = CatalogueMaterial(
                category_id=cat_obj.id,
                subcategory_id=sub_obj.id,
                name=mat_name,
                slug=slugify_label(mat_name),
                normalized_name=norm_name,
                source_row_number=line_num,
                source_dataset=summary["source_filename"],
                is_active=True,
            )
            db.add(mat_obj)
            existing_materials[mat_key] = mat_obj
            inserted_rows += 1
        else:
            changed = False
            if mat_obj.source_row_number != line_num:
                mat_obj.source_row_number = line_num
                changed = True
            if mat_obj.normalized_name != norm_name:
                mat_obj.normalized_name = norm_name
                changed = True
            if changed:
                updated_rows += 1
            else:
                skipped_rows += 1

    import_run = CatalogueImportRun(
        source_filename=summary["source_filename"],
        file_sha256=summary["file_sha256"],
        total_csv_rows=summary["total_csv_rows"],
        inserted_rows=inserted_rows,
        updated_rows=updated_rows,
        skipped_rows=skipped_rows,
        categories_count=len(existing_cats),
        subcategories_count=len(existing_subcats),
        distinct_materials_count=summary["distinct_materials_count"],
        status="COMPLETED",
        notes=(
            f"Inserted={inserted_rows}, Updated={updated_rows}, Skipped={skipped_rows}. "
            "All existing application tables preserved."
        ),
    )
    db.add(import_run)
    db.commit()

    db_totals = get_catalogue_summary(db)
    return {
        **summary,
        "inserted_rows": inserted_rows,
        "updated_rows": updated_rows,
        "skipped_rows": skipped_rows,
        "db_categories_count": db_totals["categories_count"],
        "db_subcategories_count": db_totals["subcategories_count"],
        "db_materials_count": db_totals["materials_count"],
        "db_distinct_materials_count": db_totals["distinct_materials_count"],
        "by_category": db_totals["by_category"],
    }


def get_catalogue_summary(db: Session) -> Dict[str, Any]:
    """Return authoritative database counts for the imported CSV catalogue."""
    ensure_catalogue_tables(db)
    cats = db.query(CatalogueCategory).order_by(CatalogueCategory.display_order.asc(), CatalogueCategory.id.asc()).all()
    subcats_count = db.query(CatalogueSubcategory).count()
    materials_count = db.query(CatalogueMaterial).count()
    distinct_count = db.query(func.count(func.distinct(CatalogueMaterial.name))).scalar() or 0

    by_category = []
    for c in cats:
        sub_cnt = db.query(CatalogueSubcategory).filter_by(category_id=c.id).count()
        mat_cnt = db.query(CatalogueMaterial).filter_by(category_id=c.id).count()
        by_category.append(
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "explorer_category_slug": c.explorer_category_slug,
                "explorer_category_name": c.explorer_category_name,
                "subcategories_count": sub_cnt,
                "materials_count": mat_cnt,
            }
        )

    return {
        "categories_count": len(cats),
        "subcategories_count": subcats_count,
        "materials_count": materials_count,
        "distinct_materials_count": distinct_count,
        "by_category": by_category,
    }


def get_catalogue_tree(db: Session, include_materials: bool = False) -> Dict[str, Any]:
    """Return full 10-category -> 184-subcategory -> materials hierarchy."""
    ensure_catalogue_tables(db)
    cats = db.query(CatalogueCategory).order_by(CatalogueCategory.display_order.asc(), CatalogueCategory.id.asc()).all()
    tree = []
    for cat in cats:
        subs_out = []
        for sub in cat.subcategories:
            mat_query = db.query(CatalogueMaterial).filter_by(subcategory_id=sub.id).order_by(CatalogueMaterial.id.asc())
            sub_entry: Dict[str, Any] = {
                "id": sub.id,
                "name": sub.name,
                "slug": sub.slug,
                "materials_count": mat_query.count(),
            }
            if include_materials:
                sub_entry["materials"] = [
                    {"id": m.id, "name": m.name, "slug": m.slug}
                    for m in mat_query.all()
                ]
            subs_out.append(sub_entry)
        tree.append(
            {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "explorer_category_slug": cat.explorer_category_slug,
                "explorer_category_name": cat.explorer_category_name,
                "description": cat.description,
                "subcategories_count": len(subs_out),
                "materials_count": sum(s["materials_count"] for s in subs_out),
                "subcategories": subs_out,
            }
        )
    summary = get_catalogue_summary(db)
    return {
        "total_categories": summary["categories_count"],
        "total_subcategories": summary["subcategories_count"],
        "total_materials": summary["materials_count"],
        "distinct_materials_count": summary["distinct_materials_count"],
        "categories": tree,
    }


def search_catalogue_materials(
    db: Session,
    q: Optional[str] = None,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """Search across imported CSV catalogue materials, subcategories, and categories."""
    ensure_catalogue_tables(db)
    query = (
        db.query(CatalogueMaterial, CatalogueCategory, CatalogueSubcategory)
        .join(CatalogueCategory, CatalogueMaterial.category_id == CatalogueCategory.id)
        .join(CatalogueSubcategory, CatalogueMaterial.subcategory_id == CatalogueSubcategory.id)
    )

    if category and category.strip():
        cat_clean = category.strip().lower()
        query = query.filter(
            or_(
                func.lower(CatalogueCategory.slug) == cat_clean,
                func.lower(CatalogueCategory.name) == cat_clean,
                CatalogueCategory.name.ilike(f"%{category.strip()}%"),
                func.lower(CatalogueCategory.explorer_category_slug) == cat_clean,
            )
        )

    if subcategory and subcategory.strip():
        sub_clean = subcategory.strip().lower()
        query = query.filter(
            or_(
                func.lower(CatalogueSubcategory.slug) == sub_clean,
                func.lower(CatalogueSubcategory.name) == sub_clean,
                CatalogueSubcategory.name.ilike(f"%{subcategory.strip()}%"),
            )
        )

    if q and q.strip():
        q_clean = q.strip()
        pattern = f"%{q_clean}%"
        query = query.filter(
            or_(
                CatalogueMaterial.name.ilike(pattern),
                CatalogueSubcategory.name.ilike(pattern),
                CatalogueCategory.name.ilike(pattern),
            )
        )

    total = query.count()
    rows = query.order_by(CatalogueMaterial.id.asc()).offset(max(0, offset)).limit(max(1, min(limit, 500))).all()
    items = [
        {
            "id": mat.id,
            "material": mat.name,
            "slug": mat.slug,
            "category": cat.name,
            "category_slug": cat.slug,
            "explorer_category_slug": cat.explorer_category_slug,
            "subcategory": sub.name,
            "subcategory_slug": sub.slug,
            "source_row_number": mat.source_row_number,
        }
        for mat, cat, sub in rows
    ]
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }

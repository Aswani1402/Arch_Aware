from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db, Base
from app.models.models import MaterialCategory, Product, ArchitecturalReference, CustomKeyword
from app.schemas.schemas import CategoryOut, CategoryDetailOut

router = APIRouter(prefix="/categories", tags=["Material Categories"])

@router.get("", response_model=List[CategoryOut])
def get_categories(
    section: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(MaterialCategory)
    if section:
        query = query.filter(MaterialCategory.section_code == section.upper())
    return query.order_by(MaterialCategory.section_code.asc(), MaterialCategory.name.asc()).all()

from app.services.taxonomy_service import get_all_taxonomy_categories, match_query_to_taxonomy

@router.get("/taxonomy/tree")
def get_taxonomy_tree():
    """
    Returns the comprehensive 29-category architectural & construction taxonomy
    with subcategories, applications, IS standards, and sections.
    """
    return {
        "total_categories": 29,
        "taxonomy": get_all_taxonomy_categories()
    }

@router.get("/taxonomy/match")
def match_taxonomy(q: str):
    """
    Intent-aware taxonomy matcher for natural-language search queries.
    """
    return {
        "query": q,
        "matched_categories": match_query_to_taxonomy(q)
    }


@router.get("/catalogue/summary")
def get_master_catalogue_summary(db: Session = Depends(get_db)):
    """
    Returns counts and breakdown for the imported 6,319-row master material catalogue.
    """
    from app.services.catalogue_import_service import get_catalogue_summary
    return get_catalogue_summary(db)


@router.get("/catalogue/tree")
def get_master_catalogue_tree(
    include_materials: bool = False,
    db: Session = Depends(get_db)
):
    """
    Returns the complete CSV material catalogue hierarchy (10 categories -> 184 subcategories -> materials).
    """
    from app.services.catalogue_import_service import get_catalogue_tree
    return get_catalogue_tree(db, include_materials=include_materials)


@router.get("/catalogue/search")
def search_master_catalogue(
    q: Optional[str] = None,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Searches imported CSV catalogue materials by keyword, category, or subcategory.
    """
    from app.services.catalogue_import_service import search_catalogue_materials
    return search_catalogue_materials(
        db=db,
        q=q,
        category=category,
        subcategory=subcategory,
        limit=limit,
        offset=offset,
    )

@router.get("/{id_or_slug}", response_model=CategoryDetailOut)
def get_category_detail(id_or_slug: str, db: Session = Depends(get_db)):
    cat = None
    if id_or_slug.isdigit():
        cat = db.query(MaterialCategory).filter_by(id=int(id_or_slug)).first()
    if not cat:
        cat = db.query(MaterialCategory).filter_by(slug=id_or_slug).first()

    if not cat:
        raise HTTPException(status_code=404, detail="Material category not found")

    products = db.query(Product).filter_by(category_id=cat.id).all()
    references = db.query(ArchitecturalReference).filter_by(category_id=cat.id).limit(20).all()

    prods_out = [{
        "id": p.id,
        "name": p.name,
        "slug": p.slug,
        "material_type": p.material_type,
        "finish": p.finish,
        "dimensions": p.dimensions,
        "thickness": p.thickness,
        "manufacturer_name": p.manufacturer.name if p.manufacturer else "Not verified",
        "image_url": p.image_url,
        "verification_status": p.verification_status,
        "supplier_count": len(p.supplier_links)
    } for p in products]

    refs_out = [{
        "id": r.id,
        "title": r.title,
        "slug": r.slug,
        "source_platform": r.source_platform,
        "location_context": r.location_context,
        "country": r.country,
        "architectural_style": r.architectural_style,
        "thumbnail_url": r.thumbnail_url,
        "creator_name": r.creator_name or r.architect_name
    } for r in references]

    return CategoryDetailOut(
        id=cat.id,
        name=cat.name,
        slug=cat.slug,
        description=cat.description,
        image_url=cat.image_url,
        section_code=cat.section_code,
        section_name=cat.section_name,
        typical_applications=cat.typical_applications,
        subcategories=cat.subcategories,
        standards_compliance=cat.standards_compliance,
        products_count=len(products),
        references_count=len(references),
        products=prods_out,
        references=refs_out
    )


class CustomKeywordCreate(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=200)
    category_name: Optional[str] = Field(None, max_length=150)
    is_followed: bool = True


def _ensure_custom_keyword_table(db: Session) -> None:
    Base.metadata.create_all(bind=db.get_bind(), tables=[CustomKeyword.__table__], checkfirst=True)


@router.get("/keywords/library")
def get_keyword_library_endpoint():
    """
    Returns the complete 14 consolidated architectural categories (4-level hierarchy).
    """
    from app.services.keyword_library import get_all_keyword_groups
    return get_all_keyword_groups()


@router.get("/keywords/unified")
def get_unified_keyword_explorer(db: Session = Depends(get_db)):
    """
    Returns both the 14 consolidated architectural keyword categories and the 10-category CSV master catalogue tree.
    """
    from app.services.keyword_library import get_all_keyword_groups
    from app.services.catalogue_import_service import get_catalogue_tree
    _ensure_custom_keyword_table(db)
    custom_rows = db.query(CustomKeyword).order_by(CustomKeyword.created_at.desc()).all()
    return {
        "explorer_categories": get_all_keyword_groups(),
        "catalogue_tree": get_catalogue_tree(db, include_materials=False),
        "custom_keywords": [
            {
                "id": k.id,
                "keyword": k.keyword,
                "category_name": k.category_name,
                "is_followed": k.is_followed,
            }
            for k in custom_rows
        ],
    }


@router.get("/keywords/custom")
def list_custom_keywords(db: Session = Depends(get_db)):
    _ensure_custom_keyword_table(db)
    rows = db.query(CustomKeyword).order_by(CustomKeyword.created_at.desc()).all()
    return [
        {
            "id": k.id,
            "keyword": k.keyword,
            "category_name": k.category_name,
            "is_followed": k.is_followed,
        }
        for k in rows
    ]


@router.post("/keywords/custom")
def save_custom_keyword(payload: CustomKeywordCreate = Body(...), db: Session = Depends(get_db)):
    _ensure_custom_keyword_table(db)
    clean_kw = payload.keyword.strip()
    if not clean_kw:
        raise HTTPException(status_code=422, detail="Keyword cannot be empty.")
    existing = db.query(CustomKeyword).filter(CustomKeyword.keyword.ilike(clean_kw)).first()
    if existing:
        existing.is_followed = payload.is_followed
        if payload.category_name:
            existing.category_name = payload.category_name.strip()
        db.commit()
        db.refresh(existing)
        return {
            "id": existing.id,
            "keyword": existing.keyword,
            "category_name": existing.category_name,
            "is_followed": existing.is_followed,
        }
    row = CustomKeyword(
        keyword=clean_kw,
        category_name=payload.category_name.strip() if payload.category_name else None,
        is_followed=payload.is_followed,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "keyword": row.keyword,
        "category_name": row.category_name,
        "is_followed": row.is_followed,
    }


@router.delete("/keywords/custom/{keyword_id}")
def delete_custom_keyword(keyword_id: int, db: Session = Depends(get_db)):
    _ensure_custom_keyword_table(db)
    row = db.query(CustomKeyword).filter_by(id=keyword_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Custom keyword not found.")
    db.delete(row)
    db.commit()
    return {"deleted": True, "id": keyword_id}


@router.get("/keywords/search")
def search_keyword_library_endpoint(q: str, db: Session = Depends(get_db)):
    """
    Searches across the 14 consolidated architectural categories AND the 6,319-material CSV master catalogue.
    """
    from app.services.keyword_library import search_keyword_library, expand_search_query_with_synonyms
    from app.services.catalogue_import_service import search_catalogue_materials
    catalogue_hits = search_catalogue_materials(db, q=q, limit=25)
    return {
        "query": q,
        "synonyms": expand_search_query_with_synonyms(q),
        "results": search_keyword_library(q),
        "catalogue_results": catalogue_hits.get("items", []),
        "catalogue_total": catalogue_hits.get("total", 0),
    }


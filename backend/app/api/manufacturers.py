from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Manufacturer, Product, MaterialCategory
from app.schemas.schemas import ManufacturerOut, ManufacturerCreate, ProductOut

router = APIRouter(prefix="/manufacturers", tags=["Original Manufacturers"])

@router.get("", response_model=List[ManufacturerOut])
def get_manufacturers(
    country: Optional[str] = None,
    category: Optional[str] = None,
    verification_status: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Manufacturer)
    if country:
        query = query.filter(Manufacturer.country.ilike(f"%{country}%"))
    if verification_status:
        query = query.filter(Manufacturer.verification_status == verification_status)
    if category:
        # Filter manufacturers that produce items in this category
        cat = db.query(MaterialCategory).filter_by(slug=category).first()
        if cat:
            mfg_ids_with_cat = db.query(Product.manufacturer_id).filter(
                Product.category_id == cat.id,
                Product.manufacturer_id.isnot(None)
            ).distinct().all()
            mfg_ids = [m[0] for m in mfg_ids_with_cat if m[0] is not None]
            query = query.filter(Manufacturer.id.in_(mfg_ids))
    if q:
        query = query.filter(
            (Manufacturer.name.ilike(f"%{q}%")) |
            (Manufacturer.company_name.ilike(f"%{q}%")) |
            (Manufacturer.description.ilike(f"%{q}%"))
        )

    manufacturers = query.order_by(Manufacturer.name.asc()).all()
    results = []
    for m in manufacturers:
        m_out = ManufacturerOut.model_validate(m)
        m_out.products_count = len(m.products)
        results.append(m_out)
    return results

@router.get("/{id_or_slug}")
def get_manufacturer_detail(id_or_slug: str, db: Session = Depends(get_db)):
    mfg = None
    if id_or_slug.isdigit():
        mfg = db.query(Manufacturer).filter_by(id=int(id_or_slug)).first()
    if not mfg:
        mfg = db.query(Manufacturer).filter_by(slug=id_or_slug).first()

    if not mfg:
        raise HTTPException(status_code=404, detail="Manufacturer not found")

    products_out = []
    for p in mfg.products:
        products_out.append({
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "sku_code": p.sku_code,
            "product_type": p.product_type,
            "material_type": p.material_type,
            "category_name": p.category.name if p.category else None,
            "category_slug": p.category.slug if p.category else None,
            "image_url": p.image_url,
            "official_product_url": p.official_product_url,
            "verification_status": p.verification_status,
            "available_suppliers_count": len(p.supplier_links)
        })

    return {
        "id": mfg.id,
        "name": mfg.name,
        "company_name": mfg.company_name,
        "slug": mfg.slug,
        "country": mfg.country,
        "official_website": mfg.official_website,
        "official_catalog_url": mfg.official_catalog_url,
        "official_product_page_url": mfg.official_product_page_url,
        "official_video_channel_url": mfg.official_video_channel_url,
        "description": mfg.description,
        "logo_url": mfg.logo_url,
        "contact_info": mfg.contact_info,
        "verification_status": mfg.verification_status,
        "last_verified_at": mfg.last_verified_at,
        "source_url": mfg.source_url,
        "unverified_notes": mfg.unverified_notes,
        "created_at": mfg.created_at,
        "products_count": len(products_out),
        "products": products_out
    }

@router.post("", response_model=ManufacturerOut)
def create_manufacturer(
    mfg_in: ManufacturerCreate,
    db: Session = Depends(get_db)
):
    # Verify unique slug
    existing = db.query(Manufacturer).filter_by(slug=mfg_in.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Manufacturer slug already exists")

    new_mfg = Manufacturer(
        name=mfg_in.name,
        company_name=mfg_in.company_name,
        slug=mfg_in.slug,
        country=mfg_in.country,
        official_website=mfg_in.official_website,
        official_catalog_url=mfg_in.official_catalog_url,
        official_product_page_url=mfg_in.official_product_page_url,
        official_video_channel_url=mfg_in.official_video_channel_url,
        description=mfg_in.description,
        logo_url=mfg_in.logo_url,
        contact_info=mfg_in.contact_info,
        verification_status=mfg_in.verification_status or "MANUFACTURER_CONFIRMED",
        last_verified_at=datetime.now(timezone.utc),
        source_url=mfg_in.source_url,
        unverified_notes=mfg_in.unverified_notes
    )
    db.add(new_mfg)
    db.commit()
    db.refresh(new_mfg)
    out = ManufacturerOut.model_validate(new_mfg)
    out.products_count = 0
    return out

@router.put("/{mfg_id}", response_model=ManufacturerOut)
def update_manufacturer(
    mfg_id: int,
    updates: dict = Body(...),
    db: Session = Depends(get_db)
):
    mfg = db.query(Manufacturer).filter_by(id=mfg_id).first()
    if not mfg:
        raise HTTPException(status_code=404, detail="Manufacturer not found")

    allowed_fields = [
        "name", "company_name", "official_website", "official_catalog_url",
        "official_product_page_url", "official_video_channel_url", "description",
        "logo_url", "contact_info", "verification_status", "source_url", "unverified_notes"
    ]
    for key, val in updates.items():
        if key in allowed_fields:
            setattr(mfg, key, val)

    mfg.last_verified_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(mfg)
    out = ManufacturerOut.model_validate(mfg)
    out.products_count = len(mfg.products)
    return out

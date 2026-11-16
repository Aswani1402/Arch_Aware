from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.models.models import Product, Manufacturer, MaterialCategory, SupplierProduct, ArchitecturalReference, ReferenceProductMatch
from app.schemas.schemas import ProductOut, ProductDetailOut, ProductCreate, ManufacturerOut, CategoryOut, SupplierListingBrief

router = APIRouter(prefix="/products", tags=["Architectural Products"])

@router.get("", response_model=List[ProductOut])
def get_products(
    category: Optional[str] = None,
    material: Optional[str] = None,
    manufacturer: Optional[str] = None,
    sku: Optional[str] = None,
    finish: Optional[str] = None,
    product_type: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if category:
        cat = db.query(MaterialCategory).filter_by(slug=category).first()
        if cat:
            query = query.filter(Product.category_id == cat.id)

    if manufacturer:
        mfg = db.query(Manufacturer).filter_by(slug=manufacturer).first()
        if mfg:
            query = query.filter(Product.manufacturer_id == mfg.id)

    if sku:
        query = query.filter(Product.sku_code.ilike(f"%{sku}%"))

    if finish:
        query = query.filter(Product.finish.ilike(f"%{finish}%"))

    if product_type:
        query = query.filter(Product.product_type.ilike(f"%{product_type}%"))

    if material:
        query = query.filter(Product.material_type.ilike(f"%{material}%"))

    if q and q.strip():
        term = f"%{q.strip().lower()}%"
        query = query.filter(
            or_(
                Product.name.ilike(term),
                Product.sku_code.ilike(term),
                Product.product_type.ilike(term),
                Product.material_type.ilike(term),
                Product.material_composition.ilike(term),
                Product.finish.ilike(term),
                Product.color.ilike(term),
                Product.intended_use.ilike(term)
            )
        )

    products = query.order_by(Product.name.asc()).all()
    results: List[ProductOut] = []
    for p in products:
        results.append(
            ProductOut(
                id=p.id,
                name=p.name,
                slug=p.slug,
                sku_code=p.sku_code,
                product_type=p.product_type,
                material_type=p.material_type,
                material_composition=p.material_composition,
                finish=p.finish,
                color=p.color,
                intended_use=p.intended_use,
                dimensions=p.dimensions,
                thickness=p.thickness,
                installation_requirements=p.installation_requirements,
                specs=p.specs,
                official_product_url=p.official_product_url,
                official_catalog_url=p.official_catalog_url,
                country_of_manufacture=p.country_of_manufacture,
                image_url=p.image_url,
                data_source=p.data_source,
                verification_status=p.verification_status,
                last_checked_at=p.last_checked_at,
                manufacturer_id=p.manufacturer_id,
                category_id=p.category_id,
                manufacturer_name=p.manufacturer.name if p.manufacturer else "Not verified",
                category_name=p.category.name if p.category else None,
                created_at=p.created_at
            )
        )
    return results

@router.get("/{id_or_slug}", response_model=ProductDetailOut)
def get_product_detail(id_or_slug: str, db: Session = Depends(get_db)):
    prod = None
    if id_or_slug.isdigit():
        prod = db.query(Product).filter_by(id=int(id_or_slug)).first()
    if not prod:
        prod = db.query(Product).filter_by(slug=id_or_slug).first()

    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    mfg_out = None
    if prod.manufacturer:
        mfg_out = ManufacturerOut.model_validate(prod.manufacturer)
        mfg_out.products_count = len(prod.manufacturer.products)

    cat_out = None
    if prod.category:
        cat_out = CategoryOut.model_validate(prod.category)

    # Suppliers selling this product
    suppliers_list: List[SupplierListingBrief] = []
    for sp in prod.supplier_links:
        sup = sp.supplier
        if sup:
            suppliers_list.append(
                SupplierListingBrief(
                    supplier_id=sup.id,
                    supplier_name=sup.name,
                    city=sup.city,
                    district=sup.district,
                    state=sup.state,
                    match_type=sp.match_type or "exact_product",
                    supplier_product_code=sp.supplier_product_code,
                    price=sp.price,
                    currency=sp.currency or "INR",
                    price_unit=sp.price_unit or "piece",
                    availability_status=sp.availability_status or "in_stock",
                    stock_status=sp.stock_status or "in_stock",
                    stock_confirmed_at=sp.stock_confirmed_at,
                    available_quantity=sp.available_quantity,
                    min_order_quantity=sp.min_order_quantity,
                    delivery_scope=sp.delivery_scope or "state",
                    estimated_lead_time_days=sp.estimated_lead_time_days,
                    phone=sup.phone,
                    website=sup.website,
                    google_maps_url=sup.google_maps_url,
                    verification_status=sp.verification_status or "VERIFIED",
                    is_potential=sup.is_potential
                )
            )

    # Sort suppliers: Exact verified matches first, then in-stock items, then price ascending (if price known)
    def supplier_sort_key(s: SupplierListingBrief):
        is_exact = 0 if s.match_type == "exact_product" else 1
        is_instock = 0 if s.stock_status == "in_stock" else 1
        price_val = s.price if (s.price is not None and s.price > 0) else 999999999.0
        return (is_exact, is_instock, price_val)

    suppliers_list.sort(key=supplier_sort_key)

    # Related architectural references
    related_refs = []
    for match in prod.reference_matches:
        ref = match.reference
        if ref:
            related_refs.append({
                "id": ref.id,
                "title": ref.title,
                "slug": ref.slug,
                "source_platform": ref.source_platform,
                "thumbnail_url": ref.thumbnail_url,
                "match_type": match.match_type,
                "creator_name": ref.creator_name,
                "source_url": ref.source_url
            })

    return ProductDetailOut(
        id=prod.id,
        name=prod.name,
        slug=prod.slug,
        sku_code=prod.sku_code,
        product_type=prod.product_type,
        material_type=prod.material_type,
        material_composition=prod.material_composition,
        finish=prod.finish,
        color=prod.color,
        intended_use=prod.intended_use,
        dimensions=prod.dimensions,
        thickness=prod.thickness,
        installation_requirements=prod.installation_requirements,
        specs=prod.specs,
        official_product_url=prod.official_product_url,
        official_catalog_url=prod.official_catalog_url,
        country_of_manufacture=prod.country_of_manufacture,
        image_url=prod.image_url,
        data_source=prod.data_source,
        verification_status=prod.verification_status,
        last_checked_at=prod.last_checked_at,
        manufacturer_id=prod.manufacturer_id,
        category_id=prod.category_id,
        manufacturer_name=prod.manufacturer.name if prod.manufacturer else "Not verified",
        category_name=prod.category.name if prod.category else None,
        created_at=prod.created_at,
        manufacturer=mfg_out,
        category=cat_out,
        available_suppliers=suppliers_list,
        related_references=related_refs
    )

@router.post("", response_model=ProductOut)
def create_product(prod_in: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter_by(slug=prod_in.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product slug already exists")

    new_prod = Product(
        name=prod_in.name,
        slug=prod_in.slug,
        sku_code=prod_in.sku_code,
        product_type=prod_in.product_type,
        material_type=prod_in.material_type,
        material_composition=prod_in.material_composition,
        finish=prod_in.finish,
        color=prod_in.color,
        intended_use=prod_in.intended_use,
        dimensions=prod_in.dimensions,
        thickness=prod_in.thickness,
        installation_requirements=prod_in.installation_requirements,
        specs=prod_in.specs,
        official_product_url=prod_in.official_product_url,
        official_catalog_url=prod_in.official_catalog_url,
        country_of_manufacture=prod_in.country_of_manufacture,
        image_url=prod_in.image_url,
        data_source=prod_in.data_source or "official_catalog",
        verification_status=prod_in.verification_status or "MANUFACTURER_CONFIRMED",
        last_checked_at=datetime.now(timezone.utc),
        manufacturer_id=prod_in.manufacturer_id,
        category_id=prod_in.category_id
    )
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)

    return ProductOut(
        id=new_prod.id,
        name=new_prod.name,
        slug=new_prod.slug,
        sku_code=new_prod.sku_code,
        product_type=new_prod.product_type,
        material_type=new_prod.material_type,
        material_composition=new_prod.material_composition,
        finish=new_prod.finish,
        color=new_prod.color,
        intended_use=new_prod.intended_use,
        dimensions=new_prod.dimensions,
        thickness=new_prod.thickness,
        installation_requirements=new_prod.installation_requirements,
        specs=new_prod.specs,
        official_product_url=new_prod.official_product_url,
        official_catalog_url=new_prod.official_catalog_url,
        country_of_manufacture=new_prod.country_of_manufacture,
        image_url=new_prod.image_url,
        data_source=new_prod.data_source,
        verification_status=new_prod.verification_status,
        last_checked_at=new_prod.last_checked_at,
        manufacturer_id=new_prod.manufacturer_id,
        category_id=new_prod.category_id,
        manufacturer_name=new_prod.manufacturer.name if new_prod.manufacturer else None,
        category_name=new_prod.category.name if new_prod.category else None,
        created_at=new_prod.created_at
    )

@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    updates: dict = Body(...),
    db: Session = Depends(get_db)
):
    prod = db.query(Product).filter_by(id=product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    allowed_fields = [
        "name", "sku_code", "product_type", "material_type", "material_composition",
        "finish", "color", "intended_use", "dimensions", "thickness",
        "installation_requirements", "specs", "official_product_url",
        "official_catalog_url", "country_of_manufacture", "image_url",
        "verification_status", "manufacturer_id", "category_id"
    ]
    for key, val in updates.items():
        if key in allowed_fields:
            setattr(prod, key, val)

    prod.last_checked_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(prod)

    return ProductOut(
        id=prod.id,
        name=prod.name,
        slug=prod.slug,
        sku_code=prod.sku_code,
        product_type=prod.product_type,
        material_type=prod.material_type,
        material_composition=prod.material_composition,
        finish=prod.finish,
        color=prod.color,
        intended_use=prod.intended_use,
        dimensions=prod.dimensions,
        thickness=prod.thickness,
        installation_requirements=prod.installation_requirements,
        specs=prod.specs,
        official_product_url=prod.official_product_url,
        official_catalog_url=prod.official_catalog_url,
        country_of_manufacture=prod.country_of_manufacture,
        image_url=prod.image_url,
        data_source=prod.data_source,
        verification_status=prod.verification_status,
        last_checked_at=prod.last_checked_at,
        manufacturer_id=prod.manufacturer_id,
        category_id=prod.category_id,
        manufacturer_name=prod.manufacturer.name if prod.manufacturer else None,
        category_name=prod.category.name if prod.category else None,
        created_at=prod.created_at
    )

from app.services.comparison_service import get_all_comparisons, get_comparison_by_id

@router.get("/comparisons/all")
def get_all_material_comparisons():
    """
    Returns all side-by-side material comparisons (Category 27).
    """
    return {
        "total": len(get_all_comparisons()),
        "comparisons": get_all_comparisons()
    }

@router.get("/comparisons/{comp_id}")
def get_single_material_comparison(comp_id: str):
    """
    Returns specific comparative matrix between two architectural materials.
    """
    comp = get_comparison_by_id(comp_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Material comparison matrix not found")
    return comp


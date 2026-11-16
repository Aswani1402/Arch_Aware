from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import Supplier, SupplierProduct, Product, User
from app.schemas.schemas import (
    SupplierOut,
    SupplierDetailOut,
    SupplierProductLink,
    SupplierRegister,
    SupplierCreate,
    HierarchicalSourcingResponse,
    SourcingSearchQuery
)
from app.services.sourcing_service import execute_hierarchical_sourcing

router = APIRouter(prefix="/suppliers", tags=["Suppliers & Vendors"])

@router.get("", response_model=List[SupplierOut])
def get_suppliers(
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
    business_type: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Supplier)
    if city:
        query = query.filter(Supplier.city.ilike(f"%{city}%"))
    if state:
        query = query.filter(Supplier.state.ilike(f"%{state}%"))
    if country:
        query = query.filter(Supplier.country.ilike(f"%{country}%"))
    if business_type:
        query = query.filter(Supplier.business_type == business_type)
    if q:
        query = query.filter(Supplier.name.ilike(f"%{q}%"))

    return query.order_by(Supplier.name.asc()).all()

@router.get("/discover", response_model=HierarchicalSourcingResponse)
def discover_suppliers(
    q: Optional[str] = Query(None, description="Search material or product term (e.g. CPVC pipe, TMT bar, Athangudi tiles)"),
    category: Optional[str] = Query(None, description="Category slug"),
    city: Optional[str] = Query(None, description="City name (e.g. Kochi, Bengaluru, Chennai)"),
    state: Optional[str] = Query(None, description="State (e.g. Kerala, Tamil Nadu, Karnataka)"),
    lat: Optional[float] = Query(None, description="Latitude coordinate"),
    lon: Optional[float] = Query(None, description="Longitude coordinate"),
    radius: float = Query(25.0, description="Initial radius in km"),
    db: Session = Depends(get_db)
):
    """
    Category-Based Supplier Discovery with 7-Tier Geographic Fallback (Part 16).
    Enables users to search suppliers directly without requiring an image.
    Never fails on exact queries by falling back to broader category suppliers with honest match labels.
    """
    search_query = SourcingSearchQuery(
        query=q,
        category_slug=category,
        city=city,
        state=state,
        latitude=lat,
        longitude=lon,
        initial_radius_km=radius
    )
    return execute_hierarchical_sourcing(db, search_query)

@router.get("/{id_or_slug}", response_model=SupplierDetailOut)
def get_supplier_detail(id_or_slug: str, db: Session = Depends(get_db)):
    sup = None
    if id_or_slug.isdigit():
        sup = db.query(Supplier).filter_by(id=int(id_or_slug)).first()
    if not sup:
        sup = db.query(Supplier).filter_by(slug=id_or_slug).first()

    if not sup:
        raise HTTPException(status_code=404, detail="Supplier not found")

    catalog: List[SupplierProductLink] = []
    for sp in sup.product_links:
        prod = sp.product
        if prod:
            catalog.append(
                SupplierProductLink(
                    product_id=prod.id,
                    product_name=prod.name,
                    material_type=prod.material_type,
                    price=sp.price,
                    currency=sp.currency,
                    availability_status=sp.availability_status,
                    min_order_quantity=sp.min_order_quantity,
                    delivery_scope=sp.delivery_scope,
                    image_url=prod.image_url
                )
            )

    return SupplierDetailOut(
        id=sup.id,
        name=sup.name,
        slug=sup.slug,
        business_type=sup.business_type,
        contact_person=sup.contact_person,
        address=sup.address,
        city=sup.city,
        district=sup.district,
        state=sup.state,
        pin_code=sup.pin_code,
        country=sup.country,
        latitude=sup.latitude,
        longitude=sup.longitude,
        phone=sup.phone,
        whatsapp=sup.whatsapp,
        email=sup.email,
        website=sup.website,
        google_maps_url=sup.google_maps_url,
        google_place_id=sup.google_place_id,
        gstin=sup.gstin,
        brands_distributed=sup.brands_distributed,
        delivery_areas=sup.delivery_areas,
        materials_sold=sup.materials_sold,
        verification_status=sup.verification_status,
        verification_method=sup.verification_method,
        verification_notes=sup.verification_notes,
        is_potential=sup.is_potential,
        delivery_radius_km=sup.delivery_radius_km,
        last_updated_at=sup.last_updated_at,
        created_at=sup.created_at,
        catalog_products=catalog
    )

@router.post("/register", response_model=SupplierOut)
def register_supplier(reg: SupplierRegister, db: Session = Depends(get_db)):
    import urllib.parse
    slug = reg.name.lower().replace(" ", "-").replace("&", "and")
    # ensure unique slug
    count = db.query(Supplier).filter(Supplier.slug.like(f"{slug}%")).count()
    if count > 0:
        slug = f"{slug}-{count+1}"

    # Generate 100% free web search map navigation URL without any API key or Google Cloud billing
    search_query = f"{reg.name} {reg.address} {reg.city} {reg.state}"
    free_maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote_plus(search_query)}"

    sup = Supplier(
        name=reg.name,
        slug=slug,
        business_type=reg.business_type,
        contact_person=reg.contact_person,
        address=reg.address,
        city=reg.city,
        district=reg.district,
        state=reg.state,
        pin_code=reg.pin_code,
        country="India",
        latitude=reg.latitude,
        longitude=reg.longitude,
        phone=reg.phone,
        whatsapp=reg.whatsapp,
        email=reg.email,
        website=reg.website,
        google_maps_url=free_maps_url,
        gstin=reg.gstin,
        brands_distributed=reg.brands_distributed,
        delivery_areas=reg.delivery_areas,
        verification_status="PENDING_REVIEW",  # New supplier registrations require admin review
        verification_method="manual_admin_review",
        is_potential=False,
        delivery_radius_km=reg.delivery_radius_km
    )
    db.add(sup)
    db.commit()
    db.refresh(sup)
    return sup

@router.post("/{supplier_id}/products")
def link_supplier_product(
    supplier_id: int,
    link_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import datetime, timezone
    sup = db.query(Supplier).filter_by(id=supplier_id).first()
    if not sup:
        raise HTTPException(status_code=404, detail="Supplier not found")

    if current_user.role != "admin" and sup.user_id is not None and sup.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to manage this supplier's products",
        )

    product_id = link_data.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")

    prod = db.query(Product).filter_by(id=product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if link exists
    link = db.query(SupplierProduct).filter_by(supplier_id=supplier_id, product_id=product_id).first()
    if not link:
        link = SupplierProduct(supplier_id=supplier_id, product_id=product_id)
        db.add(link)

    link.match_type = link_data.get("match_type", "exact_product")
    link.supplier_product_code = link_data.get("supplier_product_code")
    link.price = link_data.get("price")
    link.currency = link_data.get("currency", "INR")
    link.price_unit = link_data.get("price_unit", "piece")
    link.availability_status = link_data.get("availability_status", "in_stock")
    link.stock_status = link_data.get("stock_status", "in_stock")
    link.stock_confirmed_at = datetime.now(timezone.utc)
    link.available_quantity = link_data.get("available_quantity")
    link.min_order_quantity = link_data.get("min_order_quantity")
    link.delivery_scope = link_data.get("delivery_scope", "state")
    link.estimated_lead_time_days = link_data.get("estimated_lead_time_days")
    link.listing_url = link_data.get("listing_url")
    link.last_confirmed_date = datetime.now(timezone.utc)
    link.last_updated_at = datetime.now(timezone.utc)
    link.notes = link_data.get("notes")

    sup.last_updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(link)

    return {
        "success": True,
        "supplier_id": supplier_id,
        "product_id": product_id,
        "price": link.price,
        "currency": link.currency,
        "price_unit": link.price_unit,
        "stock_status": link.stock_status,
        "match_type": link.match_type,
        "message": "Supplier product listing updated successfully"
    }

@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(
    supplier_id: int,
    updates: dict = Body(...),
    db: Session = Depends(get_db)
):
    from datetime import datetime, timezone
    sup = db.query(Supplier).filter_by(id=supplier_id).first()
    if not sup:
        raise HTTPException(status_code=404, detail="Supplier not found")

    allowed_fields = [
        "name", "business_type", "contact_person", "address", "city", "district",
        "state", "pin_code", "country", "phone", "whatsapp", "email", "website", "gstin",
        "brands_distributed", "delivery_areas", "delivery_radius_km"
    ]
    for key, val in updates.items():
        if key in allowed_fields:
            setattr(sup, key, val)

    sup.last_updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(sup)
    return sup

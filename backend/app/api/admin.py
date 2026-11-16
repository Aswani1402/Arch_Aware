from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_admin
from app.models.models import (
    User, Supplier, Product, ArchitecturalReference,
    Manufacturer, MaterialCategory, SourceConnector, SourceSyncLog,
    SupplierProduct
)
from app.schemas.schemas import SupplierOut, ProductOut, ReferenceOut, UserOut

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/stats")
def get_admin_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_refs = db.query(ArchitecturalReference).count()
    total_prods = db.query(Product).count()
    total_suppliers = db.query(Supplier).count()
    verified_suppliers = db.query(Supplier).filter(Supplier.verification_status == "VERIFIED").count()
    pending_suppliers = db.query(Supplier).filter(Supplier.verification_status.in_(["PENDING_REVIEW", "UNVERIFIED", "POTENTIAL_GOOGLE_PLACE"])).count()
    total_mfgs = db.query(Manufacturer).count()
    total_users = db.query(User).count()
    connectors_count = db.query(SourceConnector).count()

    recent_logs = db.query(SourceSyncLog).order_by(SourceSyncLog.id.desc()).limit(5).all()
    logs_data = [{
        "id": l.id,
        "connector_id": l.connector_id,
        "status": l.status,
        "items_ingested": l.items_ingested,
        "error_message": l.error_message,
        "timestamp": l.timestamp
    } for l in recent_logs]

    return {
        "total_references": total_refs,
        "total_products": total_prods,
        "total_suppliers": total_suppliers,
        "verified_suppliers": verified_suppliers,
        "pending_suppliers": pending_suppliers,
        "total_manufacturers": total_mfgs,
        "total_users": total_users,
        "connectors_count": connectors_count,
        "recent_sync_logs": logs_data
    }

@router.put("/suppliers/{supplier_id}/verify")
def update_supplier_verification(
    supplier_id: int,
    status: str = Body(..., embed=True),
    notes: Optional[str] = Body(None, embed=True),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    sup = db.query(Supplier).filter_by(id=supplier_id).first()
    if not sup:
        raise HTTPException(status_code=404, detail="Supplier not found")

    valid_statuses = ["VERIFIED", "PENDING_REVIEW", "UNVERIFIED", "REJECTED", "EXPIRED", "POTENTIAL_GOOGLE_PLACE"]
    if status.upper() not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid verification status. Must be one of: {valid_statuses}")

    sup.verification_status = status.upper()
    if status.upper() == "VERIFIED":
        sup.is_potential = False
    db.commit()
    db.refresh(sup)
    return {
        "success": True,
        "supplier_id": sup.id,
        "name": sup.name,
        "verification_status": sup.verification_status,
        "message": f"Supplier verification updated to {sup.verification_status}"
    }

@router.put("/products/{product_id}/verify")
def update_product_verification(
    product_id: int,
    status: str = Body(..., embed=True),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    prod = db.query(Product).filter_by(id=product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    prod.verification_status = status.upper()
    db.commit()
    db.refresh(prod)
    return {
        "success": True,
        "product_id": prod.id,
        "name": prod.name,
        "verification_status": prod.verification_status
    }

@router.put("/references/{reference_id}/verify")
def update_reference_verification(
    reference_id: int,
    status: str = Body(..., embed=True),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    ref = db.query(ArchitecturalReference).filter_by(id=reference_id).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Reference not found")

    ref.verification_status = status.upper()
    db.commit()
    db.refresh(ref)
    return {
        "success": True,
        "reference_id": ref.id,
        "title": ref.title,
        "verification_status": ref.verification_status
    }

@router.get("/quality-audit")
def get_data_quality_audit(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    sixty_days_ago = now - timedelta(days=60)
    ninety_days_ago = now - timedelta(days=90)

    # 1. Broken / Flagged source links
    all_refs = db.query(ArchitecturalReference).all()
    broken_sources = []
    for r in all_refs:
        if r.content_availability_status in ["BROKEN_LINK", "FLAGGED_FOR_REVIEW"] or not r.source_url:
            broken_sources.append({
                "id": r.id,
                "title": r.title,
                "source_platform": r.source_platform,
                "source_url": r.source_url,
                "status": r.content_availability_status
            })

    # 2. Missing product images
    all_prods = db.query(Product).all()
    missing_images = []
    prod_name_counts = {}
    prods_without_mfg = []

    for p in all_prods:
        if not p.image_url:
            missing_images.append({"id": p.id, "name": p.name, "category": p.category.name if p.category else None})
        if not p.manufacturer_id:
            prods_without_mfg.append({"id": p.id, "name": p.name})
        
        # Check duplicate name
        clean_name = p.name.strip().lower()
        prod_name_counts.setdefault(clean_name, []).append(p.id)

    duplicate_products = [
        {"name": name, "product_ids": ids} for name, ids in prod_name_counts.items() if len(ids) > 1
    ]

    # 3. Suppliers audit
    all_sups = db.query(Supplier).all()
    duplicate_sups = []
    sup_name_counts = {}
    sups_without_products = []
    unverified_claims = []

    for s in all_sups:
        if len(s.product_links) == 0:
            sups_without_products.append({"id": s.id, "name": s.name, "city": s.city})
        if s.verification_status in ["PENDING_REVIEW", "UNVERIFIED"] or s.is_potential:
            unverified_claims.append({
                "id": s.id,
                "name": s.name,
                "city": s.city,
                "status": s.verification_status,
                "is_potential": s.is_potential
            })

        key = f"{s.name.strip().lower()}--{s.city.strip().lower()}"
        sup_name_counts.setdefault(key, []).append(s.id)

    duplicate_suppliers = [
        {"key": key, "supplier_ids": ids} for key, ids in sup_name_counts.items() if len(ids) > 1
    ]

    # 4. Outdated stock & missing price units
    all_sp = db.query(SupplierProduct).all()
    outdated_stock = []
    prices_without_units = []

    for sp in all_sp:
        # Check stock timestamp
        if sp.stock_confirmed_at and sp.stock_confirmed_at.replace(tzinfo=timezone.utc) < sixty_days_ago:
            outdated_stock.append({
                "supplier_id": sp.supplier_id,
                "product_id": sp.product_id,
                "supplier_name": sp.supplier.name if sp.supplier else "Unknown",
                "product_name": sp.product.name if sp.product else "Unknown",
                "last_confirmed": sp.stock_confirmed_at.isoformat()
            })
        if sp.price is not None and not sp.price_unit:
            prices_without_units.append({
                "supplier_id": sp.supplier_id,
                "product_id": sp.product_id,
                "price": sp.price
            })

    # 5. Unchecked catalog links
    all_mfgs = db.query(Manufacturer).all()
    unchecked_catalogs = []
    for m in all_mfgs:
        if m.official_catalog_url:
            if not m.last_verified_at or m.last_verified_at.replace(tzinfo=timezone.utc) < ninety_days_ago:
                unchecked_catalogs.append({
                    "id": m.id,
                    "name": m.name,
                    "catalog_url": m.official_catalog_url,
                    "last_verified": m.last_verified_at.isoformat() if m.last_verified_at else None
                })

    # 6. References with missing attribution
    missing_attribution = []
    for r in all_refs:
        if not r.creator_name or not r.source_url:
            missing_attribution.append({
                "id": r.id,
                "title": r.title,
                "source_platform": r.source_platform
            })

    return {
        "timestamp": now.isoformat(),
        "summary": {
            "total_broken_sources": len(broken_sources),
            "total_missing_product_images": len(missing_images),
            "total_duplicate_products": len(duplicate_products),
            "total_duplicate_suppliers": len(duplicate_suppliers),
            "total_products_without_manufacturer": len(prods_without_mfg),
            "total_suppliers_without_products": len(sups_without_products),
            "total_unverified_supplier_claims": len(unverified_claims),
            "total_outdated_stock": len(outdated_stock),
            "total_prices_without_units": len(prices_without_units),
            "total_unchecked_catalogs": len(unchecked_catalogs),
            "total_missing_attribution": len(missing_attribution)
        },
        "issues": {
            "broken_source_links": broken_sources,
            "missing_product_images": missing_images,
            "duplicate_products": duplicate_products,
            "duplicate_suppliers": duplicate_suppliers,
            "products_without_manufacturers": prods_without_mfg,
            "suppliers_without_products": sups_without_products,
            "unverified_supplier_claims": unverified_claims,
            "outdated_stock": outdated_stock,
            "prices_without_units": prices_without_units,
            "unchecked_catalog_links": unchecked_catalogs,
            "references_missing_attribution": missing_attribution
        }
    }

@router.put("/records/correct")
def correct_record(
    record_type: str = Body(..., embed=True),  # product, supplier, manufacturer, reference
    record_id: int = Body(..., embed=True),
    corrections: dict = Body(..., embed=True),
    reason: str = Body(..., embed=True),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    if record_type == "product":
        obj = db.query(Product).filter_by(id=record_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Product not found")
        for k, v in corrections.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        obj.last_checked_at = now

    elif record_type == "supplier":
        obj = db.query(Supplier).filter_by(id=record_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Supplier not found")
        for k, v in corrections.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        obj.last_updated_at = now
        obj.verification_notes = f"Admin corrected: {reason}"

    elif record_type == "manufacturer":
        obj = db.query(Manufacturer).filter_by(id=record_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Manufacturer not found")
        for k, v in corrections.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        obj.last_verified_at = now
        obj.unverified_notes = f"Verified/corrected: {reason}"

    elif record_type == "reference":
        obj = db.query(ArchitecturalReference).filter_by(id=record_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Reference not found")
        for k, v in corrections.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        obj.last_checked_at = now

    else:
        raise HTTPException(status_code=400, detail="Invalid record_type. Must be product, supplier, manufacturer, or reference")

    db.commit()
    return {
        "success": True,
        "record_type": record_type,
        "record_id": record_id,
        "reason_logged": reason,
        "updated_at": now.isoformat()
    }


@router.get("/daily-collection/status")
def get_daily_collection_status_endpoint(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Returns the status of the 9:00 AM IST automated data collection system,
    including the next run time, today's summary, and last completed job.
    """
    from app.services.daily_collection_service import get_collection_status_summary
    return get_collection_status_summary(db)


@router.post("/daily-collection/trigger")
def trigger_daily_collection_endpoint(
    max_categories: Optional[int] = Body(6, embed=True),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Explicit Administrator trigger to run the daily collection job on-demand
    without waiting for 9:00 AM IST. Normal users browsing or refreshing never trigger this.
    """
    from app.services.daily_collection_service import execute_daily_collection_task
    # Trigger synchronously or with budget limit
    result = execute_daily_collection_task(force=True, max_items=max_categories)
    return {
        "success": True,
        "triggered_by": "administrator",
        "result": result
    }


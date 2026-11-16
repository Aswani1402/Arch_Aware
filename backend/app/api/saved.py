from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User, SavedItem, ArchitecturalReference, Product, Supplier
from app.schemas.schemas import SavedItemCreate, SavedItemOut

router = APIRouter(prefix="/saved", tags=["Saved Items & Collections"])

@router.post("/toggle")
def toggle_save_item(
    item_in: SavedItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(SavedItem).filter_by(
        user_id=current_user.id,
        item_type=item_in.item_type
    )
    if item_in.item_type == "reference":
        query = query.filter_by(reference_id=item_in.reference_id)
    elif item_in.item_type == "product":
        query = query.filter_by(product_id=item_in.product_id)
    elif item_in.item_type == "supplier":
        query = query.filter_by(supplier_id=item_in.supplier_id)

    existing = query.first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"saved": False, "is_saved": False, "status": "unsaved", "message": "Item removed from collection"}
    else:
        new_item = SavedItem(
            user_id=current_user.id,
            item_type=item_in.item_type,
            reference_id=item_in.reference_id,
            product_id=item_in.product_id,
            supplier_id=item_in.supplier_id,
            project_collection=item_in.project_collection
        )
        db.add(new_item)
        db.commit()
        return {"saved": True, "is_saved": True, "status": "saved", "message": "Item saved to collection"}

@router.get("/counts")
def get_saved_counts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = db.query(SavedItem.item_type).filter_by(user_id=current_user.id).all()
    references_count = sum(1 for it in items if it[0] == "reference")
    suppliers_count = sum(1 for it in items if it[0] == "supplier")
    products_count = sum(1 for it in items if it[0] == "product")
    return {
        "total_count": len(items),
        "references_count": references_count,
        "suppliers_count": suppliers_count,
        "products_count": products_count
    }

@router.get("", response_model=List[SavedItemOut])
@router.get("/items", response_model=List[SavedItemOut])
def get_saved_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = db.query(SavedItem).filter_by(user_id=current_user.id).order_by(SavedItem.id.desc()).all()
    results: List[SavedItemOut] = []
    for item in items:
        item_data = None
        if item.item_type == "reference" and item.reference_id:
            ref = db.query(ArchitecturalReference).filter_by(id=item.reference_id).first()
            if ref:
                item_data = {
                    "id": ref.id,
                    "title": ref.title,
                    "slug": ref.slug,
                    "thumbnail_url": ref.thumbnail_url,
                    "media_url": ref.media_url or ref.thumbnail_url,
                    "inspiration_image_url": ref.inspiration_image_url or ref.thumbnail_url,
                    "inspiration_source_url": ref.inspiration_source_url or ref.source_url,
                    "video_embed_id": ref.video_embed_id,
                    "video_duration": ref.video_duration,
                    "is_short": ref.is_short,
                    "source_platform": ref.source_platform,
                    "source_url": ref.source_url,
                    "source_domain": ref.source_domain,
                    "creator_name": ref.creator_name,
                    "architect_name": ref.architect_name,
                    "category_name": ref.category.name if ref.category else None,
                    "material_tags": ref.material_tags,
                    "location_context": ref.location_context,
                    "image_attribution": ref.image_attribution,
                    "colors_and_finishes": ref.colors_and_finishes,
                    "content_type": ref.content_type,
                    "description": ref.description,
                    "matched_products_count": len(ref.product_matches),
                    "product_match_status": ref.product_match_status,
                    "verification_status": ref.verification_status or "UNVERIFIED",
                }
        elif item.item_type == "product" and item.product_id:
            prod = db.query(Product).filter_by(id=item.product_id).first()
            if prod:
                item_data = {
                    "name": prod.name,
                    "slug": prod.slug,
                    "image_url": prod.image_url,
                    "material_type": prod.material_type,
                    "manufacturer_name": prod.manufacturer.name if prod.manufacturer else "Not verified",
                    "verification_status": prod.verification_status or "UNKNOWN",
                }
        elif item.item_type == "supplier" and item.supplier_id:
            sup = db.query(Supplier).filter_by(id=item.supplier_id).first()
            if sup:
                item_data = {
                    "id": sup.id,
                    "supplier_id": sup.id,
                    "name": sup.name,
                    "title": sup.name,
                    "slug": sup.slug,
                    "business_type": sup.business_type,
                    "materials_sold": sup.materials_sold,
                    "verification_status": sup.verification_status,
                    "is_potential": sup.is_potential,
                    "address": sup.address,
                    "city": sup.city,
                    "state": sup.state,
                    "country": sup.country or "India",
                    "phone": sup.phone,
                    "whatsapp": getattr(sup, "whatsapp", None),
                    "email": sup.email,
                    "website": sup.website,
                    "google_maps_url": sup.google_maps_url,
                    "instagram_url": getattr(sup, "instagram_url", None),
                }

        results.append(
            SavedItemOut(
                id=item.id,
                user_id=item.user_id,
                item_type=item.item_type,
                reference_id=item.reference_id,
                product_id=item.product_id,
                supplier_id=item.supplier_id,
                project_collection=item.project_collection,
                created_at=item.created_at,
                item_data=item_data
            )
        )
    return results

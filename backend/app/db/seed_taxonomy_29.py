from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import MaterialCategory
from app.services.taxonomy_service import TAXONOMY_29_CATEGORIES

def sync_taxonomy_29(db: Session):
    print(f"[Taxonomy Sync] Synchronizing {len(TAXONOMY_29_CATEGORIES)} comprehensive architectural categories...")
    
    existing_by_slug = {c.slug: c for c in db.query(MaterialCategory).all()}
    added = 0
    updated = 0
    
    for cat_def in TAXONOMY_29_CATEGORIES:
        slug = cat_def["slug"]
        subcategories_str = ", ".join(cat_def.get("subcategories", []))
        
        if slug in existing_by_slug:
            existing = existing_by_slug[slug]
            existing.description = cat_def["description"]
            existing.section_name = cat_def["section"]
            existing.typical_applications = cat_def["applications"]
            existing.subcategories = subcategories_str
            existing.standards_compliance = cat_def["standards"]
            updated += 1
        else:
            new_cat = MaterialCategory(
                name=cat_def["name"],
                slug=slug,
                description=cat_def["description"],
                image_url=cat_def["image_url"],
                section_code=cat_def["code"],
                section_name=cat_def["section"],
                typical_applications=cat_def["applications"],
                subcategories=subcategories_str,
                standards_compliance=cat_def["standards"]
            )
            db.add(new_cat)
            added += 1
            
    db.commit()
    print(f"[Taxonomy Sync] Finished: {added} new categories added, {updated} existing categories enriched.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        sync_taxonomy_29(db)
    finally:
        db.close()

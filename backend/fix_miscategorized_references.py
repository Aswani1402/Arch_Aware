from app.core.database import SessionLocal
from app.models.models import ArchitecturalReference, MaterialCategory

def fix_categories():
    db = SessionLocal()
    slug_map = {c.slug: c.id for c in db.query(MaterialCategory).all()}
    
    # Map reference IDs to their correct category slugs
    CORRECTIONS = {
        26: "plumbing-piping",              # CPVC Pipe & Fittings
        28: "lighting",                     # 25 Premium Interior Lighting Choices
        30: "interior-design-furnishings",  # 3 Interior Designers Transform Loft Bedroom
        31: "ceiling-systems",              # PVC ceiling installation method
        33: "structural-steel",             # Tips formwork installation
        39: "flooring",                     # Terrazzo Flooring Installation
        40: "flooring",                     # White Cementitious Terrazzo
        41: "flooring",                     # Terrazzo Flooring Installation & Diamond Polishing
        48: "interior-design-furnishings",  # Warm Japandi Living Room Transformation
        55: "kitchens-storage",             # Contemporary Modular Kitchen Design
        63: "architecture-house-types",     # Budget-Friendly Small House Construction
        80: "renovation-stories"            # Kitchen Renovation & Modular Cabinet
    }
    
    updated = 0
    for ref_id, cat_slug in CORRECTIONS.items():
        ref = db.query(ArchitecturalReference).filter_by(id=ref_id).first()
        if ref and cat_slug in slug_map:
            old_cat = ref.category.name if ref.category else "None"
            ref.category_id = slug_map[cat_slug]
            print(f"Updated Ref #{ref_id} '{ref.title[:40]}' from '{old_cat}' -> '{cat_slug}'")
            updated += 1
            
    db.commit()
    print(f"Successfully updated {updated} references in database.")
    db.close()

if __name__ == "__main__":
    fix_categories()

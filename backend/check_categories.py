from app.core.database import SessionLocal
from app.models.models import ArchitecturalReference, MaterialCategory

db = SessionLocal()
refs = db.query(ArchitecturalReference).all()
cats = {c.id: c.name for c in db.query(MaterialCategory).all()}

for r in refs:
    c_name = cats.get(r.category_id, "NONE")
    print(f"[{r.id:2d}] Cat: {c_name:<30} | {r.title}")
db.close()

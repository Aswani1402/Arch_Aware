import urllib.request
import json
from app.core.database import SessionLocal
from app.models.models import MaterialCategory

def check_category_population():
    db = SessionLocal()
    cats = db.query(MaterialCategory).order_by(MaterialCategory.id).all()
    print("=" * 80)
    print("TAXONOMY BRANCH POPULATION AUDIT")
    print("=" * 80)
    
    populated = []
    unpopulated = []
    
    for c in cats:
        url = f"http://127.0.0.1:8000/api/feed?category={c.slug}&page_size=5"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                total = data.get("total", 0)
                if total > 0:
                    populated.append((c.id, c.slug, c.name, total))
                    print(f"  [POPULATED]   ({total:2d} items) [{c.id:2d}] {c.slug:<28} -> {c.name}")
                else:
                    unpopulated.append((c.id, c.slug, c.name))
                    print(f"  [UNPOPULATED] ( 0 items) [{c.id:2d}] {c.slug:<28} -> {c.name}")
        except Exception as e:
            print(f"  [ERROR] {c.slug}: {e}")

    print("\nSummary:")
    print(f"  Total Categories: {len(cats)}")
    print(f"  Populated Branches: {len(populated)}")
    print(f"  Unpopulated (Placeholder) Branches: {len(unpopulated)}")
    
    db.close()

if __name__ == "__main__":
    check_category_population()

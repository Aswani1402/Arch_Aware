from app.core.database import SessionLocal
from app.models.models import ArchitecturalReference
from collections import Counter

db = SessionLocal()
refs = db.query(ArchitecturalReference).filter(ArchitecturalReference.video_embed_id.isnot(None)).all()
v_counts = Counter([r.video_embed_id for r in refs if r.video_embed_id])
dupes = {k: v for k, v in v_counts.items() if v > 1}
print(f"Total video items: {len(refs)}, Unique IDs: {len(v_counts)}")
print("Duplicate video IDs count:", len(dupes))
for k, count in dupes.items():
    print(f"\nVideo ID '{k}' used {count} times:")
    matching = [r for r in refs if r.video_embed_id == k]
    for m in matching:
        print(f"  [#{m.id}] {m.title}")
db.close()

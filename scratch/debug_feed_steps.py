import sys
import os
sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import SessionLocal
from app.models.models import ArchitecturalReference, MaterialCategory, Product
from app.services.socialcrawl_service import is_socialcrawl_configured
from app.services.relevance_service import relevance_service
from app.services.image_search_service import image_search_service
from app.schemas.schemas import ReferenceOut, FeedResponse

db = SessionLocal()

print("Step 1: db.query(ArchitecturalReference)...", flush=True)
q = db.query(ArchitecturalReference).all()
print(f"Step 1 done: {len(q)} records", flush=True)

print("Step 2: is_socialcrawl_configured()...", flush=True)
sc = is_socialcrawl_configured()
print(f"Step 2 done: {sc}", flush=True)

print("Step 3: image_search_service.get_provider_status()...", flush=True)
img_st = image_search_service.get_provider_status()
print(f"Step 3 done: {img_st}", flush=True)

print("Step 4: counting query...", flush=True)
yt_count = db.query(ArchitecturalReference).filter_by(source_platform="youtube").count()
print(f"Step 4 done: {yt_count}", flush=True)

db.close()
print("All steps finished successfully!", flush=True)


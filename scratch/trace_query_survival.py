import sys
sys.path.insert(0, 'backend')
from app.core.database import SessionLocal
from app.services.search_orchestration_service import search_orchestration_service
from app.services.catalogue_import_service import search_catalogue_materials
from app.api.discovery import _enrich_taxonomy_context
from app.services.discovery_adapters import (
    PinterestAdapter,
    InstagramAdapter,
    YouTubeAdapter,
    RedditAdapter,
    GoogleSearchAdapter,
    GoogleShoppingAdapter,
    GooglePlacesAdapter
)

queries = [
    ("Fly ash brick", "Exterior", "Bricks, blocks and masonry"),
    ("Hollow concrete block", "Exterior", "Bricks, blocks and masonry"),
    ("Marble flooring", "Interior", "Floor finishes"),
    ("Laterite stone", "Exterior", "Bricks, blocks and masonry")
]

db = SessionLocal()

adapters = {
    "Pinterest": PinterestAdapter(),
    "Instagram": InstagramAdapter(),
    "YouTube": YouTubeAdapter(),
    "Reddit": RedditAdapter(),
    "Google Search": GoogleSearchAdapter(),
    "Google Shopping": GoogleShoppingAdapter(),
    "Google Places": GooglePlacesAdapter()
}

print("="*80)
print("FORENSIC TRACE: MATERIAL QUERY SURVIVAL THROUGH DISCOVERY PIPELINE")
print("="*80)

for q, cat, subcat in queries:
    print(f"\n>>> QUERY: '{q}' (Cat: {cat}, Subcat: {subcat})")
    
    # 1. Taxonomy context enrichment
    ctx = _enrich_taxonomy_context(
        db=db,
        clean_query=q,
        category=cat,
        subcategory=subcat,
        material=q,
        city="Thiruvananthapuram",
        state="Kerala"
    )
    print(f"  [Taxonomy Context]: exact='{ctx.get('exact_keyword')}', cat='{ctx.get('category')}', subcat='{ctx.get('subcategory')}', cat_matches_count={ctx.get('catalogue_matches_count')}")
    if ctx.get("catalogue_top_match"):
        top = ctx["catalogue_top_match"]
        print(f"  [Catalogue Top Match]: id={top.get('id')}, name='{top.get('name')}', cat='{top.get('category_name')}', subcat='{top.get('subcategory_name')}'")
    else:
        print("  [Catalogue Top Match]: NONE")

    # 2. Query variations constructed by adapters
    print("  [Adapter Query Variations]:")
    for name, adp in adapters.items():
        q_vars = adp.build_queries(q, ctx)
        primary = q_vars[0] if q_vars else "NONE"
        print(f"    - {name:15}: primary='{primary}' | all={q_vars[:3]}")

db.close()


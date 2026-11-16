from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas.schemas import SourcingSearchQuery, HierarchicalSourcingResponse
from app.services.sourcing_service import execute_hierarchical_sourcing

router = APIRouter(prefix="/sourcing", tags=["Location-Based Sourcing & Regional Fallback"])

@router.get("/search", response_model=HierarchicalSourcingResponse)
def search_sourcing(
    q: Optional[str] = Query(None, description="Search material or product term"),
    product_id: Optional[int] = Query(None, description="Direct product ID"),
    category: Optional[str] = Query(None, description="Category slug"),
    city: Optional[str] = Query(None, description="City name (e.g. Kochi, Bengaluru, Chennai, Mumbai)"),
    state: Optional[str] = Query(None, description="State (e.g. Kerala, Karnataka, Tamil Nadu)"),
    lat: Optional[float] = Query(None, description="Latitude coordinate"),
    lon: Optional[float] = Query(None, description="Longitude coordinate"),
    radius: float = Query(25.0, description="Initial radius in km (default 25)"),
    db: Session = Depends(get_db)
):
    search_query = SourcingSearchQuery(
        query=q,
        product_id=product_id,
        category_slug=category,
        city=city,
        state=state,
        latitude=lat,
        longitude=lon,
        initial_radius_km=radius
    )
    return execute_hierarchical_sourcing(db, search_query)

@router.post("/search", response_model=HierarchicalSourcingResponse)
def search_sourcing_post(
    search_query: SourcingSearchQuery,
    db: Session = Depends(get_db)
):
    return execute_hierarchical_sourcing(db, search_query)

@router.get("/places-suppliers")
async def get_places_suppliers(
    material_type: str = Query("Building Materials", description="Material or product to search"),
    city: Optional[str] = Query(None, description="City name (e.g. Bangalore, Kochi, Chennai)"),
    lat: Optional[float] = Query(None, description="Latitude coordinate"),
    lon: Optional[float] = Query(None, description="Longitude coordinate"),
    radius: float = Query(25.0, description="Search radius in km")
):
    from app.services.google_places_service import GooglePlacesService
    svc = GooglePlacesService()
    return await svc.search_nearby_suppliers(
        material_type=material_type,
        lat=lat,
        lon=lon,
        city=city,
        radius_km=radius
    )

@router.get("/socialcrawl-suppliers")
def get_socialcrawl_suppliers(
    q: str = Query(..., min_length=1, description="Material or business keyword"),
    location: Optional[str] = Query(None, description="Location string (e.g. Bengaluru, Karnataka, India)"),
    lat: Optional[float] = Query(None, description="Latitude coordinate"),
    lon: Optional[float] = Query(None, description="Longitude coordinate"),
    dry_run: bool = Query(False, description="Dry-run price check")
):
    """
    Discover suppliers via SocialCrawl Google Business and products via Google Shopping.
    Integrates external Google Business directories with verified stock and pricing.
    """
    from app.services.socialcrawl_service import search_google_businesses, search_google_shopping
    search_location = location if location and location.strip() else "India"
    biz_res = search_google_businesses(query=q, location=search_location, lat=lat, lon=lon, dry_run=dry_run)
    shop_res = search_google_shopping(query=q, dry_run=dry_run)
    return {
        "query": q,
        "location": location,
        "search_scope": search_location,
        "businesses": biz_res.get("items", []),
        "products": shop_res.get("items", []),
        "businesses_count": biz_res.get("total_items", 0),
        "products_count": shop_res.get("total_items", 0),
        "dry_run": dry_run
    }


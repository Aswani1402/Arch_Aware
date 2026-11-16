from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User, ArchitecturalReference, SavedItem, Product, Supplier
from app.services.socialcrawl_service import (
    search_instagram_reels,
    search_instagram_profiles,
    get_instagram_profile,
    generate_focused_instagram_queries,
    search_youtube,
    search_reddit,
    search_twitter_ai,
    search_google_business,
    search_google_shopping,
    search_all_sources,
    is_socialcrawl_configured,
    ARCHITECTURAL_CATEGORIES,
    CREDIT_COSTS,
    _SOCIALCRAWL_CACHE
)

router = APIRouter(prefix="/socialcrawl", tags=["SocialCrawl Multi-Platform Integration"])


class SocialCrawlSaveIn(BaseModel):
    source_platform: str = Field(..., description="Source: instagram, youtube, reddit, google_business, google_shopping")
    external_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    source_url: str = Field(..., description="Original platform URL")
    creator_name: Optional[str] = None
    creator_url: Optional[str] = None
    category_slug: Optional[str] = None
    material_tags: Optional[str] = None
    project_collection: Optional[str] = "Moodboard"


@router.get("/status")
def get_socialcrawl_status():
    """
    Return whether the SocialCrawl API key is configured and endpoint statuses.
    Never exposes the raw API key.
    """
    configured = is_socialcrawl_configured()
    return {
        "configured": configured,
        "provider": "SocialCrawl",
        "endpoints": {
            "instagram_reels": "https://www.socialcrawl.dev/v1/instagram/search/reels",
            "instagram_profiles": "https://www.socialcrawl.dev/v1/instagram/search/profiles",
            "instagram_profile": "https://www.socialcrawl.dev/v1/instagram/profile",
            "youtube": "https://www.socialcrawl.dev/v1/youtube/search",
            "reddit": "https://www.socialcrawl.dev/v1/reddit/search",
            "x": "https://www.socialcrawl.dev/v1/twitter/ai-search",
            "google_business": "https://www.socialcrawl.dev/v1/google/business/search",
            "google_shopping": "https://www.socialcrawl.dev/v1/google_shopping/product",
        },
        "credit_pricing": CREDIT_COSTS,
        "cached_queries_count": len(_SOCIALCRAWL_CACHE),
        "message": (
            "SocialCrawl API is configured and operational."
            if configured
            else "SOCIALCRAWL_API_KEY environment variable is missing. Configured key required for live crawling."
        )
    }


@router.get("/categories")
def get_socialcrawl_categories():
    """
    Returns the comprehensive architectural taxonomy and targeted queries
    for each platform source across all 10 architectural categories.
    """
    return {
        "total": len(ARCHITECTURAL_CATEGORIES),
        "categories": ARCHITECTURAL_CATEGORIES
    }


@router.get("/instagram")
def get_instagram_reels(
    query: str = Query(..., min_length=1, max_length=300, description="Architectural search term"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    date_posted: Optional[str] = Query("last-month", description="Date posted filter"),
    relevance: Optional[str] = Query("score", description="Relevance ranking metric"),
    max_pages: Optional[int] = Query(1, ge=1, le=10, description="Max pages to fetch"),
    dry_run: Optional[bool] = Query(False, description="Dry-run price check without charging credits")
):
    """
    Search architectural inspiration reels from Instagram via SocialCrawl.
    Cost: 1 credit per page.
    """
    clean_query = query.strip()
    if not clean_query:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Query cannot be empty.")

    if not is_socialcrawl_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SOCIALCRAWL_API_KEY environment variable is missing."
        )

    try:
        return search_instagram_reels(
            query=clean_query,
            cursor=cursor,
            date_posted=date_posted or "last-month",
            relevance=relevance or "score",
            max_pages=max_pages or 1,
            dry_run=bool(dry_run)
        )
    except RuntimeError as err:
        err_msg = str(err)
        if "missing" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"SocialCrawl Instagram error: {err_msg}")
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Instagram search failed: {str(err)}")


@router.get("/instagram/reels")
def get_instagram_reels_alias(
    query: str = Query(..., min_length=1, max_length=300, description="Architectural search term"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    date_posted: Optional[str] = Query("last-month", description="Date posted filter"),
    relevance: Optional[str] = Query("score", description="Relevance ranking metric"),
    max_pages: Optional[int] = Query(1, ge=1, le=10, description="Max pages to fetch"),
    dry_run: Optional[bool] = Query(False, description="Dry-run price check without charging credits")
):
    """
    Search architectural inspiration reels from Instagram via SocialCrawl (GET /v1/instagram/search/reels).
    Cost: 1 credit per page.
    """
    return get_instagram_reels(
        query=query,
        cursor=cursor,
        date_posted=date_posted,
        relevance=relevance,
        max_pages=max_pages,
        dry_run=dry_run
    )


@router.get("/instagram/profiles")
def get_instagram_profiles(
    query: str = Query(..., min_length=1, max_length=300, description="Architect / professional search query"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    max_pages: Optional[int] = Query(1, ge=1, le=10, description="Max pages to fetch (default 1, max 10)"),
    dry_run: Optional[bool] = Query(False, description="Dry-run price check without charging credits")
):
    """
    Search Instagram accounts (architects, interior designers, builders, suppliers, manufacturers) via SocialCrawl.
    Cost: 1 credit per page.
    Endpoint: GET /v1/instagram/search/profiles
    """
    clean_query = query.strip()
    if not clean_query:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Query cannot be empty.")

    if not is_socialcrawl_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SOCIALCRAWL_API_KEY environment variable is missing."
        )

    try:
        return search_instagram_profiles(
            query=clean_query,
            cursor=cursor,
            max_pages=max_pages or 1,
            dry_run=bool(dry_run)
        )
    except RuntimeError as err:
        err_msg = str(err)
        if "missing" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"SocialCrawl Instagram Profiles error: {err_msg}")
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Instagram profiles search failed: {str(err)}")


@router.get("/instagram/profile")
def get_instagram_profile_detail(
    handle: str = Query(..., min_length=1, max_length=100, description="Instagram username / handle"),
    dry_run: Optional[bool] = Query(False, description="Dry-run price check without charging credits")
):
    """
    Retrieve specific Instagram profile details via SocialCrawl (GET /v1/instagram/profile).
    Selective lookup for selected accounts discovered through search.
    Cost: 1 credit per call.
    """
    clean_handle = handle.strip().lstrip("@")
    if not clean_handle:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Handle cannot be empty.")

    if not is_socialcrawl_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SOCIALCRAWL_API_KEY environment variable is missing."
        )

    try:
        result = get_instagram_profile(
            handle=clean_handle,
            dry_run=bool(dry_run)
        )
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Instagram profile '@{clean_handle}' not found.")
        return result
    except HTTPException:
        raise
    except RuntimeError as err:
        err_msg = str(err)
        if "missing" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"SocialCrawl Instagram Profile error: {err_msg}")
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Instagram profile lookup failed: {str(err)}")


@router.get("/instagram/queries")
def get_focused_instagram_queries(
    term: str = Query(..., min_length=1, max_length=100, description="Keyword / category term"),
    target: Optional[str] = Query("all", description="Target: reels, profiles, or all")
):
    """
    Generates focused 2-4 word search queries for Instagram discovery.
    Connects Keyword Explorer terms to high-yield SocialCrawl queries.
    """
    return {
        "term": term,
        "target": target,
        "queries": generate_focused_instagram_queries(term, target=target or "all")
    }


@router.get("/youtube")
def get_youtube_videos(
    query: str = Query(..., min_length=1, max_length=300, description="Architectural search term"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    relevance: Optional[str] = Query("score", description="Relevance ranking metric"),
    max_pages: Optional[int] = Query(1, ge=1, le=10, description="Max pages to fetch"),
    dry_run: Optional[bool] = Query(False, description="Dry-run price check without charging credits")
):
    """
    Search architecture and interior design videos from YouTube via SocialCrawl.
    Cost: 1 credit per page.
    """
    clean_query = query.strip()
    if not clean_query:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Query cannot be empty.")

    if not is_socialcrawl_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SOCIALCRAWL_API_KEY environment variable is missing."
        )

    try:
        return search_youtube(
            query=clean_query,
            cursor=cursor,
            relevance=relevance or "score",
            max_pages=max_pages or 1,
            dry_run=bool(dry_run)
        )
    except RuntimeError as err:
        err_msg = str(err)
        if "missing" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"SocialCrawl YouTube error: {err_msg}")
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"YouTube search failed: {str(err)}")


@router.get("/reddit")
def get_reddit_discussions(
    query: str = Query(..., min_length=1, max_length=300, description="Architecture discussion keyword"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    relevance: Optional[str] = Query("score", description="Relevance ranking metric"),
    max_pages: Optional[int] = Query(1, ge=1, le=10, description="Max pages to fetch"),
    dry_run: Optional[bool] = Query(False, description="Dry-run price check without charging credits")
):
    """
    Search architecture-related community discussions from Reddit via SocialCrawl.
    Cost: 1 credit per page.
    """
    clean_query = query.strip()
    if not clean_query:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Query cannot be empty.")

    if not is_socialcrawl_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SOCIALCRAWL_API_KEY environment variable is missing."
        )

    try:
        return search_reddit(
            query=clean_query,
            cursor=cursor,
            relevance=relevance or "score",
            max_pages=max_pages or 1,
            dry_run=bool(dry_run)
        )
    except RuntimeError as err:
        err_msg = str(err)
        if "missing" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"SocialCrawl Reddit error: {err_msg}")
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Reddit search failed: {str(err)}")


@router.get("/twitter")
def get_twitter_posts(
    query: str = Query(..., min_length=1, max_length=300, description="Architectural search term"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    dry_run: Optional[bool] = Query(False, description="Dry-run price check without charging credits")
):
    """
    Search architectural inspiration and design releases on X (Twitter) via SocialCrawl AI-Search.
    Cost: 5 credits per call. Cache hits are free and failed calls refunded.
    """
    clean_query = query.strip()
    if not clean_query:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Query cannot be empty.")

    if not is_socialcrawl_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SOCIALCRAWL_API_KEY environment variable is missing."
        )

    try:
        return search_twitter_ai(
            query=clean_query,
            cursor=cursor,
            dry_run=bool(dry_run)
        )
    except RuntimeError as err:
        err_msg = str(err)
        if "missing" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"SocialCrawl X/Twitter error: {err_msg}")
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Twitter search failed: {str(err)}")


@router.get("/businesses")
def get_google_businesses(
    query: str = Query(..., min_length=1, max_length=300, description="Supplier / material query"),
    location: Optional[str] = Query("Kochi, Kerala, India", description="Location: Locality, City, State or City, Country"),
    lat: Optional[float] = Query(None, description="GPS Latitude"),
    lon: Optional[float] = Query(None, description="GPS Longitude"),
    dry_run: Optional[bool] = Query(False, description="Dry-run price check without charging credits")
):
    """
    Search manufacturers, suppliers, dealers, showrooms and contractors via Google Business.
    Cost: 5 credits per call.
    """
    clean_query = query.strip()
    if not clean_query:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Query cannot be empty.")

    if not is_socialcrawl_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SOCIALCRAWL_API_KEY environment variable is missing."
        )

    try:
        return search_google_business(
            query=clean_query,
            location=location,
            lat=lat,
            lon=lon,
            dry_run=bool(dry_run)
        )
    except RuntimeError as err:
        err_msg = str(err)
        if "missing" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"SocialCrawl Google Business error: {err_msg}")
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Business search failed: {str(err)}")


@router.get("/shopping")
def get_google_shopping_products(
    query: Optional[str] = Query(None, description="Search keyword for building materials / products"),
    gid: Optional[str] = Query(None, description="Google Shopping product GID identifier"),
    product_id: Optional[str] = Query(None, description="Specific product ID"),
    country: Optional[str] = Query("IN", description="Two-letter country code"),
    dry_run: Optional[bool] = Query(False, description="Dry-run price check without charging credits")
):
    """
    Search or lookup architectural products via Google Shopping.
    Supports gid parameter lookup (1 credit) and product keyword search (5 credits).
    """
    if not query and not gid and not product_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one of query, gid, or product_id must be provided."
        )

    if not is_socialcrawl_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SOCIALCRAWL_API_KEY environment variable is missing."
        )

    try:
        return search_google_shopping(
            query=query,
            gid=gid,
            product_id=product_id,
            country=country or "IN",
            dry_run=bool(dry_run)
        )
    except RuntimeError as err:
        err_msg = str(err)
        if "missing" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"SocialCrawl Shopping error: {err_msg}")
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Shopping search failed: {str(err)}")


@router.get("/search-all")
def search_all_endpoints(
    query: str = Query(..., min_length=1, max_length=300, description="Global search query"),
    sources: Optional[str] = Query(None, description="Comma-separated list of sources (instagram,youtube,reddit,businesses,shopping)"),
    location: Optional[str] = Query("Kochi, Kerala, India", description="Location for supplier searches"),
    dry_run: Optional[bool] = Query(False, description="Dry-run price check without charging credits")
):
    """
    Search across multiple SocialCrawl sources with independent error handling.
    A failure in one endpoint does not interrupt or stop other endpoints.
    """
    clean_query = query.strip()
    if not clean_query:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Query cannot be empty.")

    if not is_socialcrawl_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SOCIALCRAWL_API_KEY environment variable is missing."
        )

    source_list = [s.strip() for s in sources.split(",") if s.strip()] if sources else None
    res = search_all_sources(
        query=clean_query,
        sources=source_list,
        location=location,
        dry_run=bool(dry_run)
    )
    return {
        "success": True,
        "query": clean_query,
        "results": res,
        "errors": res.get("errors", {}),
        "instagram": res.get("instagram"),
        "youtube": res.get("youtube"),
        "reddit": res.get("reddit"),
        "google_business": res.get("google_business"),
        "google_shopping": res.get("google_shopping"),
    }


@router.post("/save")
def save_socialcrawl_item(
    item_in: SocialCrawlSaveIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save an item from any SocialCrawl source to the user's saved collection/moodboard.
    Creates an ArchitecturalReference if none exists, and links a SavedItem.
    """
    user_id = current_user.id

    # Check if reference already exists by source_url
    ref = db.query(ArchitecturalReference).filter_by(source_url=item_in.source_url).first()
    if not ref:
        ref_slug = f"{item_in.source_platform}-{item_in.external_id or str(abs(hash(item_in.source_url)))[:10]}"
        ref = ArchitecturalReference(
            title=item_in.title or f"{item_in.source_platform.capitalize()} Architectural Reference",
            slug=ref_slug,
            source_platform=item_in.source_platform,
            source_url=item_in.source_url,
            creator_name=item_in.creator_name,
            creator_url=item_in.creator_url,
            thumbnail_url=item_in.image_url,
            media_url=item_in.video_url or item_in.image_url,
            video_embed_id=item_in.external_id if item_in.source_platform == "youtube" else None,
            inspiration_image_url=item_in.image_url,
            inspiration_source_url=item_in.source_url,
            source_domain=f"{item_in.source_platform}.com",
            material_tags=item_in.material_tags,
            description=item_in.description,
            verification_status="UNVERIFIED",
            provenance_notes=f"Saved from SocialCrawl {item_in.source_platform.capitalize()} search."
        )
        db.add(ref)
        db.commit()
        db.refresh(ref)

    # Check if already saved by user
    saved = db.query(SavedItem).filter_by(
        user_id=user_id,
        item_type="reference",
        reference_id=ref.id
    ).first()

    if saved:
        # Toggle: unsave
        db.delete(saved)
        db.commit()
        return {
            "saved": False,
            "reference_id": ref.id,
            "status": "removed",
            "message": "Item removed from collection."
        }
    else:
        # Save
        new_saved = SavedItem(
            user_id=user_id,
            item_type="reference",
            reference_id=ref.id,
            project_collection=item_in.project_collection or "Moodboard"
        )
        db.add(new_saved)
        db.commit()
        return {
            "saved": True,
            "reference_id": ref.id,
            "status": "saved",
            "message": "Item saved to collection."
        }

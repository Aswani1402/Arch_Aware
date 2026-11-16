from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User, ArchitecturalReference, SavedItem
from app.services.pinterest_service import (
    search_pinterest_page,
    is_socialcrawl_configured,
    get_socialcrawl_api_key,
    PINTEREST_CATEGORIES,
    _CACHE
)

router = APIRouter(prefix="/pinterest", tags=["Pinterest Inspiration (SocialCrawl)"])


class PinterestSaveIn(BaseModel):
    pin_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: str = Field(..., description="High-resolution pin image URL")
    source_url: str = Field(..., description="Original Pinterest pin URL")
    creator_name: Optional[str] = None
    creator_url: Optional[str] = None
    category_slug: Optional[str] = None
    material_tags: Optional[str] = None
    project_collection: Optional[str] = "Moodboard"


@router.get("/status")
def get_pinterest_status():
    """
    Return whether the SocialCrawl Pinterest API key is configured.
    Never returns the key itself.
    """
    configured = is_socialcrawl_configured()
    return {
        "configured": configured,
        "provider": "SocialCrawl",
        "endpoint": "https://www.socialcrawl.dev/v1/pinterest/search",
        "timeout_seconds": 14,
        "max_retries": 3,
        "max_pages": 10,
        "cached_queries_count": len(_CACHE),
        "message": (
            "SocialCrawl Pinterest API is configured and ready."
            if configured
            else "SOCIALCRAWL_API_KEY environment variable is missing. Live search is inactive until configured."
        )
    }


@router.get("/categories")
def get_pinterest_categories():
    """
    Returns the 28 Architect AI categories configured with focused search queries.
    Allows users to browse category-specific architectural inspiration.
    """
    return {
        "total": len(PINTEREST_CATEGORIES),
        "categories": PINTEREST_CATEGORIES
    }


@router.get("/search")
def search_pinterest_endpoint(
    query: str = Query(..., min_length=1, max_length=300, description="Search keyword or category term"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    relevance: Optional[str] = Query("score", description="Relevance score or filter"),
    trim: Optional[bool] = Query(False, description="Trim search responses"),
    label: Optional[str] = Query(None, description="Optional sponsored label"),
    dry_run: Optional[bool] = Query(False, description="Dry-run price check without fetching or charging credits")
):
    """
    Search Pinterest via SocialCrawl API.
    Requirements:
    - Explicit user-triggered searches only.
    - Validate inputs strictly and handle provider failures safely.
    - Do not allow arbitrary external URLs or user-controlled API endpoints.
    - Support cursor-based pagination.
    - Support dry_run=1 for price checking without fetching or charging.
    """
    # Strict validation of search query
    clean_query = query.strip()
    if not clean_query:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Search query cannot be empty or whitespace."
        )

    # Check API key configuration
    if not is_socialcrawl_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SOCIALCRAWL_API_KEY environment variable is missing. Please configure it in your environment."
        )

    try:
        result = search_pinterest_page(
            query=clean_query,
            cursor=cursor,
            relevance=relevance or "score",
            trim=trim if trim is not None else False,
            label=label,
            dry_run=bool(dry_run)
        )
        return result

    except RuntimeError as err:
        err_msg = str(err)
        # Safe error formatting without exposing API keys
        if "missing" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"SocialCrawl Pinterest API error: {err_msg}")

    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Search request failed: {str(err)}")


@router.post("/save")
def toggle_save_pinterest_pin(
    item_in: PinterestSaveIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save or unsave a Pinterest pin to user's saved items / moodboard.
    Seamlessly integrates with the existing ArchitecturalReference and SavedItem tables.
    """
    user_id = current_user.id

    # Ensure a corresponding ArchitecturalReference exists
    ref = db.query(ArchitecturalReference).filter_by(source_url=item_in.source_url).first()
    if not ref:
        pin_slug = f"pinterest-{item_in.pin_id or str(abs(hash(item_in.source_url)))[:10]}"
        ref = ArchitecturalReference(
            title=item_in.title or "Pinterest Architectural Inspiration",
            slug=pin_slug,
            source_platform="pinterest",
            source_url=item_in.source_url,
            creator_name=item_in.creator_name,
            creator_url=item_in.creator_url,
            thumbnail_url=item_in.image_url,
            media_url=item_in.image_url,
            inspiration_image_url=item_in.image_url,
            inspiration_source_url=item_in.source_url,
            source_domain="pinterest.com",
            image_attribution=f"Pinterest Pin / {item_in.creator_name or 'Architectural Reference'}",
            verification_status="UNVERIFIED",
            description=item_in.description,
            material_tags=item_in.material_tags,
            content_type="architectural_project",
            retrieval_method="api_sync"
        )
        db.add(ref)
        db.commit()
        db.refresh(ref)

    # Check if already saved by this user
    existing_save = db.query(SavedItem).filter_by(
        user_id=user_id,
        item_type="reference",
        reference_id=ref.id
    ).first()

    if existing_save:
        db.delete(existing_save)
        db.commit()
        return {
            "saved": False,
            "reference_id": ref.id,
            "status": "unsaved",
            "message": "Pinterest pin removed from your saved collection."
        }
    else:
        new_save = SavedItem(
            user_id=user_id,
            item_type="reference",
            reference_id=ref.id,
            project_collection=item_in.project_collection or "Moodboard"
        )
        db.add(new_save)
        db.commit()
        return {
            "saved": True,
            "reference_id": ref.id,
            "status": "saved",
            "message": "Pinterest pin saved to your moodboard collection."
        }

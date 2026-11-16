"""
Nivora — Stage 3 Unified Multi-Source Discovery API Router

Exposes GET and POST /api/discovery/search backed by SearchOrchestrationService,
strict optional JWT authentication, trusted-proxy IP resolution, atomic rate/budget guards,
catalogue context matching, and bounded zero-credit cache-first retrieval.
"""

from typing import Any, Dict, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_optional_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.models import User
from app.schemas.discovery import (
    DiscoveryOverallStatusEnum,
    DiscoveryTabEnum,
    UnifiedDiscoveryResponse,
)
from app.services.catalogue_import_service import search_catalogue_materials
from app.services.discovery_cache import discovery_cache
from app.services.discovery_guard import (
    discovery_request_guard,
    extract_verified_client_ip,
    provider_budget_manager,
)
from app.services.search_orchestration_service import search_orchestration_service

router = APIRouter(prefix="/discovery", tags=["Unified Multi-Source Discovery"])

# Exactly the 5 active inspiration sources for all-sources discovery feed
INSPIRATION_DISCOVERY_SOURCES = [
    "pinterest",
    "instagram",
    "youtube",
    "reddit",
    "google_shopping",
]

ALL_DISCOVERY_SOURCES = [
    "pinterest",
    "instagram",
    "youtube",
    "reddit",
    "google_shopping",
    "google_places",
    "google_search",
]


class DiscoverySearchRequest(BaseModel):
    q: str = Field(..., min_length=1, max_length=300)
    sources: Optional[List[str]] = None
    tab: DiscoveryTabEnum = DiscoveryTabEnum.ALL
    category: Optional[str] = None
    subcategory: Optional[str] = None
    material: Optional[str] = None
    material_id: Optional[int] = None
    aliases: Optional[List[str]] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    page: int = Field(1, ge=1, le=20)
    page_size: int = Field(30, ge=1, le=100)
    target_per_source: int = Field(15, ge=1, le=30)
    query_expansions: int = Field(1, ge=1, le=5)
    dry_run: bool = False
    refresh: bool = False


def _normalize_sources_param(raw_sources: Optional[List[str]]) -> List[str]:
    if not raw_sources:
        return list(INSPIRATION_DISCOVERY_SOURCES)
    parsed: List[str] = []
    for entry in raw_sources:
        for token in str(entry).split(","):
            cleaned = token.strip().lower()
            if not cleaned:
                continue
            if cleaned == "all":
                return list(INSPIRATION_DISCOVERY_SOURCES)
            parsed.append(cleaned)
    return parsed or list(INSPIRATION_DISCOVERY_SOURCES)


def _enrich_taxonomy_context(
    db: Session,
    clean_query: str,
    category: Optional[str],
    subcategory: Optional[str],
    material: Optional[str],
    city: Optional[str],
    state: Optional[str],
) -> Dict[str, Any]:
    ctx = dict(search_orchestration_service.resolve_taxonomy_context(clean_query) or {})
    ctx["exact_keyword"] = clean_query
    ctx["normalized_keyword"] = " ".join(clean_query.lower().split())
    if category:
        ctx["filter_category"] = category
        ctx["category"] = category
    if subcategory:
        ctx["filter_subcategory"] = subcategory
        ctx["subcategory"] = subcategory
    if material:
        ctx["filter_material"] = material
        ctx["material"] = material
    if city:
        ctx["city"] = city
    if state:
        ctx["state"] = state
    ctx["location_hierarchy"] = [p for p in [city, state, "India"] if p and str(p).strip()]

    # Attach non-blocking CSV catalogue context matches if tables exist
    try:
        cat_lookup = search_catalogue_materials(
            db,
            q=material or clean_query,
            category=category,
            subcategory=subcategory,
            limit=5,
        )
        if cat_lookup.get("items"):
            ctx["catalogue_matches_count"] = cat_lookup["total"]
            ctx["catalogue_top_match"] = cat_lookup["items"][0]
    except Exception:
        pass
    return ctx


async def _execute_discovery(
    request: Request,
    db: Session,
    current_user: Optional[User],
    q: str,
    sources_list: List[str],
    tab: DiscoveryTabEnum,
    category: Optional[str],
    subcategory: Optional[str],
    material: Optional[str],
    city: Optional[str],
    state: Optional[str],
    lat: Optional[float],
    lon: Optional[float],
    page: int,
    page_size: int,
    target_per_source: int,
    query_expansions: int,
    dry_run: bool,
    refresh: bool,
    material_id: Optional[int] = None,
):
    clean_q = q.strip()
    if not clean_q:
        raise HTTPException(
            status_code=422,
            detail="Search query cannot be empty or whitespace.",
        )

    client_ip = extract_verified_client_ip(request, trusted_proxies=settings.TRUSTED_PROXIES)
    user_id = str(current_user.id) if current_user is not None else None
    is_authenticated = current_user is not None

    cache_key = discovery_cache.build_key(
        query=clean_q,
        sources=sources_list,
        tab=tab.value if isinstance(tab, DiscoveryTabEnum) else str(tab),
        category=category,
        subcategory=subcategory,
        material=material,
        city=city,
        state=state,
        page=page,
        page_size=page_size,
    )

    if not dry_run and not refresh:
        cached_payload = discovery_cache.get(cache_key)
        if cached_payload is not None:
            # Apply HTTP rate limit without spending any provider credits
            guard_dec = discovery_request_guard.check_http_request(
                request,
                current_user=current_user,
                trusted_proxies=settings.TRUSTED_PROXIES,
            )
            if not guard_dec.allowed:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": guard_dec.reason,
                        "retry_after_seconds": guard_dec.retry_after_seconds,
                    },
                    headers={"Retry-After": str(guard_dec.retry_after_seconds or 60)},
                )
            provider_budget_manager.check_budget(sources_list, page=page, query_expansions=query_expansions, cached=True)
            hit_copy = dict(cached_payload)
            hit_copy["request_id"] = f"disc_cache_{uuid.uuid4().hex[:10]}"
            hit_warnings = list(hit_copy.get("warnings") or [])
            cache_note = "Served from bounded discovery cache (0 provider credits consumed)."
            if cache_note not in hit_warnings:
                hit_warnings.append(cache_note)
            hit_copy["warnings"] = hit_warnings
            return UnifiedDiscoveryResponse.model_validate(hit_copy)

    taxonomy_context = _enrich_taxonomy_context(
        db=db,
        clean_query=clean_q,
        category=category,
        subcategory=subcategory,
        material=material,
        city=city,
        state=state,
    )

    resp = await search_orchestration_service.orchestrate_discovery_async(
        query=clean_q,
        sources=sources_list,
        tab=tab,
        page=page,
        page_size=page_size,
        target_per_source=target_per_source,
        dry_run=dry_run,
        taxonomy_context=taxonomy_context,
        city=city,
        lat=lat,
        lon=lon,
        user_id=user_id,
        client_ip=client_ip,
        is_authenticated=is_authenticated,
        enforce_guard=True,
        query_expansions=query_expansions,
    )

    if resp.overall_status == DiscoveryOverallStatusEnum.RATE_LIMITED:
        retry_after = 60
        for err in resp.errors:
            if err.get("guard") == "rate_limit" and err.get("retry_after_seconds"):
                retry_after = int(err["retry_after_seconds"])
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content=resp.model_dump(mode="json"),
                    headers={"Retry-After": str(retry_after)},
                )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=resp.model_dump(mode="json"),
        )

    if not dry_run and resp.overall_status in (
        DiscoveryOverallStatusEnum.SUCCESS,
        DiscoveryOverallStatusEnum.PARTIAL_SUCCESS,
        DiscoveryOverallStatusEnum.EMPTY,
    ):
        discovery_cache.set(cache_key, resp.model_dump(mode="json"))

    return resp


@router.get("/search", response_model=UnifiedDiscoveryResponse)
async def discovery_search_get(
    request: Request,
    q: str = Query(..., min_length=1, max_length=300, description="Architectural keyword, material, style, or brand"),
    sources: Optional[str] = Query(None, description="Comma-separated source names or 'all'"),
    tab: DiscoveryTabEnum = Query(DiscoveryTabEnum.ALL, description="Discovery journey tab"),
    category: Optional[str] = Query(None, description="Optional category filter"),
    subcategory: Optional[str] = Query(None, description="Optional subcategory filter"),
    material: Optional[str] = Query(None, description="Optional CSV catalogue material name"),
    material_id: Optional[int] = Query(None, description="Optional catalogue material ID"),
    aliases: Optional[str] = Query(None, description="Comma-separated material aliases"),
    city: Optional[str] = Query(None, description="Optional sourcing city"),
    district: Optional[str] = Query(None, description="Optional sourcing district"),
    state: Optional[str] = Query(None, description="Optional sourcing state"),
    lat: Optional[float] = Query(None, description="Optional latitude"),
    lon: Optional[float] = Query(None, description="Optional longitude"),
    page: int = Query(1, ge=1, le=20),
    page_size: int = Query(30, ge=1, le=100),
    target_per_source: int = Query(15, ge=1, le=30),
    query_expansions: int = Query(1, ge=1, le=5),
    dry_run: bool = Query(False),
    refresh: bool = Query(False),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    sources_list = _normalize_sources_param([sources] if sources else None)
    return await _execute_discovery(
        request=request,
        db=db,
        current_user=current_user,
        q=q,
        sources_list=sources_list,
        tab=tab,
        category=category,
        subcategory=subcategory,
        material=material,
        material_id=material_id,
        city=city,
        state=state,
        lat=lat,
        lon=lon,
        page=page,
        page_size=page_size,
        target_per_source=target_per_source,
        query_expansions=query_expansions,
        dry_run=dry_run,
        refresh=refresh,
    )


@router.post("/search", response_model=UnifiedDiscoveryResponse)
async def discovery_search_post(
    request: Request,
    payload: DiscoverySearchRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    sources_list = _normalize_sources_param(payload.sources)
    return await _execute_discovery(
        request=request,
        db=db,
        current_user=current_user,
        q=payload.q,
        sources_list=sources_list,
        tab=payload.tab,
        category=payload.category,
        subcategory=payload.subcategory,
        material=payload.material,
        city=payload.city,
        state=payload.state,
        lat=payload.lat,
        lon=payload.lon,
        page=payload.page,
        page_size=payload.page_size,
        target_per_source=payload.target_per_source,
        query_expansions=payload.query_expansions,
        dry_run=payload.dry_run,
        refresh=payload.refresh,
    )


@router.get("/status")
def get_discovery_engine_status():
    """
    Returns non-secret operational telemetry for the unified discovery engine:
    rate guard state, provider credit budget, bounded cache stats, and adapter readiness.
    """
    adapters_status = {
        name: {"configured": adapter.is_configured()}
        for name, adapter in search_orchestration_service.adapters.items()
    }
    adapters_status["x"] = {"configured": False, "disabled": True}
    return {
        "engine": "Nivora Multi-Source Discovery Engine",
        "sources": adapters_status,
        "rate_guard": discovery_request_guard.get_status(),
        "budget": provider_budget_manager.get_status(),
        "cache": discovery_cache.stats(),
    }

import os
import random
import time
import uuid
import logging
from typing import Dict, List, Any, Optional, Tuple
import requests

from app.core.config import settings

logger = logging.getLogger(__name__)

URL = "https://www.socialcrawl.dev/v1/pinterest/search"
TIMEOUT_S = 14
MAX_RETRIES = 3
MAX_PAGES = 10

# In-memory cache for search responses: key -> (timestamp, response_data)
# Prevents repeated billing on identical queries within cache TTL (1 hour)
_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 3600

# 28 Curated Architect AI Search Categories with focused, high-precision search queries
PINTEREST_CATEGORIES: List[Dict[str, str]] = [
    {
        "id": "arch-building-design",
        "name": "Architecture and Building Design",
        "query": "architectural design building",
        "section": "Typologies",
        "description": "Architectural forms, structural concepts, and contemporary residential and commercial building design."
    },
    {
        "id": "exterior-facade",
        "name": "Exterior and Facade Design",
        "query": "exterior facade design modern",
        "section": "Envelopes",
        "description": "Building envelopes, front elevations, louvers, dynamic screens, and weather envelopes."
    },
    {
        "id": "interior-design",
        "name": "Interior Design",
        "query": "interior architecture design",
        "section": "Interiors",
        "description": "Holistic interior architecture, spatial planning, natural lighting, and curated aesthetics."
    },
    {
        "id": "living-rooms",
        "name": "Living Rooms",
        "query": "living room architectural design",
        "section": "Spaces",
        "description": "Double-height living rooms, formal sitting areas, courtyard connectivity, and seating layouts."
    },
    {
        "id": "bedrooms",
        "name": "Bedrooms",
        "query": "modern bedroom architecture",
        "section": "Spaces",
        "description": "Master bedroom suites, ambient lighting, headboard details, and peaceful architectural retreats."
    },
    {
        "id": "kitchens",
        "name": "Kitchens",
        "query": "modern kitchen architecture",
        "section": "Spaces",
        "description": "Modular kitchens, quartz islands, pantry storage, concealed handles, and task lighting."
    },
    {
        "id": "bathrooms",
        "name": "Bathrooms",
        "query": "luxury bathroom architecture",
        "section": "Spaces",
        "description": "Minimalist washrooms, walk-in showers, freestanding bathtubs, fluted glass, and vanity design."
    },
    {
        "id": "building-materials",
        "name": "Building Materials",
        "query": "architectural materials texture",
        "section": "Materials",
        "description": "Tactile architectural materials, raw finishes, sustainable composites, and structural components."
    },
    {
        "id": "stone-marble",
        "name": "Stone and Marble",
        "query": "natural stone marble architecture",
        "section": "Materials",
        "description": "Italian marble, Indian Makrana, honed granite, limestone, and architectural stone masonry."
    },
    {
        "id": "wood-timber",
        "name": "Wood and Timber",
        "query": "wood timber architecture",
        "section": "Materials",
        "description": "Malabar teak, hardwood rafters, louvers, timber screens, and natural wood cladding."
    },
    {
        "id": "bricks-blocks",
        "name": "Bricks and Blocks",
        "query": "exposed brick architecture",
        "section": "Materials",
        "description": "Exposed wire-cut clay bricks, terracotta jaali, rat-trap bond masonry, and AAC block systems."
    },
    {
        "id": "cement-concrete",
        "name": "Cement and Concrete",
        "query": "exposed concrete architecture",
        "section": "Materials",
        "description": "Board-formed concrete, microcement surfaces, polished screed, and structural concrete frames."
    },
    {
        "id": "tiles-flooring",
        "name": "Tiles and Flooring",
        "query": "architectural tiles flooring",
        "section": "Finishes",
        "description": "Vitrified porcelain slabs, Athangudi handmade tiles, terrazzo flooring, and wooden parquet."
    },
    {
        "id": "glass-metal",
        "name": "Glass and Metal",
        "query": "architectural glass metal facade",
        "section": "Finishes",
        "description": "Double-glazed Low-E units, fluted glass, blackened steel, anodized aluminium, and brass accents."
    },
    {
        "id": "paint-colour-combos",
        "name": "Paint and Colour Combinations",
        "query": "architectural colour palette",
        "section": "Finishes",
        "description": "Curated architectural colour palettes, mineral limewashes, earth tones, and warm neutrals."
    },
    {
        "id": "walls-ceiling-finishes",
        "name": "Walls and Ceiling Finishes",
        "query": "textured wall finishes architecture",
        "section": "Finishes",
        "description": "Lime plaster, stucco render, wooden slatted false ceilings, cove troughs, and acoustic panelling."
    },
    {
        "id": "doors-windows",
        "name": "Doors and Windows",
        "query": "architectural doors and windows",
        "section": "Envelopes",
        "description": "Pivot entry doors, carved timber portals, minimal aluminium sliding frames, and french casements."
    },
    {
        "id": "staircases",
        "name": "Staircases",
        "query": "architectural staircase design",
        "section": "Circulation",
        "description": "Cantilever floating treads, steel spine staircases, timber stringers, and sculptural railings."
    },
    {
        "id": "lighting-electrical",
        "name": "Lighting and Electrical Fixtures",
        "query": "architectural lighting design",
        "section": "Services",
        "description": "Concealed 2700K warm coves, magnetic track fixtures, recessed dark-light downlights, and chandeliers."
    },
    {
        "id": "furniture",
        "name": "Furniture",
        "query": "architectural furniture design",
        "section": "Interiors",
        "description": "Bespoke architectural furniture, floating credenzas, solid wood dining tables, and upholstered seating."
    },
    {
        "id": "landscaping-gardens",
        "name": "Landscaping and Gardens",
        "query": "landscape architecture courtyard",
        "section": "Landscape",
        "description": "Central courtyards, koi ponds, granite boulder water features, stepping pavers, and pergolas."
    },
    {
        "id": "construction-techniques",
        "name": "Construction Techniques",
        "query": "architectural construction craftsmanship",
        "section": "Craftsmanship",
        "description": "Traditional joinery, passive solar orientations, earthquake resistance, and masonry detailing."
    },
    {
        "id": "architectural-details",
        "name": "Architectural Details",
        "query": "architectural joinery details",
        "section": "Craftsmanship",
        "description": "Material junction thresholds, shadow gaps, reveal beads, sill flushings, and junction articulation."
    },
    {
        "id": "architectural-styles",
        "name": "Architectural Styles",
        "query": "architectural styles modern",
        "section": "Typologies",
        "description": "Tropical Modernism, Brutalism, Minimalist, Scandinavian, and Contemporary Asian styles."
    },
    {
        "id": "commercial-spaces",
        "name": "Commercial Spaces",
        "query": "commercial architecture interior",
        "section": "Typologies",
        "description": "Architectural boutique cafes, retail showrooms, co-working studios, and corporate headquarters."
    },
    {
        "id": "products-manufacturers",
        "name": "Products and Manufacturers",
        "query": "architectural fixtures products",
        "section": "Products",
        "description": "Commercial architectural fittings, sanitaryware, modular hardware, and specification products."
    },
    {
        "id": "sustainable-architecture",
        "name": "Sustainable Architecture",
        "query": "sustainable architecture green building",
        "section": "Sustainability",
        "description": "Passive cross-ventilation, rainwater harvesting, rammed earth, low-carbon CSEB, and cool roofs."
    },
    {
        "id": "indian-kerala-architecture",
        "name": "Indian and Kerala Architecture",
        "query": "Kerala architecture modern courtyard",
        "section": "Regional",
        "description": "Traditional Kerala Nalukettu courtyards, sloped clay tile roofs, wooden gables, and tropical verandahs."
    }
]


def get_socialcrawl_api_key() -> str:
    """
    Read the API key exclusively from environment variables or backend settings.
    Never hardcode or expose. Dynamically resolves from .env and backend/.env as fallback.
    """
    key = os.environ.get("SOCIALCRAWL_API_KEY") or settings.get_socialcrawl_api_key()
    if not key:
        # Dynamically inspect .env files to support hot-saving without restarting
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        root_dir = os.path.dirname(base_dir)
        for env_file in [os.path.join(base_dir, ".env"), os.path.join(root_dir, ".env"), ".env", "backend/.env"]:
            if os.path.exists(env_file):
                try:
                    with open(env_file, "r", encoding="utf-8") as f:
                        for line in f:
                            sline = line.strip()
                            if sline.startswith("SOCIALCRAWL_API_KEY=") and not sline.startswith("#"):
                                val = sline.split("=", 1)[1].strip().strip('"\'')
                                if val:
                                    return val
                except Exception:
                    pass
    return key or ""


def is_socialcrawl_configured() -> bool:
    """Return whether the SocialCrawl API key is configured."""
    key = get_socialcrawl_api_key()
    return bool(key and key.strip())


def backoff(attempt: int) -> float:
    """Exponential backoff with jitter."""
    return 2 ** attempt * (0.5 + random.random() / 2)


def socialcrawl(params: Dict[str, Any], api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Core SocialCrawl Pinterest Search API client implementation.
    Requirements:
    - Use requests.
    - 14-second timeout.
    - Exponential backoff with jitter.
    - Max 3 retries after the initial attempt.
    - Reuse the same Idempotency-Key across retries of a request.
    - Handle API errors using error.type and error.retryable.
    - Respect Retry-After.
    - Handle RESOURCE_NOT_FOUND.
    """
    resolved_key = api_key or get_socialcrawl_api_key()
    if not resolved_key:
        raise RuntimeError(
            "SOCIALCRAWL_API_KEY environment variable is missing."
        )

    # Reuse the same Idempotency-Key across all retries of this request
    idempotency_key = str(uuid.uuid4())

    for attempt in range(MAX_RETRIES + 1):
        try:
            res = requests.get(
                URL,
                params=params,
                headers={
                    "x-api-key": resolved_key,
                    "Idempotency-Key": idempotency_key,
                },
                timeout=TIMEOUT_S,
            )

            body = res.json()

        except (requests.RequestException, ValueError) as err:
            if attempt == MAX_RETRIES:
                logger.error(f"SocialCrawl request failed on attempt {attempt}: {err}")
                raise

            time.sleep(backoff(attempt))
            continue

        if body.get("success"):
            return body

        error = body.get("error", {})
        error_type = error.get("type", "UNKNOWN_ERROR")

        if error_type == "RESOURCE_NOT_FOUND":
            return None

        retry_after = res.headers.get("Retry-After")

        permanent = (
            error_type == "SERVICE_UNAVAILABLE"
            and retry_after is None
        )

        if (
            not error.get("retryable")
            or permanent
            or attempt == MAX_RETRIES
        ):
            raise RuntimeError(
                f"{error_type}: {error.get('message', 'Unknown error')} "
                f"(request_id {body.get('request_id')})"
            )

        time.sleep(
            float(retry_after)
            if retry_after
            else backoff(attempt)
        )

    raise RuntimeError("Pinterest API request failed.")


def normalize_pinterest_pin(raw_item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a SocialCrawl Pinterest search item into a standard Architect AI visual reference.
    Enforces attribution and data integrity:
    - Supports both SocialCrawl canonical format (wrapped in 'post') and flat schemas.
    - Preserves original pin image URL and video duration if available.
    - Preserves pin title, if available (never invents missing titles).
    - Preserves pin description, if available.
    - Preserves creator name and profile URL, if available.
    - Retains original Pinterest pin URL.
    - Clearly marks source as Pinterest content.
    - Explicitly marks verification_status as UNVERIFIED to avoid falsely representing it
      as a manufacturer-verified product or material spec.
    """
    post = raw_item.get("post") if isinstance(raw_item.get("post"), dict) else raw_item
    content = post.get("content") if isinstance(post.get("content"), dict) else {}
    author = post.get("author") if isinstance(post.get("author"), dict) else (raw_item.get("author") or {})
    ext = post.get("ext") if isinstance(post.get("ext"), dict) else (raw_item.get("ext") or {})

    # Source URL: original Pinterest pin link
    source_url = post.get("url") or raw_item.get("url") or raw_item.get("link")

    # Pin ID: resolve from post.id, raw_item.id, or URL
    pin_id = str(post.get("id") or raw_item.get("id") or raw_item.get("pin_id") or "")
    if (not pin_id or pin_id == "None") and source_url and "/pin/" in source_url:
        pin_id = source_url.rstrip("/").split("/")[-1].split("?")[0]
    if not source_url and pin_id:
        source_url = f"https://www.pinterest.com/pin/{pin_id}/"
    elif not source_url:
        source_url = "https://www.pinterest.com"

    # Image URL: inspect media_urls, thumbnail_url, or nested image objects
    media = content.get("media_urls")
    if isinstance(media, list) and media:
        image_url = media[0]
    elif isinstance(media, str) and media:
        image_url = media
    else:
        images_dict = raw_item.get("images") if isinstance(raw_item.get("images"), dict) else {}
        image_url = (
            content.get("thumbnail_url")
            or raw_item.get("image_url")
            or (images_dict.get("orig", {}).get("url") if isinstance(images_dict.get("orig"), dict) else None)
            or (images_dict.get("736x", {}).get("url") if isinstance(images_dict.get("736x"), dict) else None)
            or (images_dict.get("large", {}).get("url") if isinstance(images_dict.get("large"), dict) else None)
            or raw_item.get("image")
            or raw_item.get("media_url")
            or raw_item.get("thumbnail_url")
        )
    if isinstance(image_url, dict):
        image_url = image_url.get("url")

    thumbnail_url = content.get("thumbnail_url") or image_url

    # Video details
    duration_seconds = content.get("duration_seconds")
    is_video = bool(duration_seconds and float(duration_seconds) > 0)
    video_duration = None
    if is_video and duration_seconds:
        secs = int(float(duration_seconds))
        video_duration = f"{secs // 60}:{secs % 60:02d}"

    # Title: Keep existing text/title, never invent fake names
    title = (
        content.get("text")
        or post.get("title")
        or raw_item.get("title")
        or raw_item.get("grid_title")
        or ext.get("alt_text")
    )
    if isinstance(title, str):
        title = title.strip() or None

    # Description
    description = (
        raw_item.get("description")
        or raw_item.get("note")
        or ext.get("alt_text")
        or ext.get("board_name")
    )
    if isinstance(description, str):
        description = description.strip() or None
        if description == title:
            description = None

    # Creator information
    pinner = raw_item.get("pinner") or raw_item.get("creator") or author
    creator_name = None
    creator_url = None
    if isinstance(pinner, dict):
        creator_name = pinner.get("display_name") or pinner.get("name") or pinner.get("username") or None
        username = pinner.get("username")
        creator_url = (
            f"https://www.pinterest.com/{username}/" if username
            else pinner.get("url") or pinner.get("profile_image_url")
        )
    elif isinstance(pinner, str):
        creator_name = pinner

    if not creator_name:
        creator_name = raw_item.get("creator_name") or (raw_item.get("board", {}).get("name") if isinstance(raw_item.get("board"), dict) else None)

    return {
        "id": pin_id or str(uuid.uuid4()),
        "pin_id": pin_id,
        "title": title,
        "description": description,
        "image_url": image_url,
        "thumbnail_url": thumbnail_url,
        "source_url": source_url,
        "creator_name": creator_name,
        "creator_url": creator_url,
        "is_video": is_video,
        "video_duration": video_duration,
        "source_platform": "pinterest",
        "source_label": "Pinterest",
        "attribution_notice": "Pinterest visual reference via SocialCrawl. Pins are inspirational architectural references and do not represent verified manufacturer products or specifications.",
        "verification_status": "UNVERIFIED",
        "content_type": "architectural_project"
    }


def search_pinterest_page(
    query: str,
    cursor: Optional[str] = None,
    relevance: str = "score",
    trim: bool = False,
    label: Optional[str] = None,
    dry_run: bool = False,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Searches SocialCrawl Pinterest Search API for a single page with cursor pagination.
    Supports dry_run=1 for price checking without fetching results or burning credits.
    Caches successful non-dry-run searches to protect against duplicate credit usage.
    """
    clean_query = query.strip() if query else ""
    if not clean_query:
        return {
            "success": True,
            "dry_run": dry_run,
            "query": "",
            "items": [],
            "has_more": False,
            "next_cursor": None,
            "total_items": 0
        }

    params: Dict[str, Any] = {
        "query": clean_query,
        "relevance": relevance or "score",
        "trim": "false" if not trim else "true",
    }
    if cursor:
        params["cursor"] = cursor
    if label:
        params["label"] = label

    # Check cache for non-dry-run calls
    cache_key = f"{clean_query.lower()}:{cursor or ''}:{relevance}:{trim}:{label or ''}"
    if not dry_run and cache_key in _CACHE:
        timestamp, cached_result = _CACHE[cache_key]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            logger.info(f"Returning cached Pinterest results for query '{clean_query}'")
            return cached_result

    if dry_run:
        params["dry_run"] = 1
        logger.info(f"Executing SocialCrawl dry-run price check for query '{clean_query}'")
        raw_result = socialcrawl(params, api_key=api_key)
        return {
            "success": True,
            "dry_run": True,
            "query": clean_query,
            "items": [],
            "has_more": False,
            "next_cursor": None,
            "total_items": 0,
            "dry_run_details": raw_result or {
                "message": "Dry-run succeeded. No credits deducted.",
                "price_estimate": "0 credits (dry_run mode)"
            }
        }

    raw_result = socialcrawl(params, api_key=api_key)

    if raw_result is None:
        return {
            "success": True,
            "dry_run": False,
            "query": clean_query,
            "items": [],
            "has_more": False,
            "next_cursor": None,
            "total_items": 0
        }

    data = raw_result.get("data", {})
    raw_items = data.get("items", [])
    pagination = raw_result.get("pagination") or {}

    has_more = bool(pagination.get("has_more"))
    next_cursor = pagination.get("next_cursor")

    normalized_items = [normalize_pinterest_pin(it) for it in raw_items if isinstance(it, dict)]

    result_payload = {
        "success": True,
        "dry_run": False,
        "query": clean_query,
        "cursor": cursor,
        "next_cursor": next_cursor,
        "has_more": has_more,
        "total_items": len(normalized_items),
        "items": normalized_items,
        "request_id": raw_result.get("request_id")
    }

    # Cache successful page
    _CACHE[cache_key] = (time.time(), result_payload)

    return result_payload


def search_pinterest(
    query: str,
    relevance: str = "score",
    trim: bool = False,
    dry_run: bool = False,
    max_pages: int = MAX_PAGES,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Multi-page search utility following the provided reference implementation.
    Stops when has_more is False, cursor is absent, or max_pages is reached.
    """
    params: Dict[str, Any] = {
        "query": query,
        "relevance": relevance,
        "trim": "false" if not trim else "true",
    }

    if dry_run:
        params["dry_run"] = 1
        logger.info("Running SocialCrawl dry-run price check...")
        result = socialcrawl(params, api_key=api_key)
        if result is not None:
            logger.info(f"Dry-run response: {result}")
        return []

    items: List[Dict[str, Any]] = []

    for page_number in range(min(max_pages, MAX_PAGES)):
        result = socialcrawl(params, api_key=api_key)
        if result is None:
            break

        data = result.get("data", {})
        raw_items = data.get("items", [])
        items.extend([normalize_pinterest_pin(it) for it in raw_items if isinstance(it, dict)])

        pagination = result.get("pagination") or {}
        if not pagination.get("has_more") or not pagination.get("next_cursor"):
            break

        params["cursor"] = pagination["next_cursor"]

    return items

import re
import os
import random
import time
import uuid
import logging
from typing import Any, Optional, Dict, List, Tuple

import requests
from app.core.config import settings

logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://www.socialcrawl.dev/v1"

MAX_RETRIES = 3

INSTAGRAM_TIMEOUT = 46  # /v1/instagram/search/reels
INSTAGRAM_PROFILES_TIMEOUT = 34  # /v1/instagram/search/profiles
INSTAGRAM_PROFILE_TIMEOUT = 28  # /v1/instagram/profile
YOUTUBE_TIMEOUT = 15
REDDIT_TIMEOUT = 22
GOOGLE_BUSINESS_TIMEOUT = 54
GOOGLE_SHOPPING_TIMEOUT = 60
TWITTER_TIMEOUT = 80

MAX_PAGES = 10

# Set DRY_RUN=True to check endpoint pricing without fetching data.
# Dry runs do not fetch or charge credits.
DRY_RUN = os.environ.get("SOCIALCRAWL_DRY_RUN", "false").lower() == "true"

CREDIT_COSTS: Dict[str, str] = {
    "instagram": "1 credit per page",
    "instagram_reels": "1 credit per page",
    "instagram_profiles": "1 credit per page",
    "instagram_profile": "1 credit per call",
    "youtube": "1 credit per page",
    "reddit": "1 credit per page",
    "google_business": "5 credits per call",
    "google_shopping": "1 credit per call (product lookup), 5 credits per call (product search)",
    "twitter": "5 credits per call",
    "x": "5 credits per call",
}

# In-memory cache for search responses: cache_key -> (timestamp, response_data)
# Prevents duplicate requests and unbilled calls within cache TTL (1 hour)
_SOCIALCRAWL_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 3600


def get_socialcrawl_api_key() -> str:
    """
    Read the API key exclusively from environment variables or backend settings.
    Never hardcode or expose. Dynamically resolves from .env and backend/.env as fallback.
    """
    key = os.environ.get("SOCIALCRAWL_API_KEY") or settings.get_socialcrawl_api_key()
    if not key:
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


# Dynamic property alias for backwards compatibility with the supplied file
API_KEY = get_socialcrawl_api_key() or "YOUR_API_KEY"


# ============================================================
# SHARED SEARCH QUERY
# ============================================================

ARCHITECTURE_QUERY = (
    "Architecture, architectural design, modern architecture, "
    "traditional architecture, contemporary architecture, "
    "residential architecture, commercial architecture, "
    "modern houses, traditional houses, villas, luxury villas, "
    "apartments, flats, duplex houses, independent houses, "
    "bungalows, cottages, farmhouses, tiny houses, modular homes, "
    "prefabricated buildings, commercial buildings, offices, "
    "hotels, resorts, restaurants, cafes, shops, retail spaces, "
    "institutional buildings, schools, colleges, hospitals, "
    "architectural concepts, architectural drawings, floor plans, "
    "house plans, 2D plans, 3D plans, elevation designs, "
    "section drawings, structural drawings, construction drawings, "
    "building layouts, space planning, vastu house plans, "
    "interior design, exterior design, home interiors, "
    "home exteriors, living room design, bedroom design, "
    "master bedroom, children's bedroom, guest bedroom, "
    "kitchen design, modular kitchens, open kitchens, "
    "bathroom design, luxury bathrooms, powder rooms, "
    "dining room design, pooja rooms, prayer rooms, "
    "home offices, study rooms, entertainment rooms, "
    "walk-in wardrobes, dressing rooms, utility rooms, "
    "balcony design, terrace design, rooftop design, "
    "basement design, staircase design, entrance design, "
    "foyer design, corridors, indoor spaces, outdoor spaces, "
    "furniture, sofas, couches, recliners, lounge chairs, "
    "dining tables, coffee tables, side tables, console tables, "
    "chairs, stools, benches, beds, bunk beds, headboards, "
    "wardrobes, cabinets, cupboards, drawers, shelves, "
    "bookcases, storage units, TV units, display units, "
    "kitchen cabinets, kitchen islands, countertops, "
    "office furniture, outdoor furniture, custom furniture, "
    "doors, main doors, wooden doors, glass doors, sliding doors, "
    "folding doors, flush doors, UPVC doors, aluminium doors, "
    "windows, bay windows, sliding windows, casement windows, "
    "French windows, skylights, ventilators, louvers, "
    "facades, building elevations, exterior walls, cladding, "
    "wall treatments, wall panels, wooden panels, stone cladding, "
    "roofing, roof tiles, metal roofing, flat roofs, sloped roofs, "
    "false ceilings, gypsum ceilings, POP ceilings, "
    "flooring, floor tiles, wall tiles, ceramic tiles, "
    "vitrified tiles, porcelain tiles, marble flooring, "
    "granite flooring, natural stone flooring, wooden flooring, "
    "laminate flooring, vinyl flooring, epoxy flooring, "
    "microcement, polished concrete, terrazzo, mosaics, "
    "marble, granite, quartz, sandstone, limestone, slate, "
    "natural stone, engineered stone, wood, timber, plywood, "
    "MDF, HDF, particle board, laminates, veneers, "
    "bricks, clay bricks, fly ash bricks, AAC blocks, "
    "concrete blocks, cement, ready mix concrete, concrete, "
    "reinforcement steel, TMT bars, structural steel, "
    "steel sections, aluminium, glass, toughened glass, "
    "laminated glass, acrylic sheets, polycarbonate sheets, "
    "pipes, plumbing pipes, PVC pipes, CPVC pipes, UPVC pipes, "
    "HDPE pipes, drainage pipes, water supply pipes, "
    "electrical materials, electrical wiring, cables, "
    "switches, sockets, distribution boards, circuit breakers, "
    "smart switches, home automation, electrical fittings, "
    "plumbing materials, sanitaryware, wash basins, sinks, "
    "toilets, water closets, urinals, bathtubs, showers, "
    "shower enclosures, shower panels, faucets, taps, mixers, "
    "bathroom fittings, kitchen faucets, floor drains, "
    "water heaters, geysers, water tanks, pumps, valves, "
    "hardware, door handles, cabinet handles, hinges, "
    "locks, smart locks, latches, tower bolts, drawer channels, "
    "sliding systems, aluminium profiles, glass hardware, "
    "lighting design, interior lighting, exterior lighting, "
    "ambient lighting, task lighting, accent lighting, "
    "LED lights, strip lights, spotlights, downlights, "
    "track lights, chandeliers, pendant lights, wall lights, "
    "table lamps, floor lamps, garden lights, landscape lights, "
    "ceiling fans, exhaust fans, decorative fans, "
    "air conditioning, ventilation, HVAC, "
    "paints, wall paints, exterior paints, interior paints, "
    "primers, waterproofing, wood finishes, metal finishes, "
    "textures, textured walls, wallpapers, wall coverings, "
    "decorative laminates, decorative finishes, "
    "colour combinations, colour palettes, paint combinations, "
    "curtains, blinds, roller blinds, shutters, drapes, "
    "rugs, carpets, doormats, cushions, throws, upholstery, "
    "mirrors, decorative mirrors, artwork, paintings, "
    "sculptures, statues, idols, clocks, wall clocks, "
    "vases, pottery, ceramics, artefacts, antiques, "
    "collectibles, handicrafts, decorative objects, "
    "table decor, wall decor, shelf decor, home accessories, "
    "planters, indoor plants, outdoor plants, gardens, "
    "landscaping, garden design, vertical gardens, "
    "courtyards, patios, decks, pergolas, gazebos, "
    "swimming pools, water features, fountains, "
    "outdoor kitchens, outdoor seating, boundary walls, "
    "compound gates, fences, driveways, pathways, "
    "sustainable architecture, green buildings, "
    "eco friendly materials, recycled materials, "
    "passive design, natural ventilation, daylighting, "
    "solar panels, rainwater harvesting, smart homes, "
    "home automation, energy efficient buildings, "
    "space saving furniture, compact homes, small house design, "
    "storage solutions, DIY home improvement, renovation, "
    "remodelling, construction techniques, building methods, "
    "waterproofing solutions, insulation, acoustic treatment, "
    "fire safety, structural details, construction materials, "
    "building products, product innovations, design trends, "
    "material trends, brands, manufacturers, dealers, "
    "distributors, wholesalers, retailers, suppliers, "
    "showrooms, construction companies, contractors, "
    "architects, interior designers, landscape designers, "
    "product reviews, material comparisons, installation guides, "
    "product demonstrations, architectural inspiration"
)


# ============================================================
# CURATED CATEGORIES TAXONOMY
# ============================================================

ARCHITECTURAL_CATEGORIES: List[Dict[str, Any]] = [
    {
        "id": "arch-modern-houses",
        "name": "Modern Houses",
        "domain": "architecture",
        "queries": {
            "instagram": "modern house design architecture reel",
            "youtube": "modern house architectural design walkthrough",
            "reddit": "modern house design construction architecture",
            "google_business": "architects residential design modern houses",
            "google_shopping": "architectural house plan modern elevation"
        }
    },
    {
        "id": "arch-traditional-kerala",
        "name": "Traditional & Kerala Houses",
        "domain": "architecture",
        "queries": {
            "instagram": "Kerala architecture courtyard nalukettu house",
            "youtube": "traditional Kerala house architecture walkthrough courtyard",
            "reddit": "kerala traditional house architecture renovation",
            "google_business": "traditional kerala house architects construction",
            "google_shopping": "kerala clay roof tiles wooden gables"
        }
    },
    {
        "id": "interior-kitchens",
        "name": "Modular Kitchens",
        "domain": "interior",
        "queries": {
            "instagram": "modular kitchen interior architecture design",
            "youtube": "modular kitchen design materials quartz acrylic",
            "reddit": "modular kitchen materials plywood acrylic hardware quality",
            "google_business": "modular kitchen showrooms manufacturers dealers",
            "google_shopping": "modular kitchen quartz countertop island"
        }
    },
    {
        "id": "interior-bathrooms",
        "name": "Bathrooms & Sanitaryware",
        "domain": "interior",
        "queries": {
            "instagram": "luxury bathroom design walk-in shower architecture",
            "youtube": "bathroom interior design plumbing sanitaryware review",
            "reddit": "bathroom renovation fixtures tiles waterproofing",
            "google_business": "bathroom sanitaryware showrooms dealers",
            "google_shopping": "freestanding bathtub thermostatic shower faucet"
        }
    },
    {
        "id": "mat-bricks-blocks",
        "name": "Bricks & Blocks",
        "domain": "materials",
        "queries": {
            "instagram": "exposed brick architecture wirecut clay bricks",
            "youtube": "exposed brick masonry rat trap bond AAC blocks",
            "reddit": "AAC blocks vs wirecut red clay bricks cost quality",
            "google_business": "wirecut brick manufacturers AAC block suppliers",
            "google_shopping": "wirecut clay bricks AAC lightweight blocks"
        }
    },
    {
        "id": "mat-cement-concrete",
        "name": "Cement & Concrete",
        "domain": "materials",
        "queries": {
            "instagram": "board-formed concrete microcement polished screed",
            "youtube": "concrete construction microcement floor board form",
            "reddit": "microcement flooring durability ready mix concrete",
            "google_business": "cement dealers ready mix concrete suppliers",
            "google_shopping": "microcement wall floor kit Portland cement"
        }
    },
    {
        "id": "mat-steel-tmt",
        "name": "TMT & Reinforcement Steel",
        "domain": "materials",
        "queries": {
            "instagram": "structural steel architecture glass frame",
            "youtube": "TMT bar manufacturing testing construction steel",
            "reddit": "best TMT bar brand Fe 550D Tata Tiscon JSW Jindal",
            "google_business": "TMT steel bar distributors steel stockists",
            "google_shopping": "TMT rebar 12mm 16mm structural steel channel"
        }
    },
    {
        "id": "mat-marble-granite",
        "name": "Marble & Granite",
        "domain": "materials",
        "queries": {
            "instagram": "Italian marble flooring honed granite architecture",
            "youtube": "Italian marble vs Indian granite flooring review",
            "reddit": "Italian marble vs composite quartz granite kitchen countertop",
            "google_business": "marble granite dealers wholesalers stone yards",
            "google_shopping": "Italian Statuario marble slab honed black granite"
        }
    },
    {
        "id": "finish-tiles-flooring",
        "name": "Tiles & Flooring",
        "domain": "finishes",
        "queries": {
            "instagram": "vitrified tiles porcelain slab terrazzo floor",
            "youtube": "vitrified tile selection large format porcelain review",
            "reddit": "vitrified tiles Kajaria Somany vs Italian porcelain review",
            "google_business": "tiles showrooms dealers Kajaria Nitco Simpolo",
            "google_shopping": "large format vitrified floor tiles porcelain slab"
        }
    },
    {
        "id": "finish-paints-coatings",
        "name": "Paints & Finishes",
        "domain": "finishes",
        "queries": {
            "instagram": "limewash textured paint interior wall finish",
            "youtube": "texture wall paint limewash application architecture",
            "reddit": "limewash vs Asian paints royal luxury wall finish",
            "google_business": "paint dealers Asian Paints Berger Dulux wholesalers",
            "google_shopping": "natural mineral limewash paint Asian Paints Apex"
        }
    },
    {
        "id": "elec-lighting-fixtures",
        "name": "Lighting & Electrical",
        "domain": "electrical",
        "queries": {
            "instagram": "architectural lighting track lights warm downlight",
            "youtube": "architectural lighting design cove magnetic track lights",
            "reddit": "magnetic track light installation LED strip brand reviews",
            "google_business": "architectural lighting showrooms electrical dealers",
            "google_shopping": "magnetic track light recessed LED cob spotlight"
        }
    },
    {
        "id": "hard-doors-windows",
        "name": "Doors & Windows",
        "domain": "hardware",
        "queries": {
            "instagram": "pivot main door slim aluminium sliding window",
            "youtube": "slim profile aluminium sliding doors thermal break",
            "reddit": "Schueco vs Fenesta vs local UPVC aluminium window reviews",
            "google_business": "aluminium window fabricators doors manufacturers",
            "google_shopping": "magnetic door lock pivot hinge concealed handle"
        }
    }
]


# ============================================================
# SHARED REQUEST HANDLER
# ============================================================

def backoff(attempt: int) -> float:
    """
    Exponential backoff with jitter:
    approximately 0.5-1 second, 1-2 seconds, 2-4 seconds.
    """
    return 2 ** attempt * (0.5 + random.random() / 2)


def socialcrawl(
    endpoint: str,
    params: dict[str, Any],
    timeout: int
) -> Optional[dict[str, Any]]:
    """
    Shared SocialCrawl request handler.

    - Uses the API key header.
    - Uses one idempotency key per request.
    - Reuses that key for every retry of the same request.
    - Handles retryable and permanent errors.
    - Respects Retry-After.
    - Supports dry_run=1.
    """
    resolved_key = get_socialcrawl_api_key()
    if not resolved_key or resolved_key == "YOUR_API_KEY":
        raise ValueError(
            "SOCIALCRAWL_API_KEY is missing. "
            "Set it in the backend environment."
        )

    # Clean endpoint string
    endpoint_clean = endpoint.lstrip("/")
    if endpoint_clean.startswith("v1/"):
        endpoint_clean = endpoint_clean[3:]
    url = f"{BASE_URL}/{endpoint_clean}"

    request_params = params.copy()

    if DRY_RUN or request_params.get("dry_run") in [True, 1, "1", "true"]:
        request_params["dry_run"] = 1

    # One key per page/request, reused across its retries.
    idempotency_key = str(uuid.uuid4())

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.get(
                url,
                params=request_params,
                headers={
                    "x-api-key": resolved_key,
                    "Idempotency-Key": idempotency_key
                },
                timeout=timeout
            )

            body = response.json()

        except (requests.RequestException, ValueError) as err:
            if attempt == MAX_RETRIES:
                logger.error(f"SocialCrawl request to {url} failed on attempt {attempt}: {err}")
                raise

            time.sleep(backoff(attempt))
            continue

        if body.get("success"):
            return body

        error = body.get("error", {})
        error_type = error.get("type", "UNKNOWN_ERROR")

        if error_type == "RESOURCE_NOT_FOUND" or response.status_code == 404:
            return None

        retry_after = response.headers.get("Retry-After")

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
                f"{error_type}: {error.get('message', 'Unknown SocialCrawl error')} "
                f"(status {response.status_code}, request_id {body.get('request_id')})"
            )

        time.sleep(
            float(retry_after)
            if retry_after
            else backoff(attempt)
        )

    return None


# ============================================================
# PAGINATION HANDLER
# Instagram, YouTube and Reddit support pagination in
# the supplied endpoint examples.
# ============================================================

def paginated_search(
    endpoint: str,
    params: dict[str, Any],
    timeout: int,
    max_pages: int = MAX_PAGES
) -> list[dict[str, Any]]:

    items = []
    current_params = params.copy()

    for _ in range(max_pages):

        body = socialcrawl(
            endpoint=endpoint,
            params=current_params,
            timeout=timeout
        )

        if body is None:
            break

        data = body.get("data") or {}
        items.extend(data.get("items") or [])

        pagination = body.get("pagination") or {}

        if (
            not pagination.get("has_more")
            or not pagination.get("next_cursor")
        ):
            break

        current_params["cursor"] = pagination["next_cursor"]

    return items


# ============================================================
# NORMALIZERS FOR EACH SOURCE
# ============================================================

def normalize_instagram_reel(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a SocialCrawl Instagram Reel item into standard format.
    Enforces honest attribution and actual video/thumbnail URLs.
    Never fabricates posts or images.
    """
    if not isinstance(raw, dict):
        raw = {}
    post = raw.get("post") or raw if isinstance(raw, dict) else {}
    if not isinstance(post, dict):
        post = {}
    content = post.get("content") or {} if isinstance(post, dict) else {}
    author = post.get("author") or {} if isinstance(post, dict) else {}
    engagement = post.get("engagement") or {} if isinstance(post, dict) else {}
    ext = post.get("ext") or {} if isinstance(post, dict) else {}
    computed = raw.get("computed") or {} if isinstance(raw, dict) else {}

    reel_id = str(post.get("id") or "")
    url = post.get("url") or (f"https://www.instagram.com/reel/{reel_id}/" if reel_id else "https://www.instagram.com")

    media_urls = content.get("media_urls")
    media_url = None
    if isinstance(media_urls, list) and media_urls:
        media_url = media_urls[0]
    elif isinstance(media_urls, str):
        media_url = media_urls

    video_url = content.get("video_url") or media_url
    thumbnail_url = content.get("thumbnail_url") or content.get("display_url") or media_url

    caption = content.get("text") or ""
    title = caption.strip().split("\n")[0][:120] if caption.strip() else "Instagram Architectural Reel"
    duration = content.get("duration_seconds")
    formatted_duration = f"0:{int(duration):02d}" if duration else "0:15"

    rel_obj = computed.get("relevance") if isinstance(computed, dict) else None
    relevance_score = rel_obj.get("p") if isinstance(rel_obj, dict) else None

    return {
        "id": f"instagram-{reel_id or abs(hash(url))}",
        "reel_id": reel_id,
        "title": title,
        "description": caption,
        "image_url": thumbnail_url,
        "thumbnail_url": thumbnail_url,
        "video_url": video_url,
        "media_url": media_url or video_url,
        "source_url": url,
        "creator_name": f"@{author.get('username')}" if author.get("username") else (author.get("display_name") or "Instagram Creator"),
        "creator_username": author.get("username"),
        "creator_url": f"https://www.instagram.com/{author.get('username')}/" if author.get("username") else None,
        "creator_avatar": author.get("avatar_url"),
        "is_video": True,
        "is_reel": True,
        "video_duration": formatted_duration,
        "views": engagement.get("views"),
        "likes": engagement.get("likes"),
        "comments": engagement.get("comments"),
        "shares": engagement.get("shares"),
        "material_tags": ext.get("hashtags") or [],
        "source_platform": "instagram",
        "source_label": "Instagram",
        "attribution_notice": "Instagram Architectural Inspiration via SocialCrawl.",
        "verification_status": "UNVERIFIED",
        "content_type": "architectural_reel",
        "relevance_score": relevance_score,
        "published_at": post.get("published_at"),
    }


# ============================================================
# INSTAGRAM PROFESSIONAL CLASSIFICATION & PROFILE NORMALIZATION
# ============================================================

def classify_instagram_account(
    bio: str = "",
    full_name: str = "",
    category_name: str = ""
) -> str:
    """
    Classify an Instagram account into an architectural/industry role
    based strictly on available account bio, display name, and category.
    Returns 'Unclassified' if uncertain, never invents a profession.
    """
    text = f"{bio or ''} {full_name or ''} {category_name or ''}".lower()

    if any(k in text for k in ["landscape architect", "landscape design", "garden design", "landscaping", "garden architects"]):
        return "Landscape Architect"
    if any(k in text for k in ["architecture studio", "architects studio", "architectural firm", "architecture firm", "architectural practice"]):
        return "Architecture Studio"
    if any(k in text for k in ["interior design studio", "interior studio", "interiors studio"]):
        return "Interior Design Studio"
    if any(k in text for k in ["interior designer", "interior design", "interior decorator", "home stylist"]):
        return "Interior Designer"
    if any(k in text for k in ["manufacturer", "manufacturing", "factory", "producer", "fabricator", "quarry"]):
        return "Manufacturer"
    if any(k in text for k in ["showroom", "experience center", "display centre", "display center"]):
        return "Showroom"
    if any(k in text for k in ["distributor", "wholesale distributor", "importer", "exporter"]):
        return "Product Distributor"
    if any(k in text for k in ["supplier", "dealer", "stockist", "building materials dealer", "material supplier"]):
        return "Supplier"
    if any(k in text for k in ["structural engineer", "structural consultancy", "structural consultant"]):
        return "Structural Engineer"
    if any(k in text for k in ["civil engineer", "civil engineering"]):
        return "Civil Engineer"
    if any(k in text for k in ["builder", "home builder", "villa builder", "developers", "real estate developer"]):
        return "Builder"
    if any(k in text for k in ["general contractor", "building contractor", "civil contractor", "turnkey contractor", "contractor"]):
        return "Contractor"
    if any(k in text for k in ["brand", "official account", "flagship"]):
        return "Brand"
    if re.search(r"\b(architect|architects|architectural designer)\b", text):
        return "Architect"

    return "Unclassified"


def normalize_instagram_profile(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a SocialCrawl Instagram Profile Search or Profile Lookup item.
    Only stores fields actually returned by the API.
    Never fabricates missing details.
    """
    if not isinstance(raw, dict):
        raw = {}

    profile = raw.get("user") or raw.get("profile") or raw.get("author") or raw
    if not isinstance(profile, dict):
        profile = {}

    username = profile.get("username") or profile.get("handle") or ""
    username = str(username).lstrip("@").strip()
    full_name = profile.get("full_name") or profile.get("display_name") or profile.get("name") or username
    bio = profile.get("biography") or profile.get("bio") or profile.get("description") or ""
    avatar = profile.get("profile_pic_url") or profile.get("avatar_url") or profile.get("profile_pic_url_hd")
    website = profile.get("external_url") or profile.get("website") or profile.get("link")
    category = profile.get("category_name") or profile.get("category") or profile.get("business_category_name") or ""
    
    classification = classify_instagram_account(bio=bio, full_name=full_name, category_name=category)
    url = f"https://www.instagram.com/{username}/" if username else None

    return {
        "id": f"instagram-profile-{username or abs(hash(str(raw)))}",
        "username": username,
        "full_name": full_name,
        "biography": bio,
        "profile_pic_url": avatar,
        "external_url": website,
        "profile_url": url,
        "category": category or None,
        "classification": classification,
        "is_verified": bool(profile.get("is_verified")),
        "follower_count": profile.get("follower_count") or profile.get("followers"),
        "following_count": profile.get("following_count") or profile.get("following"),
        "media_count": profile.get("media_count") or profile.get("posts_count"),
        "is_business": bool(profile.get("is_business") or profile.get("is_professional")),
        "source_platform": "instagram",
        "source_label": "Instagram",
    }


def normalize_youtube_video(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes a SocialCrawl YouTube Search item."""
    if not isinstance(raw, dict):
        raw = {}
    post = raw.get("post") or raw if isinstance(raw, dict) else {}
    if not isinstance(post, dict):
        post = {}
    content = post.get("content") or {} if isinstance(post, dict) else {}
    author = post.get("author") or {} if isinstance(post, dict) else {}
    engagement = post.get("engagement") or {} if isinstance(post, dict) else {}
    ext = post.get("ext") or {} if isinstance(post, dict) else {}
    computed = raw.get("computed") or {} if isinstance(raw, dict) else {}

    video_id = str(post.get("id") or "")
    url = post.get("url") or (f"https://www.youtube.com/watch?v={video_id}" if video_id else "https://www.youtube.com")
    title = content.get("text") or ext.get("title") or "YouTube Architectural Video"
    thumbnail_url = content.get("thumbnail_url") or (f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else None)

    duration_sec = content.get("duration_seconds")
    if duration_sec:
        m, s = divmod(int(duration_sec), 60)
        h, m = divmod(m, 60)
        formatted_duration = f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"
    else:
        formatted_duration = None

    rel_obj = computed.get("relevance") if isinstance(computed, dict) else None
    relevance_score = rel_obj.get("p") if isinstance(rel_obj, dict) else None

    return {
        "id": f"youtube-{video_id or abs(hash(url))}",
        "video_id": video_id,
        "video_embed_id": video_id,
        "title": title,
        "description": ext.get("description") or title,
        "image_url": thumbnail_url,
        "thumbnail_url": thumbnail_url,
        "media_url": thumbnail_url,
        "source_url": url,
        "creator_name": author.get("display_name") or author.get("username") or "YouTube Creator",
        "creator_url": f"https://www.youtube.com/{author.get('username')}" if author.get("username") else None,
        "creator_avatar": author.get("avatar_url"),
        "is_video": True,
        "is_short": bool(duration_sec and duration_sec < 60),
        "video_duration": formatted_duration,
        "views": engagement.get("views"),
        "likes": engagement.get("likes"),
        "comments": engagement.get("comments"),
        "source_platform": "youtube",
        "source_label": "YouTube",
        "attribution_notice": "YouTube architectural video reference via SocialCrawl.",
        "verification_status": "UNVERIFIED",
        "content_type": "youtube_walkthrough",
        "relevance_score": relevance_score,
        "published_at": post.get("published_at"),
    }


def normalize_reddit_post(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes a SocialCrawl Reddit Search item."""
    if not isinstance(raw, dict):
        raw = {}
    post = raw.get("post") or raw if isinstance(raw, dict) else {}
    if not isinstance(post, dict):
        post = {}
    content = post.get("content") or {} if isinstance(post, dict) else {}
    author = post.get("author") or {} if isinstance(post, dict) else {}
    engagement = post.get("engagement") or {} if isinstance(post, dict) else {}
    ext = post.get("ext") or {} if isinstance(post, dict) else {}
    computed = raw.get("computed") or {} if isinstance(raw, dict) else {}

    post_id = str(post.get("id") or "")
    url = post.get("url") or (f"https://www.reddit.com/comments/{post_id}" if post_id else "https://www.reddit.com")
    title = ext.get("title") or content.get("text") or "Reddit Architectural Discussion"
    selftext = ext.get("selftext") or content.get("text") or ""
    subreddit = ext.get("subreddit") or "architecture"

    # Extract Video
    video_url: Optional[str] = None
    if content.get("video_url") and isinstance(content.get("video_url"), str):
        video_url = content.get("video_url")
    elif ext.get("media") and isinstance(ext.get("media"), dict):
        reddit_vid = ext.get("media", {}).get("reddit_video") or {}
        if isinstance(reddit_vid, dict) and reddit_vid.get("fallback_url"):
            video_url = str(reddit_vid.get("fallback_url"))
    elif ext.get("secure_media") and isinstance(ext.get("secure_media"), dict):
        reddit_vid = ext.get("secure_media", {}).get("reddit_video") or {}
        if isinstance(reddit_vid, dict) and reddit_vid.get("fallback_url"):
            video_url = str(reddit_vid.get("fallback_url"))
    elif ext.get("preview") and isinstance(ext.get("preview"), dict):
        rvp = ext.get("preview", {}).get("reddit_video_preview") or {}
        if isinstance(rvp, dict) and rvp.get("fallback_url"):
            video_url = str(rvp.get("fallback_url"))

    # Extract Gallery Images
    gallery_images: List[str] = []
    gallery_data = ext.get("gallery_data")
    media_metadata = ext.get("media_metadata")
    if isinstance(gallery_data, dict) and isinstance(media_metadata, dict):
        g_items = gallery_data.get("items") or []
        for g_item in g_items:
            if isinstance(g_item, dict):
                m_id = g_item.get("media_id")
                if m_id and m_id in media_metadata:
                    m_info = media_metadata[m_id]
                    s_obj = m_info.get("s") if isinstance(m_info, dict) else None
                    if isinstance(s_obj, dict) and s_obj.get("u"):
                        gallery_images.append(str(s_obj["u"]).replace("&amp;", "&"))

    # Extract Image URL
    image_url: Optional[str] = None
    raw_media_urls = content.get("media_urls")
    if isinstance(raw_media_urls, list) and raw_media_urls and isinstance(raw_media_urls[0], str):
        image_url = raw_media_urls[0]
    elif isinstance(raw_media_urls, str) and raw_media_urls:
        image_url = raw_media_urls

    if not image_url and gallery_images:
        image_url = gallery_images[0]

    raw_post_url = str(post.get("url") or "")
    if not image_url and (
        any(raw_post_url.lower().endswith(ext_img) for ext_img in [".jpg", ".jpeg", ".png", ".webp", ".gif"])
        or "i.redd.it" in raw_post_url
        or "i.imgur.com" in raw_post_url
    ):
        image_url = raw_post_url

    ext_preview = ext.get("preview") or {}
    if not image_url and isinstance(ext_preview, dict):
        images = ext_preview.get("images") or []
        if images and isinstance(images, list) and isinstance(images[0], dict):
            src = images[0].get("source", {}).get("url")
            if src:
                image_url = str(src).replace("&amp;", "&")
            elif images[0].get("resolutions") and isinstance(images[0].get("resolutions"), list):
                res_list = images[0].get("resolutions")
                if res_list and isinstance(res_list[-1], dict) and res_list[-1].get("url"):
                    image_url = str(res_list[-1]["url"]).replace("&amp;", "&")

    # Extract Thumbnail
    raw_thumb = content.get("thumbnail_url") or ext.get("thumbnail")
    thumbnail_url: Optional[str] = None
    if (
        isinstance(raw_thumb, str)
        and raw_thumb.startswith("http")
        and raw_thumb.lower() not in ["self", "default", "nsfw", "spoiler", "image"]
    ):
        thumbnail_url = raw_thumb
    else:
        thumbnail_url = image_url

    media_url: Optional[str] = video_url or image_url or thumbnail_url
    is_self = bool(ext.get("is_self", not media_url))
    domain = ext.get("domain") or post.get("domain") or "reddit.com"

    rel_obj = computed.get("relevance") if isinstance(computed, dict) else None
    relevance_score = rel_obj.get("p") if isinstance(rel_obj, dict) else None

    sub_name = str(subreddit).strip().lstrip("r/").lstrip("/")
    sub_label = f"r/{sub_name}" if sub_name else "r/architecture"

    return {
        "id": f"reddit-{post_id or abs(hash(url))}",
        "post_id": post_id,
        "title": title,
        "description": selftext[:500] if selftext else title,
        "image_url": image_url,
        "thumbnail_url": thumbnail_url,
        "video_url": video_url,
        "media_url": media_url,
        "source_url": url,
        "creator_name": f"u/{author.get('username')}" if author.get("username") else "Reddit User",
        "creator_url": f"https://www.reddit.com/user/{author.get('username')}/" if author.get("username") else None,
        "subreddit": sub_label,
        "subreddit_name": sub_name,
        "upvotes": engagement.get("likes") or 0,
        "comments": engagement.get("comments") or 0,
        "flair": ext.get("flair"),
        "source_platform": "reddit",
        "source_label": f"Reddit {sub_label}",
        "attribution_notice": f"Reddit community discussion from {sub_label} via SocialCrawl.",
        "verification_status": "COMMUNITY_REVIEW",
        "content_type": "architectural_discussion",
        "relevance_score": relevance_score,
        "published_at": post.get("published_at"),
        "is_self": is_self,
        "domain": domain,
        "gallery_images": gallery_images,
    }


def normalize_twitter_post(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a SocialCrawl Twitter (X) AI-Search item into standard format.
    Enforces honest attribution, actual media/links.
    """
    if not isinstance(raw, dict):
        raw = {}
    post = raw.get("post") or raw if isinstance(raw, dict) else {}
    if not isinstance(post, dict):
        post = {}
    content = post.get("content") or {} if isinstance(post, dict) else {}
    author = post.get("author") or {} if isinstance(post, dict) else {}
    engagement = post.get("engagement") or {} if isinstance(post, dict) else {}
    ext = post.get("ext") or {} if isinstance(post, dict) else {}
    computed = raw.get("computed") or {} if isinstance(raw, dict) else {}

    tweet_id = str(post.get("id") or "")
    author_username = author.get("username") or author.get("screen_name") or ""
    url = post.get("url") or (
        f"https://x.com/{author_username}/status/{tweet_id}"
        if tweet_id and author_username
        else (f"https://x.com/i/status/{tweet_id}" if tweet_id else "https://x.com")
    )

    media_urls = content.get("media_urls") or []
    if isinstance(media_urls, str):
        media_urls = [media_urls]
    elif not isinstance(media_urls, list):
        media_urls = []

    photos = ext.get("photos") or []
    if isinstance(photos, list):
        for p in photos:
            if isinstance(p, str) and p not in media_urls:
                media_urls.append(p)
            elif isinstance(p, dict) and p.get("url") and p.get("url") not in media_urls:
                media_urls.append(p.get("url"))

    media_url = media_urls[0] if media_urls else None
    thumbnail_url = content.get("thumbnail_url") or media_url

    text = content.get("text") or post.get("text") or ""
    title = text.strip().split("\n")[0][:120] if text.strip() else "X Architectural Design"

    rel_obj = computed.get("relevance") if isinstance(computed, dict) else None
    relevance_score = rel_obj.get("p") if isinstance(rel_obj, dict) else None

    return {
        "id": f"x-{tweet_id or abs(hash(url))}",
        "tweet_id": tweet_id,
        "title": title,
        "description": text,
        "image_url": thumbnail_url,
        "thumbnail_url": thumbnail_url,
        "media_url": media_url,
        "source_url": url,
        "creator_name": f"@{author_username}" if author_username else (author.get("display_name") or "X Creator"),
        "creator_username": author_username,
        "creator_url": f"https://x.com/{author_username}" if author_username else None,
        "creator_avatar": author.get("avatar_url") or author.get("profile_image_url"),
        "is_video": False,
        "likes": engagement.get("likes") or engagement.get("favorites"),
        "retweets": engagement.get("retweets") or engagement.get("reposts"),
        "replies": engagement.get("replies") or engagement.get("comments"),
        "views": engagement.get("views"),
        "source_platform": "x",
        "source_label": "X (Twitter)",
        "attribution_notice": "X architectural reference via SocialCrawl.",
        "verification_status": "COMMUNITY_REVIEW",
        "content_type": "architectural_project",
        "relevance_score": relevance_score,
        "published_at": post.get("published_at"),
    }


def normalize_google_business(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes a SocialCrawl Google Business Search item."""
    place = raw.get("place", raw)
    ext = place.get("ext", {})
    rating_data = place.get("rating", {})
    if isinstance(rating_data, dict):
        rating_val = rating_data.get("value")
    elif isinstance(rating_data, (int, float)):
        rating_val = float(rating_data)
    else:
        rating_val = None

    image_urls = place.get("image_urls")
    if isinstance(image_urls, list) and image_urls:
        main_image = image_urls[0]
    elif isinstance(image_urls, str):
        main_image = image_urls
    else:
        main_image = None

    categories = place.get("categories") or ([place.get("category")] if place.get("category") else [])
    source_verified = bool(place.get("verified"))

    return {
        "id": f"business-{place.get('id') or ext.get('place_id') or abs(hash(place.get('name', '')))}",
        "place_id": ext.get("place_id") or str(place.get("id") or ""),
        "name": place.get("name") or "Architectural Supplier / Manufacturer",
        "category": place.get("category") or "Building Materials Supplier",
        "categories": categories,
        "rating": rating_val,
        "reviews_count": place.get("reviews_count") or 0,
        "address": place.get("address") or "",
        "city": ext.get("city") or "",
        "region": ext.get("region") or "",
        "country_code": ext.get("country_code") or "IN",
        "phone": place.get("phone"),
        "latitude": place.get("latitude"),
        "longitude": place.get("longitude"),
        "website": place.get("url") or None,
        "maps_url": ext.get("maps_url") or (f"https://www.google.com/maps/search/?api=1&query={requests.utils.quote(place.get('name', ''))}" if place.get("name") else None),
        "image_url": main_image,
        "thumbnail_url": main_image,
        "opening_hours": ext.get("hours") or [],
        "is_open": ext.get("status") == "open",
        "verified": source_verified,
        "verification_status": "SUPPLIER_CONFIRMED" if source_verified else "POTENTIAL_GOOGLE_PLACE",
        "source_platform": "google_business",
        "source_label": "Google Business Directory",
        "attribution_notice": "Google Business profile discovery via SocialCrawl.",
    }


def normalize_google_shopping(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes a SocialCrawl Google Shopping item."""
    prod = raw.get("product", raw)
    price_info = prod.get("price", {})
    rating_info = prod.get("rating", {})
    ext = prod.get("ext", {})

    current_price = price_info.get("current") if isinstance(price_info, dict) else None
    currency = (price_info.get("currency") if isinstance(price_info, dict) else None) if current_price is not None else None
    original_price = price_info.get("original") if isinstance(price_info, dict) else None

    images = prod.get("image_urls") or []
    main_image = images[0] if isinstance(images, list) and images else (images if isinstance(images, str) else None)
    raw_seller = (
        prod.get("seller")
        or raw.get("seller")
        or prod.get("merchant_name")
        or raw.get("merchant_name")
    )
    seller_val = raw_seller.strip() if isinstance(raw_seller, str) and raw_seller.strip() else None

    return {
        "id": f"shopping-{prod.get('id') or ext.get('gid') or abs(hash(prod.get('title', '')))}",
        "product_id": str(prod.get("id") or ""),
        "gid": ext.get("gid"),
        "data_docid": ext.get("data_docid"),
        "title": prod.get("title") or "Architectural Product",
        "description": prod.get("description"),
        "seller": seller_val,
        "brand": prod.get("brand"),
        "price": current_price,
        "original_price": original_price,
        "currency": currency,
        "rating": rating_info.get("average") if isinstance(rating_info, dict) else None,
        "reviews_count": rating_info.get("count") if isinstance(rating_info, dict) else None,
        "image_url": main_image,
        "thumbnail_url": main_image,
        "product_url": prod.get("url"),
        "availability": prod.get("availability"),
        "source_platform": "google_shopping",
        "source_label": "Google Shopping",
        "attribution_notice": "Google Shopping product pricing via SocialCrawl.",
        "verification_status": "UNVERIFIED",
    }


# ============================================================
# 1. INSTAGRAM REELS SEARCH
# GET /v1/instagram/search/reels
#
# Metering: 1 credit per page.
# Unused credits refunded.
# Cache hits free.
# Failed calls refunded.
# ============================================================

def search_instagram_reels(
    query: str = "Modern house architecture",
    date_posted: Optional[str] = None,
    max_pages: int = MAX_PAGES,
    cursor: Optional[str] = None,
    relevance: str = "score",
    dry_run: bool = False
) -> Any:
    """
    Search Instagram Reels via SocialCrawl API.
    Supports pagination, cursor, dry-run price checking, and caching.
    Uses small targeted queries to avoid empty results or API timeouts.
    """
    clean_query = (query or "").strip()
    if clean_query == ARCHITECTURE_QUERY or len(clean_query) > 100:
        # Use clean targeted architectural query instead of enormous paragraph
        clean_query = clean_query.split(",")[0].strip() if "," in clean_query else "Modern house architecture"
        if len(clean_query) > 80:
            clean_query = "Modern house architecture"

    if not clean_query:
        clean_query = "Modern house architecture"

    cache_key = f"instagram:{clean_query}:{cursor}:{date_posted}:{relevance}:{max_pages}:{dry_run}"

    if not dry_run and cache_key in _SOCIALCRAWL_CACHE:
        ts, data = _SOCIALCRAWL_CACHE[cache_key]
        if time.time() - ts < CACHE_TTL_SECONDS:
            cached = dict(data)
            cached["cached"] = True
            cached["credits_used"] = 0
            return cached

    params: Dict[str, Any] = {
        "query": clean_query,
        "relevance": relevance,
    }
    if date_posted and date_posted != "all":
        params["date_posted"] = date_posted
    if cursor:
        params["cursor"] = cursor
    if dry_run or DRY_RUN:
        params["dry_run"] = 1

    if dry_run or DRY_RUN:
        body = socialcrawl(
            endpoint="instagram/search/reels",
            params=params,
            timeout=INSTAGRAM_TIMEOUT
        )
        return {
            "success": True,
            "dry_run": True,
            "query": clean_query,
            "platform": "instagram",
            "estimate": body.get("data", {}).get("estimate", {}) if body else {},
            "credits_used": 0,
            "request_id": body.get("request_id") if body else None,
        }

    raw_items = paginated_search(
        endpoint="instagram/search/reels",
        params=params,
        timeout=INSTAGRAM_TIMEOUT,
        max_pages=max_pages
    )

    # If 0 results returned and date_posted was restricting it, fallback without date_posted
    if not raw_items and params.get("date_posted"):
        fallback_params = params.copy()
        fallback_params.pop("date_posted", None)
        raw_items = paginated_search(
            endpoint="instagram/search/reels",
            params=fallback_params,
            timeout=INSTAGRAM_TIMEOUT,
            max_pages=max_pages
        )

    normalized_items = [normalize_instagram_reel(item) for item in raw_items]

    result = {
        "success": True,
        "dry_run": False,
        "query": clean_query,
        "platform": "instagram",
        "total_items": len(normalized_items),
        "items": normalized_items,
        "has_more": len(normalized_items) >= 20,
    }

    if not dry_run and not DRY_RUN:
        _SOCIALCRAWL_CACHE[cache_key] = (time.time(), result)

    return result


# ============================================================
# 1B. INSTAGRAM PROFILES SEARCH
# GET /v1/instagram/search/profiles
#
# Metering: 1 credit per page.
# Unused credits refunded.
# Cache hits free.
# Failed calls refunded.
# ============================================================

def search_instagram_profiles(
    query: str = "Architect",
    max_pages: int = 1,
    cursor: Optional[str] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Search Instagram Profiles via SocialCrawl API (GET /v1/instagram/search/profiles).
    Discovers architects, interior designers, builders, suppliers, manufacturers and brands.
    Cost: 1 credit per page.
    Timeout: 34 seconds (p99 latency x 1.5).
    """
    clean_query = (query or "").strip()
    if clean_query == ARCHITECTURE_QUERY or len(clean_query) > 100:
        clean_query = clean_query.split(",")[0].strip() if "," in clean_query else "Architect"
        if len(clean_query) > 80:
            clean_query = "Architect"

    if not clean_query:
        clean_query = "Architect"

    cache_key = f"instagram:profiles:{clean_query}:{cursor}:{max_pages}:{dry_run}"

    if not dry_run and cache_key in _SOCIALCRAWL_CACHE:
        ts, data = _SOCIALCRAWL_CACHE[cache_key]
        if time.time() - ts < CACHE_TTL_SECONDS:
            cached = dict(data)
            cached["cached"] = True
            cached["credits_used"] = 0
            return cached

    params: Dict[str, Any] = {
        "query": clean_query,
    }
    if cursor:
        params["cursor"] = cursor
    if dry_run or DRY_RUN:
        params["dry_run"] = 1

    if dry_run or DRY_RUN:
        body = socialcrawl(
            endpoint="instagram/search/profiles",
            params=params,
            timeout=INSTAGRAM_PROFILES_TIMEOUT
        )
        return {
            "success": True,
            "dry_run": True,
            "query": clean_query,
            "platform": "instagram",
            "estimate": body.get("data", {}).get("estimate", {}) if body else {},
            "credits_used": 0,
            "request_id": body.get("request_id") if body else None,
        }

    raw_items = paginated_search(
        endpoint="instagram/search/profiles",
        params=params,
        timeout=INSTAGRAM_PROFILES_TIMEOUT,
        max_pages=max_pages
    )

    normalized_items = [normalize_instagram_profile(item) for item in raw_items]

    # Deduplicate by username across results
    seen_usernames = set()
    deduped_items = []
    for item in normalized_items:
        u = item.get("username")
        if u and u.lower() in seen_usernames:
            continue
        if u:
            seen_usernames.add(u.lower())
        deduped_items.append(item)

    result = {
        "success": True,
        "dry_run": False,
        "query": clean_query,
        "platform": "instagram",
        "total_items": len(deduped_items),
        "items": deduped_items,
        "has_more": len(deduped_items) >= 15,
        "credits_used": 1 if not dry_run else 0,
        "cached": False,
    }

    if not dry_run and not DRY_RUN:
        _SOCIALCRAWL_CACHE[cache_key] = (time.time(), result)

    return result


# ============================================================
# 1C. INSTAGRAM PROFILE LOOKUP
# GET /v1/instagram/profile
#
# Metering: 1 credit per call.
# Cache hits free.
# Failed calls refunded.
# ============================================================

def get_instagram_profile(
    handle: str,
    dry_run: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Retrieve specific Instagram profile via SocialCrawl API (GET /v1/instagram/profile).
    Selective lookup for selected accounts discovered via search.
    Cost: 1 credit per call.
    Timeout: 28 seconds (p99 latency x 1.5).
    """
    clean_handle = (handle or "").strip().lstrip("@")
    if not clean_handle:
        raise ValueError("Instagram handle cannot be empty.")

    cache_key = f"instagram:profile:{clean_handle.lower()}:{dry_run}"

    if not dry_run and cache_key in _SOCIALCRAWL_CACHE:
        ts, data = _SOCIALCRAWL_CACHE[cache_key]
        if time.time() - ts < CACHE_TTL_SECONDS:
            cached = dict(data)
            cached["cached"] = True
            cached["credits_used"] = 0
            return cached

    params: Dict[str, Any] = {
        "handle": clean_handle,
    }
    if dry_run or DRY_RUN:
        params["dry_run"] = 1

    body = socialcrawl(
        endpoint="instagram/profile",
        params=params,
        timeout=INSTAGRAM_PROFILE_TIMEOUT
    )

    if body is None:
        return None

    if dry_run or DRY_RUN:
        return {
            "success": True,
            "dry_run": True,
            "handle": clean_handle,
            "platform": "instagram",
            "estimate": body.get("data", {}).get("estimate", {}) if body else {},
            "credits_used": 0,
            "request_id": body.get("request_id") if body else None,
        }

    raw_data = body.get("data") or {}
    normalized = normalize_instagram_profile(raw_data)

    result = {
        "success": True,
        "dry_run": False,
        "handle": clean_handle,
        "platform": "instagram",
        "data": normalized,
        "credits_used": 1 if not dry_run else 0,
        "cached": False,
        "request_id": body.get("request_id") if body else None,
    }

    if not dry_run and not DRY_RUN:
        _SOCIALCRAWL_CACHE[cache_key] = (time.time(), result)

    return result


def generate_focused_instagram_queries(term: str, target: str = "all") -> List[str]:
    """
    Generates focused, high-intent 2-4 word search queries for Instagram discovery.
    Never combines the entire taxonomy catalogue into one massive query.
    Target: 'reels' (inspiration), 'profiles' (professionals/vendors), or 'all'.
    """
    clean = (term or "").strip()
    if not clean:
        return ["Modern house architecture", "Architects"]

    # If the user passed a category name or product, generate focused variations
    reel_queries = [
        f"{clean} design",
        f"Modern {clean}",
        f"{clean} walkthrough",
        f"{clean} installation",
    ]

    profile_queries = [
        f"{clean} architect",
        f"{clean} interior design",
        f"{clean} manufacturer",
        f"{clean} supplier",
        f"{clean} showroom",
    ]

    if target == "reels":
        return reel_queries[:3]
    elif target == "profiles":
        return profile_queries[:3]
    return (reel_queries[:2] + profile_queries[:2])


# ============================================================
# 2. YOUTUBE SEARCH
# GET /v1/youtube/search
#
# Metering: 1 credit per page.
# ============================================================

def search_youtube(
    query: str = ARCHITECTURE_QUERY,
    max_pages: int = MAX_PAGES,
    cursor: Optional[str] = None,
    relevance: str = "score",
    dry_run: bool = False
) -> Any:
    """
    Search YouTube videos via SocialCrawl API.
    Supports pagination, cursor, dry-run price checking, and caching.
    """
    clean_query = query.strip()
    cache_key = f"youtube:{clean_query}:{cursor}:{relevance}:{max_pages}:{dry_run}"

    if not dry_run and cache_key in _SOCIALCRAWL_CACHE:
        ts, data = _SOCIALCRAWL_CACHE[cache_key]
        if time.time() - ts < CACHE_TTL_SECONDS:
            cached = dict(data)
            cached["cached"] = True
            cached["credits_used"] = 0
            return cached

    params: Dict[str, Any] = {
        "query": clean_query,
        "relevance": relevance
    }
    if cursor:
        params["cursor"] = cursor
    if dry_run or DRY_RUN:
        params["dry_run"] = 1

    if dry_run or DRY_RUN:
        body = socialcrawl(
            endpoint="youtube/search",
            params=params,
            timeout=YOUTUBE_TIMEOUT
        )
        return {
            "success": True,
            "dry_run": True,
            "query": clean_query,
            "platform": "youtube",
            "estimate": body.get("data", {}).get("estimate", {}) if body else {},
            "credits_used": 0,
            "request_id": body.get("request_id") if body else None,
        }

    raw_items = paginated_search(
        endpoint="youtube/search",
        params=params,
        timeout=YOUTUBE_TIMEOUT,
        max_pages=max_pages
    )

    normalized_items = [normalize_youtube_video(item) for item in raw_items]

    result = {
        "success": True,
        "dry_run": False,
        "query": clean_query,
        "platform": "youtube",
        "total_items": len(normalized_items),
        "items": normalized_items,
        "has_more": len(normalized_items) >= 20,
    }

    if not dry_run and not DRY_RUN:
        _SOCIALCRAWL_CACHE[cache_key] = (time.time(), result)

    return result






# ============================================================
# 3. REDDIT SEARCH
# GET /v1/reddit/search
#
# Metering: 1 credit per page.
# ============================================================

def search_reddit(
    query: str = ARCHITECTURE_QUERY,
    max_pages: int = MAX_PAGES,
    cursor: Optional[str] = None,
    relevance: str = "score",
    dry_run: bool = False
) -> Any:
    """
    Search Reddit discussions via SocialCrawl API.
    Supports pagination, cursor, dry-run price checking, and caching.
    """
    clean_query = query.strip()
    cache_key = f"reddit:{clean_query}:{cursor}:{relevance}:{max_pages}:{dry_run}"

    if not dry_run and cache_key in _SOCIALCRAWL_CACHE:
        ts, data = _SOCIALCRAWL_CACHE[cache_key]
        if time.time() - ts < CACHE_TTL_SECONDS:
            cached = dict(data)
            cached["cached"] = True
            cached["credits_used"] = 0
            return cached

    params: Dict[str, Any] = {
        "query": clean_query,
        "relevance": relevance
    }
    if cursor:
        params["cursor"] = cursor
    if dry_run or DRY_RUN:
        params["dry_run"] = 1

    if dry_run or DRY_RUN:
        body = socialcrawl(
            endpoint="reddit/search",
            params=params,
            timeout=REDDIT_TIMEOUT
        )
        return {
            "success": True,
            "dry_run": True,
            "query": clean_query,
            "platform": "reddit",
            "estimate": body.get("data", {}).get("estimate", {}) if body else {},
            "credits_used": 0,
            "request_id": body.get("request_id") if body else None,
        }

    raw_items = paginated_search(
        endpoint="reddit/search",
        params=params,
        timeout=REDDIT_TIMEOUT,
        max_pages=max_pages
    )

    normalized_items = [normalize_reddit_post(item) for item in raw_items]

    result = {
        "success": True,
        "dry_run": False,
        "query": clean_query,
        "platform": "reddit",
        "total_items": len(normalized_items),
        "items": normalized_items,
        "has_more": len(normalized_items) >= 20,
    }

    if not dry_run and not DRY_RUN:
        _SOCIALCRAWL_CACHE[cache_key] = (time.time(), result)

    return result






# ============================================================
# 4. GOOGLE BUSINESS SEARCH
# GET /v1/google/business/search
#
# Metering: 5 credits per call.
# Cache hits free.
# Failed calls refunded.
# ============================================================

def search_google_businesses(
    query: str = ARCHITECTURE_QUERY,
    location: str = (
        "India, UAE, China, Italy, Germany, Turkey, "
        "Japan, USA, UK, Australia, Singapore"
    ),
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    dry_run: bool = False
) -> Any:
    """
    Search businesses, suppliers and showrooms via Google Business.
    Accepts query, location (or lat/lon).
    """
    clean_query = query.strip()
    loc_str = location
    if loc_str and "india" not in loc_str.lower() and not lat:
        loc_str = f"{loc_str}, India"
    elif not loc_str and not lat:
        loc_str = "Kochi, Kerala, India"

    cache_key = f"google_business:{clean_query}:{loc_str}:{lat}:{lon}:{dry_run}"

    if not dry_run and cache_key in _SOCIALCRAWL_CACHE:
        ts, data = _SOCIALCRAWL_CACHE[cache_key]
        if time.time() - ts < CACHE_TTL_SECONDS:
            cached = dict(data)
            cached["cached"] = True
            cached["credits_used"] = 0
            return cached

    params: Dict[str, Any] = {"query": clean_query}
    if lat is not None and lon is not None:
        params["lat"] = str(lat)
        params["lng"] = str(lon)
    elif loc_str:
        params["location"] = loc_str

    if dry_run or DRY_RUN:
        params["dry_run"] = 1

    body = socialcrawl(
        endpoint="google/business/search",
        params=params,
        timeout=GOOGLE_BUSINESS_TIMEOUT
    )

    if body is None:
        return {"success": True, "items": [], "total_items": 0}

    if dry_run or DRY_RUN:
        return {
            "success": True,
            "dry_run": True,
            "query": clean_query,
            "location": loc_str,
            "platform": "google_business",
            "estimate": body.get("data", {}).get("estimate", {}) if body else {},
            "credits_used": 0,
            "request_id": body.get("request_id") if body else None,
        }

    data = body.get("data") or {}
    raw_items = data.get("items") or []
    normalized_items = [normalize_google_business(item) for item in raw_items]

    result = {
        "success": True,
        "dry_run": False,
        "query": clean_query,
        "location": loc_str,
        "platform": "google_business",
        "total_items": len(normalized_items),
        "items": normalized_items,
        "credits_used": body.get("credits_used", 5),
        "credits_remaining": body.get("credits_remaining"),
        "request_id": body.get("request_id"),
    }

    if not dry_run and not DRY_RUN:
        _SOCIALCRAWL_CACHE[cache_key] = (time.time(), result)

    return result






# Alias for singular / plural consistency
search_google_business = search_google_businesses


# ============================================================
# 5. GOOGLE SHOPPING PRODUCT SEARCH
# GET /v1/google_shopping/product
#
# Metering: 1 credit per call.
# Cache hits free.
# Failed calls refunded.
# Preserves the supplied "gid" parameter.
# ============================================================

def search_google_shopping(
    query: str = ARCHITECTURE_QUERY,
    gid: Optional[str] = None,
    product_id: Optional[str] = None,
    country: str = "IN",
    dry_run: bool = False
) -> Any:
    """
    Search or lookup Google Shopping products.
    Preserves the supplied gid parameter initially.
    Supports single product lookup (1 credit) and product keyword search (5 credits).
    """
    # Case A: gid or product_id provided
    lookup_gid = gid or (query if query != ARCHITECTURE_QUERY and len(query) < 40 and query.isdigit() else None)
    if lookup_gid or product_id:
        param_key = "gid" if lookup_gid else "product_id"
        param_val = lookup_gid or product_id
        cache_key = f"google_shopping:{param_key}:{param_val}:{dry_run}"

        if not dry_run and cache_key in _SOCIALCRAWL_CACHE:
            ts, data = _SOCIALCRAWL_CACHE[cache_key]
            if time.time() - ts < CACHE_TTL_SECONDS:
                return data

        params: Dict[str, Any] = {param_key: param_val}
        if dry_run or DRY_RUN:
            params["dry_run"] = 1

        body = socialcrawl(
            endpoint="google_shopping/product",
            params=params,
            timeout=GOOGLE_SHOPPING_TIMEOUT
        )

        if body is None:
            return {"success": True, "items": [], "total_items": 0}

        if dry_run or DRY_RUN:
            return {
                "success": True,
                "dry_run": True,
                "param": param_key,
                "value": param_val,
                "platform": "google_shopping",
                "estimate": body.get("data", {}).get("estimate", {}) if body else {},
                "credits_used": 0,
                "request_id": body.get("request_id") if body else None,
            }

        data = body.get("data") or {}
        norm = normalize_google_shopping(data)
        result = {
            "success": True,
            "dry_run": False,
            "gid": lookup_gid,
            "product_id": product_id,
            "platform": "google_shopping",
            "total_items": 1 if norm else 0,
            "items": [norm] if norm else [],
            "credits_used": body.get("credits_used", 1),
            "credits_remaining": body.get("credits_remaining"),
            "request_id": body.get("request_id"),
        }

        if not dry_run and not DRY_RUN:
            _SOCIALCRAWL_CACHE[cache_key] = (time.time(), result)
        return result

    # Case B: Search query for products
    clean_query = query.strip()
    cache_key = f"google_shopping_search:{clean_query}:{country}:{dry_run}"

    if not dry_run and cache_key in _SOCIALCRAWL_CACHE:
        ts, data = _SOCIALCRAWL_CACHE[cache_key]
        if time.time() - ts < CACHE_TTL_SECONDS:
            cached = dict(data)
            cached["cached"] = True
            cached["credits_used"] = 0
            return cached

    params = {"query": clean_query}
    if country:
        params["country"] = country
    if dry_run or DRY_RUN:
        params["dry_run"] = 1

    body = socialcrawl(
        endpoint="google_shopping/product-search",
        params=params,
        timeout=GOOGLE_SHOPPING_TIMEOUT
    )

    if body is None:
        return {"success": True, "items": [], "total_items": 0}

    if dry_run or DRY_RUN:
        return {
            "success": True,
            "dry_run": True,
            "query": clean_query,
            "platform": "google_shopping",
            "estimate": body.get("data", {}).get("estimate", {}) if body else {},
            "credits_used": 0,
            "request_id": body.get("request_id") if body else None,
        }

    data = body.get("data") or {}
    raw_items = data.get("items") or []
    normalized_items = [normalize_google_shopping(item) for item in raw_items]

    result = {
        "success": True,
        "dry_run": False,
        "query": clean_query,
        "platform": "google_shopping",
        "total_items": len(normalized_items),
        "items": normalized_items,
        "credits_used": body.get("credits_used", 5),
        "credits_remaining": body.get("credits_remaining"),
        "request_id": body.get("request_id"),
    }

    if not dry_run and not DRY_RUN:
        _SOCIALCRAWL_CACHE[cache_key] = (time.time(), result)

    return result






# ============================================================
# 5b. TWITTER (X) AI SEARCH
# GET /v1/twitter/ai-search
#
# Metering: 5 credits per call. Cache hits are free and failed calls refunded.
# Timeout: 80 seconds.
# ============================================================

def search_twitter_ai(
    query: str = ARCHITECTURE_QUERY,
    cursor: Optional[str] = None,
    dry_run: bool = False
) -> Any:
    """
    Search Twitter/X via SocialCrawl GET /v1/twitter/ai-search.
    Supports dry-run price checking, caching, and idempotency key.
    """
    clean_query = query.strip()
    cache_key = f"twitter:{clean_query}:{cursor}:{dry_run}"

    if not dry_run and cache_key in _SOCIALCRAWL_CACHE:
        ts, data = _SOCIALCRAWL_CACHE[cache_key]
        if time.time() - ts < CACHE_TTL_SECONDS:
            cached = dict(data)
            cached["cached"] = True
            cached["credits_used"] = 0
            return cached

    params: Dict[str, Any] = {
        "query": clean_query,
    }
    if cursor:
        params["cursor"] = cursor
    if dry_run or DRY_RUN:
        params["dry_run"] = 1

    if dry_run or DRY_RUN:
        body = socialcrawl(
            endpoint="twitter/ai-search",
            params=params,
            timeout=TWITTER_TIMEOUT
        )
        return {
            "success": True,
            "dry_run": True,
            "query": clean_query,
            "platform": "x",
            "estimate": body.get("data", {}).get("estimate", {}) if body else {},
            "credits_used": 0,
            "request_id": body.get("request_id") if body else None,
        }

    body = socialcrawl(
        endpoint="twitter/ai-search",
        params=params,
        timeout=TWITTER_TIMEOUT
    )
    if body is None:
        return {
            "success": True,
            "dry_run": False,
            "query": clean_query,
            "platform": "x",
            "total_items": 0,
            "items": [],
            "has_more": False,
        }

    data = body.get("data") or {}
    raw_items = data.get("items") or data.get("posts") or (data if isinstance(data, list) else [])
    normalized_items = [normalize_twitter_post(item) for item in raw_items]

    result = {
        "success": True,
        "dry_run": False,
        "query": clean_query,
        "platform": "x",
        "total_items": len(normalized_items),
        "items": normalized_items,
        "has_more": bool(body.get("pagination", {}).get("has_more")),
        "cursor": body.get("pagination", {}).get("next_cursor"),
        "credits_used": body.get("credits_used", 5),
        "credits_remaining": body.get("credits_remaining"),
        "request_id": body.get("request_id"),
    }

    if not dry_run and not DRY_RUN:
        _SOCIALCRAWL_CACHE[cache_key] = (time.time(), result)

    return result






# ============================================================
# 6. UNIFIED ARCHITECT AI SEARCH
# ============================================================

def search_all_sources(
    query: str = ARCHITECTURE_QUERY,
    location: str = (
        "India, UAE, China, Italy, Germany, Turkey, "
        "Japan, USA, UK, Australia, Singapore"
    ),
    instagram_date_posted: str = "last-month",
    max_pages: int = 1,
    sources: Optional[List[str]] = None,
    dry_run: bool = False
) -> dict[str, Any]:

    selected_sources = [s.lower().strip() for s in sources] if sources else ["instagram", "youtube", "reddit", "x", "google_business", "google_shopping"]

    results: Dict[str, Any] = {
        "instagram": [],
        "youtube": [],
        "reddit": [],
        "x": [],
        "google_business": None,
        "google_shopping": None,
        "errors": {}
    }

    # Each source is isolated so one failure does not
    # prevent the other sources from returning results.
    searches = []

    if "instagram" in selected_sources:
        searches.append((
            "instagram",
            lambda: search_instagram_reels(
                query=query,
                date_posted=instagram_date_posted,
                max_pages=max_pages,
                dry_run=dry_run
            )
        ))

    if "youtube" in selected_sources:
        searches.append((
            "youtube",
            lambda: search_youtube(
                query=query,
                max_pages=max_pages,
                dry_run=dry_run
            )
        ))

    if "reddit" in selected_sources:
        searches.append((
            "reddit",
            lambda: search_reddit(
                query=query,
                max_pages=max_pages,
                dry_run=dry_run
            )
        ))

    if "x" in selected_sources or "twitter" in selected_sources:
        searches.append((
            "x",
            lambda: search_twitter_ai(
                query=query,
                dry_run=dry_run
            )
        ))

    if "google_business" in selected_sources or "businesses" in selected_sources:
        searches.append((
            "google_business",
            lambda: search_google_businesses(
                query=query,
                location=location,
                dry_run=dry_run
            )
        ))

    if "google_shopping" in selected_sources or "shopping" in selected_sources:
        searches.append((
            "google_shopping",
            lambda: search_google_shopping(
                query=query,
                dry_run=dry_run
            )
        ))

    for source, search_function in searches:
        try:
            results[source] = search_function()
        except Exception as exc:
            results["errors"][source] = str(exc)

    return results


# ============================================================
# 7. LOCAL TEST
# ============================================================

if __name__ == "__main__":
    print("SocialCrawl dry run:", DRY_RUN)

    result = search_all_sources(
        query=ARCHITECTURE_QUERY,
        location=(
            "India, UAE, China, Italy, Germany, Turkey, "
            "Japan, USA, UK, Australia, Singapore"
        ),
        instagram_date_posted="last-month",
        max_pages=1,
        dry_run=True
    )

    for source, data in result.items():
        if source == "errors":
            print("\nErrors:", data)
        elif isinstance(data, list):
            print(f"\n{source}: {len(data)} items")
        else:
            print(f"\n{source}: {'Available' if data else 'No results'}")

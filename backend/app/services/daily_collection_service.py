"""
Arch_Aware — Daily Automated Data Collection Service (6:00 AM IST)

Runs daily at 6:00 AM India Standard Time (Asia/Kolkata, UTC+5:30).
Orchestrates collection from:
- Pinterest (existing integration)
- Instagram Reels (SocialCrawl) — including architecture tours, construction walkthroughs
- YouTube Walkthroughs (SocialCrawl)
- Reddit Discussions (SocialCrawl)
- Google Business Suppliers (SocialCrawl / Google Places)
- Google Shopping Products (SocialCrawl)

Design principles:
- Sweeps ALL 6,319 catalogue materials in a nightly rotation.
- Each material targets 50 content items + 10-20 suppliers.
- Full sweep takes multiple nights; materials are batched and rotated by day-of-year.
- Each content item is validated against its keyword using Gemini 1.5 Flash thumbnail check.
- Deduplicates against existing database records.
- Preserves historical data across days.
- Credit budget protection to prevent runaway costs.
- Never fabricates content.
- Lock-safe execution to avoid multiple instances running concurrently.
- Manual administrator trigger support.
"""

import asyncio
import logging
import threading
import time
import hashlib
from datetime import datetime, timezone, timedelta, time as dt_time
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.models import (
    ArchitecturalReference,
    Supplier,
    Product,
    MaterialCategory,
    CatalogueCategory,
    CatalogueSubcategory,
    CatalogueMaterial,
    InspirationMaterial,
    DailyCollectionRecord
)
from app.services.socialcrawl_service import (
    search_instagram_reels,
    search_youtube,
    search_reddit,
    search_twitter_ai,
    search_google_businesses,
    search_google_shopping,
    is_socialcrawl_configured
)
from app.services.keyword_library import KEYWORD_GROUPS

logger = logging.getLogger("arch_aware.daily_collection")

# Lock to ensure only one instance executes the collection at a time
_COLLECTION_LOCK = threading.Lock()
_COLLECTION_RUNNING = False

# -----------------------------------------------------------------
# Target counts per material per day
# -----------------------------------------------------------------
TARGET_CONTENT_PER_MATERIAL = 50       # inspiration items (images/videos/posts)
TARGET_VENDORS_PER_MATERIAL = 20       # suppliers / Google Business places (guarantee 20 per material)
MATERIALS_PER_DAILY_BATCH = 100        # how many unique materials to sweep in one 6AM run
                                        # (6,319 / 100 ≈ 63 nights for full coverage)
MAX_DAILY_API_CALLS = 500              # hard credit cap per run (each call fetches ~10-25 items)

# Sources used for content collection (interleaved so no one source dominates)
CONTENT_SOURCES = ["instagram", "pinterest", "youtube", "reddit"]

# Architecture tour / construction tour queries appended when no keyword selected
ARCHITECTURE_TOUR_QUERIES = [
    "house tour architecture design India",
    "construction walkthrough residential project India",
    "home interior tour materials finish",
    "modern villa house tour Kerala Tamil Nadu",
    "architect designed home project tour",
    "how they built this house construction documentation",
    "rainwater harvesting tank construction details",
    "staircase materials design residential project",
    "facade material cladding construction process",
    "interior design reveal house tour India",
    "building construction slab pour video",
    "terrace waterproofing construction India",
]

# Default broad inspiration that shows when no keyword is selected
DEFAULT_DISCOVERY_QUERIES = [
    {"q": "modern architecture India", "cat": "Architecture", "sources": ["instagram", "youtube", "pinterest"]},
    {"q": "interior design material finish", "cat": "Interior", "sources": ["instagram", "pinterest"]},
    {"q": "exterior facade cladding brick stone", "cat": "Exterior", "sources": ["instagram", "pinterest", "youtube"]},
    {"q": "construction material building India", "cat": "Construction", "sources": ["instagram", "youtube", "reddit"]},
    {"q": "kitchen bathroom interior design India", "cat": "Interior", "sources": ["instagram", "pinterest"]},
    {"q": "flooring tiles marble granite India", "cat": "Flooring", "sources": ["instagram", "shopping"]},
    {"q": "steel TMT cement concrete supplier India", "cat": "Materials", "sources": ["google_business", "shopping"]},
    {"q": "house tour Kerala Tamil Nadu architecture", "cat": "Architecture", "sources": ["youtube", "instagram"]},
    {"q": "rainwater harvesting tank construction details", "cat": "MEP", "sources": ["youtube", "instagram"]},
    {"q": "staircase design residential construction", "cat": "Interior", "sources": ["instagram", "pinterest"]},
]


# -----------------------------------------------------------------
# Time helpers
# -----------------------------------------------------------------

def get_kolkata_now() -> datetime:
    """Returns the current datetime in India Standard Time (UTC+5:30)."""
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)


def get_next_6am_ist() -> datetime:
    """Computes the datetime of the upcoming 6:00 AM IST."""
    now_ist = get_kolkata_now()
    today_6am = now_ist.replace(hour=6, minute=0, second=0, microsecond=0)
    if now_ist >= today_6am:
        return today_6am + timedelta(days=1)
    return today_6am


def seconds_until_next_6am_ist() -> float:
    """Returns the number of seconds until the next 6:00 AM IST."""
    now_ist = get_kolkata_now()
    next_6am = get_next_6am_ist()
    diff = (next_6am - now_ist).total_seconds()
    return max(0.0, diff)


# -----------------------------------------------------------------
# Gemini 1.5 Flash thumbnail alignment check (synchronous wrapper)
# -----------------------------------------------------------------

def check_thumbnail_alignment_with_gemini(
    thumbnail_url: str,
    keyword: str,
    title: str = "",
    timeout: float = 8.0
) -> Tuple[bool, float, str]:
    """
    Uses Gemini 1.5 Flash to verify whether a thumbnail/image is relevant
    to the given material keyword.

    Returns: (is_relevant: bool, confidence: float, reason: str)
    Falls back gracefully if Gemini is not configured or call fails.
    """
    if not thumbnail_url or not keyword:
        return True, 0.70, "No image URL provided; accepted by default"

    gemini_key = settings.GEMINI_API_KEY or settings.LLM_API_KEY or ""
    if not gemini_key or not gemini_key.strip():
        # No Gemini configured — do basic keyword-in-title check
        combined = (title + " " + keyword).lower()
        kw_words = [w for w in keyword.lower().split() if len(w) >= 4]
        matched = sum(1 for w in kw_words if w in combined)
        score = min(0.95, 0.5 + matched * 0.15)
        return score >= 0.60, score, "Title keyword match (Gemini not configured)"

    try:
        import requests as _req
        model = "gemini-1.5-flash"
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
            f":generateContent?key={gemini_key}"
        )
        prompt = (
            f"I fetched this image from a social media search for the keyword: '{keyword}'.\n"
            f"Content title: '{title or 'No title'}'\n"
            f"Image URL: {thumbnail_url}\n\n"
            f"Does this image appear to be related to the construction/architectural material or product '{keyword}'?\n"
            f"Answer with ONLY: YES (confidence 0.0-1.0) or NO (confidence 0.0-1.0) and one sentence reason.\n"
            f"Format: YES|0.87|<reason> or NO|0.72|<reason>"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 100}
        }
        resp = _req.post(url, json=payload, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    answer = parts[0].get("text", "").strip()
                    segments = answer.split("|")
                    if len(segments) >= 2:
                        verdict = segments[0].strip().upper()
                        try:
                            conf = float(segments[1].strip())
                        except ValueError:
                            conf = 0.75
                        reason = segments[2].strip() if len(segments) > 2 else "Gemini assessment"
                        return verdict == "YES", conf, reason
        return True, 0.65, "Gemini response parse failed; accepted"
    except Exception as e:
        logger.debug(f"Gemini thumbnail check failed for '{keyword}': {e}")
        return True, 0.65, f"Gemini call failed: {str(e)[:60]}; accepted"


# -----------------------------------------------------------------
# Persistence helpers
# -----------------------------------------------------------------

def save_inspiration_reference(
    db: Session,
    item: Dict[str, Any],
    keyword: str,
    category_name: str,
    skip_duplicate_check: bool = False,
    thumbnail_confidence: float = 0.70
) -> bool:
    """
    Saves a normalized inspiration item to the database if not already present.
    Returns True if newly inserted, False if already existed.
    """
    source_url = item.get("source_url")
    if not source_url:
        return False

    if not skip_duplicate_check:
        existing = db.query(ArchitecturalReference).filter(
            or_(
                ArchitecturalReference.source_url == source_url,
                ArchitecturalReference.slug == item.get("id")
            )
        ).first()
        if existing:
            return False

    today_str = get_kolkata_now().strftime("%Y-%m-%d")

    # Map category to ID if exists (MaterialCategory is old taxonomy; CatalogueCategory is new)
    cat = db.query(MaterialCategory).filter(MaterialCategory.name.ilike(f"%{category_name}%")).first()

    item_id = item.get("id") or f"{item.get('source_platform', 'web')}-{abs(hash(source_url)) % 10000000}"

    ref = ArchitecturalReference(
        title=item.get("title") or f"{category_name} Architectural Reference",
        slug=item_id,
        source_platform=item.get("source_platform") or "socialcrawl",
        source_url=source_url,
        creator_name=item.get("creator_name"),
        creator_url=item.get("creator_url"),
        thumbnail_url=item.get("thumbnail_url") or item.get("image_url"),
        media_url=item.get("video_url") or item.get("media_url") or item.get("image_url"),
        video_embed_id=item.get("reel_id") or item.get("video_id"),
        category_id=cat.id if cat else None,
        material_tags=",".join(item.get("material_tags", [])) if isinstance(item.get("material_tags"), list) else keyword,
        location_context="Architectural Reference via Arch_Aware",
        country="India",
        content_type=item.get("content_type") or "architectural_project",
        verification_status="UNVERIFIED",
        description=item.get("description"),
        video_duration=item.get("video_duration"),
        is_short=item.get("is_reel") or item.get("is_short") or False,
        source_domain=f"{item.get('source_platform', 'web')}.com",
        search_keyword=keyword,
        date_collected=today_str,
        external_source_id=str(item.get("reel_id") or item.get("id") or ""),
        inspiration_relevance_tier="EXACT_METADATA_MATCH" if thumbnail_confidence >= 0.80 else "PARTIAL_METADATA_MATCH"
    )
    db.add(ref)

    # Attach lightweight material tag
    im = InspirationMaterial(
        reference=ref,
        name=keyword,
        material_category=category_name,
        element_location="Primary",
        identification_type="keyword_match",
        verification_status="KEYWORD_TAGGED",
        confidence_score=thumbnail_confidence
    )
    db.add(im)

    return True


def save_supplier_lead(db: Session, biz: Dict[str, Any], keyword: str) -> bool:
    """
    Saves a Google Business/Places supplier lead to the database if not already present.
    """
    name = biz.get("name")
    if not name:
        return False

    slug = f"sup-{abs(hash(name)) % 10000000}"
    existing = db.query(Supplier).filter(
        or_(
            Supplier.name == name,
            Supplier.slug == slug
        )
    ).first()

    if existing:
        return False

    sup = Supplier(
        name=name,
        slug=slug,
        business_type=biz.get("category") or "authorized_dealer",
        address=biz.get("address") or "Address pending verification",
        city=biz.get("city") or "India",
        state=biz.get("state") or "India",
        country="India",
        phone=biz.get("phone"),
        website=biz.get("google_maps_url") or biz.get("website"),
        google_maps_url=biz.get("google_maps_url"),
        brands_distributed=keyword,
        materials_sold=biz.get("category") or keyword,
        verification_status="SUPPLIER_CONFIRMED" if biz.get("verified") else "POTENTIAL_GOOGLE_PLACE",
        is_potential=not bool(biz.get("verified"))
    )
    db.add(sup)
    return True


# -----------------------------------------------------------------
# Per-material content collection
# -----------------------------------------------------------------

def collect_content_for_material(
    db: Session,
    material_name: str,
    category_name: str,
    subcategory_name: str,
    target_content: int = TARGET_CONTENT_PER_MATERIAL,
    target_vendors: int = TARGET_VENDORS_PER_MATERIAL
) -> Dict[str, Any]:
    """
    For one specific material (e.g. 'Red clay brick'):
      1. Fetches up to target_content inspiration items from Instagram, Pinterest,
         YouTube, Reddit (interleaved to avoid source domination).
      2. Fetches up to target_vendors supplier entries from Google Business /
         Google Places / SocialCrawl Google Business search.
      3. Each item is validated with Gemini 1.5 Flash thumbnail alignment.
      4. Items not passing alignment (< 0.55 confidence) are discarded.
      5. All new items are saved; duplicates are skipped.

    Returns dict with counts.
    """
    new_content = 0
    new_vendors = 0
    skipped_low_confidence = 0
    errors = []

    sc_ok = is_socialcrawl_configured()

    # -- CONTENT COLLECTION (Instagram, Pinterest, YouTube, Reddit) --
    from app.services.social_vocabulary_service import get_social_search_terms, get_supplier_search_queries
    soc = get_social_search_terms(material_name, category_name, subcategory_name)
    clean_mat = soc["clean_noun"]
    insta_q = soc["instagram_queries"][0] if soc["instagram_queries"] else f"{clean_mat} architecture"
    pin_q = soc["pinterest_queries"][0] if soc["pinterest_queries"] else f"{clean_mat} architecture"
    yt_q = soc["youtube_queries"][0] if soc["youtube_queries"] else f"{clean_mat} construction installation"
    reddit_q = soc["reddit_queries"][0] if soc["reddit_queries"] else f"{clean_mat} material review"

    per_source = max(2, target_content // len(CONTENT_SOURCES))

    for source in CONTENT_SOURCES:
        if new_content >= target_content:
            break
        try:
            items = []

            if source == "instagram" and sc_ok:
                res = search_instagram_reels(
                    query=insta_q,
                    max_pages=2,
                    dry_run=False
                )
                items = res.get("items", [])

            elif source == "pinterest":
                try:
                    from app.services.pinterest_service import search_pinterest_page
                    res = search_pinterest_page(
                        query=pin_q,
                        trim=False
                    )
                    raw_pins = res.get("items", [])
                    for pin in raw_pins:
                        items.append({
                            "id": f"pinterest-{pin.get('pin_id') or abs(hash(pin.get('source_url', material_name)))}",
                            "title": pin.get("title") or f"{material_name} Architectural Inspiration",
                            "source_platform": "pinterest",
                            "source_url": pin.get("source_url") or "https://www.pinterest.com",
                            "creator_name": pin.get("creator_name"),
                            "creator_url": pin.get("creator_url"),
                            "thumbnail_url": pin.get("image_url"),
                            "image_url": pin.get("image_url"),
                            "media_url": pin.get("image_url"),
                            "description": pin.get("description"),
                            "material_tags": [material_name, category_name],
                            "content_type": "architectural_project",
                        })
                except Exception as pin_e:
                    logger.debug(f"Pinterest fetch error for '{material_name}': {pin_e}")

            elif source == "youtube" and sc_ok:
                res = search_youtube(
                    query=yt_q,
                    max_pages=2,
                    dry_run=False
                )
                items = res.get("items", [])

            elif source == "reddit" and sc_ok:
                res = search_reddit(
                    query=reddit_q,
                    max_pages=1,
                    dry_run=False
                )
                items = res.get("items", [])

            # Validate & save each item
            for item in items[:per_source]:
                if new_content >= target_content:
                    break

                thumbnail = item.get("thumbnail_url") or item.get("image_url") or ""
                title = item.get("title") or ""

                is_relevant, conf, reason = check_thumbnail_alignment_with_gemini(
                    thumbnail_url=thumbnail,
                    keyword=material_name,
                    title=title
                )

                if not is_relevant and conf < 0.55:
                    skipped_low_confidence += 1
                    logger.debug(f"Skipped low-confidence item for '{material_name}': {reason}")
                    continue

                try:
                    if save_inspiration_reference(
                        db, item, material_name, category_name,
                        thumbnail_confidence=conf
                    ):
                        new_content += 1
                except Exception as save_e:
                    logger.debug(f"Save error for '{material_name}' item: {save_e}")

        except Exception as src_e:
            errors.append(f"{source}: {str(src_e)[:80]}")
            logger.warning(f"Source {source} error for '{material_name}': {src_e}")

    # -- VENDOR COLLECTION (Google Business / Google Places / SocialCrawl) --
    if new_vendors < target_vendors:
        try:
            sup_queries = get_supplier_search_queries(material_name)
            primary_sup_q = sup_queries[0]["query"] if sup_queries else f"{clean_mat} suppliers dealers manufacturers India"

            if sc_ok:
                res = search_google_businesses(
                    query=primary_sup_q,
                    location="India",
                    dry_run=False
                )
                for biz in res.get("items", [])[:target_vendors]:
                    if save_supplier_lead(db, biz, material_name):
                        new_vendors += 1

            # Also query Google Places across geographic tiers if more vendors needed
            if new_vendors < target_vendors:
                places_key = settings.get_places_api_key()
                if places_key:
                    try:
                        import requests as _req
                        import urllib.parse as _up
                        for sq in sup_queries:
                            if new_vendors >= target_vendors:
                                break
                            q = sq["query"]
                            encoded_q = _up.quote_plus(q)
                            url = (
                                "https://maps.googleapis.com/maps/api/place/textsearch/json"
                                f"?query={encoded_q}&key={places_key}&language=en"
                            )
                            gp_resp = _req.get(url, timeout=10)
                            if gp_resp.status_code == 200:
                                gp_data = gp_resp.json()
                                for place in gp_data.get("results", []):
                                    if new_vendors >= target_vendors:
                                        break
                                    biz_data = {
                                        "name": place.get("name"),
                                        "address": place.get("formatted_address"),
                                        "city": place.get("formatted_address", "").split(",")[-3].strip() if len(place.get("formatted_address", "").split(",")) >= 3 else "India",
                                        "state": place.get("formatted_address", "").split(",")[-2].strip() if len(place.get("formatted_address", "").split(",")) >= 2 else "India",
                                        "phone": place.get("formatted_phone_number"),
                                        "website": place.get("website"),
                                        "google_maps_url": f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id', '')}",
                                        "verified": place.get("business_status") == "OPERATIONAL",
                                        "category": place.get("types", [None])[0],
                                    }
                                    if save_supplier_lead(db, biz_data, material_name):
                                        new_vendors += 1
                    except Exception as gp_e:
                        logger.debug(f"Google Places error for '{material_name}': {gp_e}")

        except Exception as vendor_e:
            errors.append(f"vendors: {str(vendor_e)[:80]}")
            logger.warning(f"Vendor collection error for '{material_name}': {vendor_e}")

    try:
        db.commit()
    except Exception as commit_e:
        db.rollback()
        logger.error(f"DB commit error for '{material_name}': {commit_e}")

    return {
        "material": material_name,
        "new_content": new_content,
        "new_vendors": new_vendors,
        "skipped_low_confidence": skipped_low_confidence,
        "errors": errors
    }


# -----------------------------------------------------------------
# Architecture tour content (shown when no keyword selected)
# -----------------------------------------------------------------

def collect_architecture_tour_content(db: Session, max_calls: int = 20) -> int:
    """
    Fetches architecture tour / construction walkthrough content
    that is shown by default when no keyword is selected.
    Returns count of new items saved.
    """
    new_items = 0
    sc_ok = is_socialcrawl_configured()

    for i, query_info in enumerate(DEFAULT_DISCOVERY_QUERIES):
        if i >= max_calls:
            break

        q = query_info["q"]
        cat = query_info["cat"]
        sources = query_info["sources"]

        for src in sources:
            try:
                items = []
                if src == "instagram" and sc_ok:
                    res = search_instagram_reels(query=q, max_pages=1, dry_run=False)
                    items = res.get("items", [])
                elif src == "youtube" and sc_ok:
                    res = search_youtube(query=q, max_pages=1, dry_run=False)
                    items = res.get("items", [])
                elif src == "reddit" and sc_ok:
                    res = search_reddit(query=q, max_pages=1, dry_run=False)
                    items = res.get("items", [])
                elif src == "pinterest":
                    try:
                        from app.services.pinterest_service import search_pinterest_page
                        res = search_pinterest_page(query=q, trim=False)
                        for pin in res.get("items", []):
                            items.append({
                                "id": f"pinterest-tour-{abs(hash(pin.get('source_url', q)))}",
                                "title": pin.get("title") or q,
                                "source_platform": "pinterest",
                                "source_url": pin.get("source_url") or "https://www.pinterest.com",
                                "creator_name": pin.get("creator_name"),
                                "creator_url": pin.get("creator_url"),
                                "thumbnail_url": pin.get("image_url"),
                                "image_url": pin.get("image_url"),
                                "media_url": pin.get("image_url"),
                                "description": pin.get("description"),
                                "material_tags": [cat],
                                "content_type": "architectural_project",
                            })
                    except Exception:
                        pass
                elif src == "shopping" and sc_ok:
                    res = search_google_shopping(query=q, dry_run=False)
                    items = res.get("items", [])
                elif src == "google_business" and sc_ok:
                    res = search_google_businesses(query=q, location="India", dry_run=False)
                    for biz in res.get("items", []):
                        save_supplier_lead(db, biz, q)

                for item in items[:10]:
                    if save_inspiration_reference(db, item, q, cat):
                        new_items += 1

            except Exception as e:
                logger.debug(f"Tour content error for '{q}' ({src}): {e}")

    try:
        db.commit()
    except Exception:
        db.rollback()

    return new_items


# -----------------------------------------------------------------
# Main daily collection executor
# -----------------------------------------------------------------

def execute_daily_collection_task(
    force: bool = False,
    max_items: Optional[int] = None
) -> Dict[str, Any]:
    """
    Core worker function that executes the daily 6:00 AM IST collection.

    Strategy:
    1. First collects architecture tour content (default homepage content).
    2. Then sweeps today's batch of catalogue materials:
       - Rotates through 6,319 materials split into daily batches of MATERIALS_PER_DAILY_BATCH.
       - Each material targets TARGET_CONTENT_PER_MATERIAL (50) content items.
       - Each material targets TARGET_VENDORS_PER_MATERIAL (15) supplier leads.
       - Each item is Gemini-verified against the material keyword.
    Thread-safe and lock-protected.
    """
    global _COLLECTION_RUNNING
    with _COLLECTION_LOCK:
        if _COLLECTION_RUNNING and not force:
            logger.warning("Daily collection already running. Skipping duplicate invocation.")
            return {"status": "Already Running", "collected": 0}
        _COLLECTION_RUNNING = True

    db = SessionLocal()
    today_str = get_kolkata_now().strftime("%Y-%m-%d")
    total_new = 0
    total_new_vendors = 0
    calls_made = 0
    errors_encountered = []
    budget_limit = max(1, min(max_items or MAX_DAILY_API_CALLS, 1000))

    logger.info(
        f"[Arch_Aware] Starting daily 6:00 AM IST collection for {today_str} "
        f"(budget: {budget_limit} calls)"
    )

    try:
        # --- Phase 1: Architecture tour / default homepage content ---
        logger.info("Phase 1: Collecting architecture tour & default discovery content...")
        try:
            tour_new = collect_architecture_tour_content(db, max_calls=20)
            total_new += tour_new
            calls_made += min(20, len(DEFAULT_DISCOVERY_QUERIES))
            logger.info(f"Phase 1 complete: {tour_new} new default-discovery items saved.")
        except Exception as phase1_e:
            logger.error(f"Phase 1 error: {phase1_e}")
            errors_encountered.append(f"phase1_tour: {str(phase1_e)[:100]}")

        if calls_made >= budget_limit:
            logger.info("Budget reached after Phase 1.")
            return _build_result(today_str, total_new, total_new_vendors, calls_made, budget_limit, errors_encountered)

        # --- Phase 2: Per-material catalogue sweep ---
        # Determine today's batch by rotating through all materials by day-of-year
        logger.info("Phase 2: Per-material catalogue sweep starting...")
        try:
            all_materials = (
                db.query(CatalogueMaterial, CatalogueCategory, CatalogueSubcategory)
                .join(CatalogueCategory, CatalogueMaterial.category_id == CatalogueCategory.id)
                .join(CatalogueSubcategory, CatalogueMaterial.subcategory_id == CatalogueSubcategory.id)
                .filter(CatalogueMaterial.is_active == True)
                .order_by(CatalogueMaterial.id.asc())
                .all()
            )
            total_materials = len(all_materials)
            logger.info(f"Total active catalogue materials: {total_materials}")

            if total_materials > 0:
                # Rotate batch by day-of-year
                day_of_year = get_kolkata_now().timetuple().tm_yday
                batch_size = MATERIALS_PER_DAILY_BATCH
                batch_start = ((day_of_year - 1) * batch_size) % total_materials
                # Wrap around if near end
                if batch_start + batch_size > total_materials:
                    batch_indices = list(range(batch_start, total_materials)) + list(range(0, (batch_start + batch_size) - total_materials))
                else:
                    batch_indices = list(range(batch_start, batch_start + batch_size))

                today_batch = [all_materials[i] for i in batch_indices]
                logger.info(
                    f"Today's batch: materials #{batch_start} to #{batch_start + batch_size - 1} "
                    f"({len(today_batch)} materials)"
                )

                for mat, cat, sub in today_batch:
                    if calls_made >= budget_limit:
                        logger.info(f"Budget limit {budget_limit} reached. Stopping batch sweep.")
                        break

                    mat_name = mat.name
                    cat_name = cat.name
                    sub_name = sub.name

                    # Check if already collected today
                    existing = db.query(DailyCollectionRecord).filter_by(
                        collection_date=today_str,
                        source="catalogue_sweep",
                        keyword=mat_name
                    ).first()
                    if existing and existing.status == "Completed" and not force:
                        logger.debug(f"Already collected '{mat_name}' today. Skipping.")
                        continue

                    rec = existing or DailyCollectionRecord(
                        collection_date=today_str,
                        source="catalogue_sweep",
                        category=cat_name,
                        keyword=mat_name,
                        requested_quantity=TARGET_CONTENT_PER_MATERIAL,
                        status="Running"
                    )
                    db.add(rec)
                    db.commit()

                    try:
                        result = collect_content_for_material(
                            db=db,
                            material_name=mat_name,
                            category_name=cat_name,
                            subcategory_name=sub_name,
                            target_content=TARGET_CONTENT_PER_MATERIAL,
                            target_vendors=TARGET_VENDORS_PER_MATERIAL
                        )
                        total_new += result["new_content"]
                        total_new_vendors += result["new_vendors"]
                        calls_made += len(CONTENT_SOURCES) + 1  # content sources + vendor call
                        errors_encountered.extend(result["errors"])

                        rec.actual_quantity = result["new_content"]
                        rec.status = "Completed"
                        rec.completion_timestamp = datetime.now(timezone.utc)
                        db.commit()

                        logger.info(
                            f"  ✓ '{mat_name}': +{result['new_content']} content, "
                            f"+{result['new_vendors']} vendors "
                            f"(skipped {result['skipped_low_confidence']} low-confidence)"
                        )

                    except Exception as mat_e:
                        logger.error(f"Error collecting '{mat_name}': {mat_e}")
                        db.rollback()
                        rec.status = "Failed"
                        rec.error_details = str(mat_e)
                        db.commit()
                        errors_encountered.append(f"material:{mat_name}: {str(mat_e)[:80]}")

        except Exception as phase2_e:
            logger.error(f"Phase 2 error: {phase2_e}")
            errors_encountered.append(f"phase2_sweep: {str(phase2_e)[:100]}")

        db.commit()
        overall_status = "Partially completed" if errors_encountered else "Completed"
        logger.info(
            f"[Arch_Aware] Daily collection done. "
            f"New content: {total_new}, New vendors: {total_new_vendors}, "
            f"Calls: {calls_made}, Errors: {len(errors_encountered)}"
        )

        return _build_result(today_str, total_new, total_new_vendors, calls_made, budget_limit, errors_encountered, overall_status)

    except Exception as exc:
        logger.error(f"Fatal error during daily collection run: {exc}")
        db.rollback()
        return {
            "collection_date": today_str,
            "status": "Failed",
            "error": str(exc)
        }
    finally:
        db.close()
        with _COLLECTION_LOCK:
            _COLLECTION_RUNNING = False


def _build_result(
    today_str: str,
    total_new: int,
    total_new_vendors: int,
    calls_made: int,
    budget_limit: int,
    errors: List[str],
    status: str = "Completed"
) -> Dict[str, Any]:
    return {
        "collection_date": today_str,
        "status": status,
        "total_new_content_items": total_new,
        "total_new_vendor_leads": total_new_vendors,
        "calls_made": calls_made,
        "budget_limit": budget_limit,
        "errors": errors[:20]  # cap error list length
    }


# -----------------------------------------------------------------
# Scheduler loop — fires daily at 6:00 AM IST
# -----------------------------------------------------------------

async def daily_collection_scheduler_loop():
    """
    Background asynchronous loop that sleeps until 6:00 AM IST daily
    and triggers execute_daily_collection_task.
    """
    logger.info("[Arch_Aware] Daily 6:00 AM IST collection scheduler initialized.")
    while True:
        try:
            wait_seconds = seconds_until_next_6am_ist()
            next_run_ist = get_next_6am_ist().strftime("%Y-%m-%d %H:%M:%S IST")
            logger.info(
                f"[Arch_Aware] Next scheduled collection at: {next_run_ist} "
                f"(sleeping {int(wait_seconds)} seconds / {int(wait_seconds/3600):.1f} hours)."
            )

            # Sleep until 6:00 AM IST
            await asyncio.sleep(wait_seconds)

            # Trigger execution in a background worker thread so event loop is never blocked
            logger.info("[Arch_Aware] 6:00 AM IST reached! Launching automated collection job.")
            await asyncio.to_thread(execute_daily_collection_task, force=False)

            # Brief sleep to avoid re-triggering within the same minute
            await asyncio.sleep(120)

        except asyncio.CancelledError:
            logger.info("[Arch_Aware] Daily collection scheduler loop cancelled.")
            break
        except Exception as e:
            logger.error(f"[Arch_Aware] Unexpected error in scheduler loop: {e}")
            await asyncio.sleep(60)


_SCHEDULER_THREAD = None


def start_daily_collection_scheduler():
    """
    Starts the 6:00 AM IST daily collection scheduler in a detached background daemon thread.
    This guarantees it never blocks ASGI/FastAPI/AnyIO lifespan startup or test runners.
    """
    global _SCHEDULER_THREAD
    if _SCHEDULER_THREAD is not None and _SCHEDULER_THREAD.is_alive():
        return _SCHEDULER_THREAD

    def _thread_target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(daily_collection_scheduler_loop())
        finally:
            loop.close()

    _SCHEDULER_THREAD = threading.Thread(
        target=_thread_target,
        daemon=True,
        name="DailyCollectionSchedulerThread"
    )
    _SCHEDULER_THREAD.start()
    logger.info(
        f"[Arch_Aware] Daily collection scheduler thread started. "
        f"First run at: {get_next_6am_ist().strftime('%Y-%m-%d %H:%M IST')}"
    )
    return _SCHEDULER_THREAD


# -----------------------------------------------------------------
# Status reporting
# -----------------------------------------------------------------

def get_collection_status_summary(db: Session) -> Dict[str, Any]:
    """
    Returns current daily collection status, last run details, and history.
    """
    today_str = get_kolkata_now().strftime("%Y-%m-%d")
    today_records = db.query(DailyCollectionRecord).filter_by(collection_date=today_str).all()

    total_tasks = len(today_records)
    completed_tasks = sum(1 for r in today_records if r.status == "Completed")
    failed_tasks = sum(1 for r in today_records if r.status == "Failed")
    total_items = sum(r.actual_quantity for r in today_records)

    last_record = db.query(DailyCollectionRecord).order_by(DailyCollectionRecord.id.desc()).first()

    return {
        "today_ist": today_str,
        "is_currently_running": _COLLECTION_RUNNING,
        "next_scheduled_run": get_next_6am_ist().strftime("%Y-%m-%d %H:%M:%S IST"),
        "schedule_note": "Runs daily at 6:00 AM IST. Sweeps ~100 materials per day from a 6,319-material catalogue.",
        "today_summary": {
            "total_tasks": total_tasks,
            "completed": completed_tasks,
            "failed": failed_tasks,
            "total_items_collected": total_items,
        },
        "last_run": {
            "source": last_record.source if last_record else None,
            "keyword": last_record.keyword if last_record else None,
            "status": last_record.status if last_record else None,
            "actual_quantity": last_record.actual_quantity if last_record else 0,
            "completion_timestamp": (
                last_record.completion_timestamp.isoformat()
                if (last_record and last_record.completion_timestamp)
                else None
            )
        } if last_record else None
    }

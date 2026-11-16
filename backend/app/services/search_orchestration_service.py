"""
Architect AI — Central Search Orchestration Service
Orchestrates multi-source architectural discovery across:
- Pinterest (SocialCrawl)
- Instagram Reels (SocialCrawl)
- YouTube (SocialCrawl)
- Reddit (SocialCrawl)
- X / Twitter AI (SocialCrawl)
- Google Shopping (SocialCrawl)
- Google Business (SocialCrawl)

Features:
- Category-aware query generation for real projects, architects, builders, showrooms & fabrication.
- Cursor-based multi-page collection targeting 50-100 items per source.
- Granular per-source metrics tracking (collected, unique, status, has_more, cursor).
- Safe error isolation per source.
- Multi-source round-robin interleaving.
- Deduplication against URL and external identifier hashes.
"""

import logging
import re
import time
import uuid
import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple, Union

from app.schemas.discovery import (
    SourceStatusEnum,
    DiscoveryOverallStatusEnum,
    DiscoveryTabEnum,
    ContentTypeEnum,
    DiscoveryClassificationEnum,
    MetadataClassificationEnum,
    SourceStatusReport,
    SourceExecutionMetrics,
    NormalizedDiscoveryResult,
    DiscoveryPagination,
    UnifiedDiscoveryResponse,
    determine_relevant_discovery_tabs,
    ProvenanceEnum,
    InspirationRelevanceTierEnum,
    MediaStatusEnum,
)
from app.services.discovery_guard import (
    discovery_request_guard,
    provider_budget_manager,
    GuardDecision,
)
from app.services.keyword_library import (
    search_keyword_library,
    expand_search_query_with_synonyms,
)
from app.services.discovery_adapters import (
    BaseSourceAdapter,
    PinterestAdapter,
    InstagramAdapter,
    YouTubeAdapter,
    RedditAdapter,
    GoogleSearchAdapter,
    GoogleShoppingAdapter,
    GooglePlacesAdapter,
)
from app.services.socialcrawl_service import (
    search_instagram_reels,
    search_youtube,
    search_reddit,
    search_twitter_ai,
    search_google_businesses,
    search_google_shopping,
    is_socialcrawl_configured,
)
from app.services.pinterest_service import search_pinterest

logger = logging.getLogger("architect_ai.search_orchestration")

# Category-aware query intelligence templates
# Maps topic/concept keywords to high-yield search variations across real projects, showrooms, and fabrication
CATEGORY_QUERY_MAPPINGS: Dict[str, Dict[str, List[str]]] = {
    "staircase": {
        "instagram": [
            "modern cantilever staircase design",
            "spiral staircase architectural fabrication",
            "glass and steel staircase railing design",
            "floating wooden staircase interior",
            "curved luxury staircase architecture"
        ],
        "youtube": [
            "modern staircase architectural design walkthrough",
            "cantilever floating staircase construction details",
            "luxury duplex staircase design ideas"
        ],
        "reddit": [
            "cantilever staircase structural design cost",
            "best staircase railing materials modern house"
        ],
        "shopping": [
            "staircase railing stainless steel glass fittings",
            "wooden staircase treads steps anti slip"
        ],
        "x": [
            "staircase architecture design modern villa",
            "minimalist staircase architectural interior"
        ]
    },
    "chandelier": {
        "instagram": [
            "luxury crystal chandelier living room design",
            "modern architectural chandelier showroom",
            "double height living room chandelier walkthrough",
            "imported crystal pendant chandelier lighting"
        ],
        "youtube": [
            "luxury chandelier showroom tour modern lighting",
            "double height living room chandelier installation"
        ],
        "reddit": [
            "best chandelier brands modern house",
            "crystal chandelier vs modern ring pendant lighting"
        ],
        "shopping": [
            "crystal chandelier modern double height ceiling",
            "contemporary led ring pendant chandelier"
        ],
        "x": [
            "luxury chandelier architectural lighting design"
        ]
    },
    "landscaping": {
        "instagram": [
            "tropical courtyard landscaping natural stone",
            "villa garden waterfall and reflection pond design",
            "architectural hardscaping pebble pathway design",
            "modern courtyard landscaping walkthrough"
        ],
        "youtube": [
            "tropical villa landscape design walkthrough",
            "courtyard garden and koi pond architectural tour"
        ],
        "reddit": [
            "natural stone vs pavers courtyard landscaping",
            "maintenance tropical garden reflection pond"
        ],
        "shopping": [
            "natural river pebbles landscaping garden stone",
            "outdoor garden waterfall fountain pump"
        ],
        "x": [
            "architectural landscape design contemporary villa"
        ]
    },
    "kitchen": {
        "instagram": [
            "luxury modular kitchen interior walkthrough",
            "acrylic finish quartz countertop modern kitchen",
            "hafele blum hardware kitchen design",
            "island modular kitchen design contemporary"
        ],
        "youtube": [
            "modern modular kitchen walkthrough luxury house",
            "modular kitchen materials acrylic vs pu lacquer"
        ],
        "reddit": [
            "quartz vs granite kitchen countertops cost",
            "best modular kitchen hardware hafele hettich blum"
        ],
        "shopping": [
            "hafele kitchen soft close tandem box fittings",
            "granite quartz kitchen sink double bowl"
        ],
        "x": [
            "modern modular kitchen interior design architecture"
        ]
    },
    "house": {
        "instagram": [
            "modern villa architecture design walkthrough",
            "contemporary house turnkey handover tour",
            "minimalist tropical villa architecture",
            "luxury house elevation and interior design"
        ],
        "youtube": [
            "complete modern house architectural walkthrough",
            "kerala contemporary courtyard house tour",
            "luxury modern villa full house project tour"
        ],
        "reddit": [
            "building contemporary house cost breakdown",
            "architect vs turnkey builder experience"
        ],
        "shopping": [
            "architectural elevation louvers wall cladding",
            "smart door lock wifi biometric main door"
        ],
        "x": [
            "contemporary residential architecture villa design"
        ]
    },
    "pipe": {
        "instagram": [
            "concealed plumbing pipe installation house",
            "cpvc pipe fittings architectural plumbing"
        ],
        "youtube": [
            "concealed plumbing pipeline installation house construction",
            "astral vs supreme cpvc pipe comparison test"
        ],
        "reddit": [
            "cpvc vs upvc pipes plumbing house construction",
            "best plumbing pipe brand astral supreme"
        ],
        "shopping": [
            "astral cpvc pipe 1 inch sdr 11",
            "supreme cpvc pipe fittings brass elbow tee"
        ],
        "x": [
            "plumbing engineering architectural building materials"
        ]
    },
    "tile": {
        "instagram": [
            "italian marble flooring luxury living room",
            "athangudi handcrafted cement tiles flooring",
            "large format vitrified tiles flooring design",
            "terrazzo floor tiles architectural interior"
        ],
        "youtube": [
            "italian marble vs vitrified tiles flooring walkthrough",
            "athangudi handmade cement tile manufacturing and laying"
        ],
        "reddit": [
            "italian marble vs large format vitrified tiles",
            "athangudi tiles durability maintenance"
        ],
        "shopping": [
            "vitrified tiles 4x2 feet glazed porcelain flooring",
            "athangudi cement handcrafted floor tile"
        ],
        "x": [
            "architectural flooring marble tile design"
        ]
    },
    "elevation": {
        "instagram": [
            "modern house front elevation design walkthrough",
            "contemporary exterior facade architecture",
            "side elevation design modern villa",
            "exterior louvers and stone cladding facade"
        ],
        "youtube": [
            "modern house elevation designs 3d walkthrough",
            "contemporary villa exterior facade architecture tour"
        ],
        "reddit": [
            "exterior wall cladding materials weather proof",
            "cost of facade louvers modern house"
        ],
        "shopping": [
            "wpc exterior wall cladding louvers",
            "natural stone veneer cladding panels exterior"
        ],
        "x": [
            "modern house elevation exterior architecture design"
        ]
    }
}


class SearchOrchestrationService:
    """
    Coordinates multi-source search across Pinterest, Instagram Reels,
    YouTube, Reddit, X, Google Shopping and Google Business.
    """

    def __init__(self):
        self.adapters: Dict[str, BaseSourceAdapter] = {
            "pinterest": PinterestAdapter(),
            "instagram": InstagramAdapter(),
            "youtube": YouTubeAdapter(),
            "reddit": RedditAdapter(),
            "google_search": GoogleSearchAdapter(),
            "google_shopping": GoogleShoppingAdapter(),
            "google_places": GooglePlacesAdapter(),
        }
        self.source_alias_map: Dict[str, str] = {
            "pinterest": "pinterest",
            "pin": "pinterest",
            "instagram": "instagram",
            "reels": "instagram",
            "insta": "instagram",
            "youtube": "youtube",
            "yt": "youtube",
            "reddit": "reddit",
            "google_search": "google_search",
            "web": "google_search",
            "google_shopping": "google_shopping",
            "shopping": "google_shopping",
            "google_places": "google_places",
            "google_business": "google_places",
            "places": "google_places",
            "suppliers": "google_places",
        }

    def generate_category_aware_queries(
        self,
        query: str,
        platform: str = "instagram"
    ) -> List[str]:
        """
        Generates targeted search queries based on query intent and platform.
        """
        clean_q = query.strip().lower()
        if not clean_q:
            return ["modern architecture design"]

        # Preserve specific user query: only use general topic mappings when query is identical to generic topic
        if clean_q in CATEGORY_QUERY_MAPPINGS:
            platform_dict = CATEGORY_QUERY_MAPPINGS[clean_q]
            queries = platform_dict.get(platform) or platform_dict.get("instagram", [])
            if queries:
                return queries

        # Default intelligent variations for general architectural terms
        if platform == "pinterest":
            return [
                f"{clean_q} architecture",
                f"{clean_q} wall design",
                f"{clean_q} construction inspiration",
                f"{clean_q} house projects",
            ]
        elif platform == "instagram":
            return [
                f"{clean_q} architecture design",
                f"{clean_q} construction projects",
                f"{clean_q} design walkthrough",
                f"{clean_q} architectural reel",
            ]
        elif platform == "youtube":
            return [
                f"{clean_q} construction",
                f"{clean_q} installation",
                f"{clean_q} manufacturing",
                f"{clean_q} comparison",
                f"{clean_q} building projects",
            ]
        elif platform == "reddit":
            return [
                f"{clean_q} comparisons and construction discussions",
                f"{clean_q} cost durability experience",
                f"{clean_q} architecture materials review",
            ]
        elif platform in ("shopping", "google_shopping"):
            exclusions = "-wallpaper -sticker -toy -lego -puzzle -3d-panel -poster -shirt"
            return [
                f"{clean_q} building materials {exclusions}".strip(),
                f"{clean_q} products {exclusions}".strip(),
                f"{clean_q} for construction {exclusions}".strip(),
                f"{clean_q} manufacturers {exclusions}".strip(),
            ]
        elif platform in ("places", "google_places"):
            return [
                f"{clean_q} suppliers",
                f"{clean_q} dealers and manufacturers",
                f"{clean_q} distributors and dealers",
            ]
        elif platform in ("x", "twitter"):
            return [
                f"{clean_q} architecture contemporary design"
            ]

        return [clean_q]

    def search_source_with_pagination(
        self,
        source: str,
        query: str,
        target_count: int = 50,
        max_cap: int = 100,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Fetches up to target_count (max max_cap) items for a single source
        using cursor-based pagination and category-aware queries.
        """
        effective_limit = min(max(target_count, 10), max_cap)
        collected_items: List[Dict[str, Any]] = []
        seen_keys: Set[str] = set()
        has_more = True
        cursor: Optional[str] = None
        error_msg: Optional[str] = None
        status = "ok"

        queries = self.generate_category_aware_queries(query, platform=source)
        primary_query = queries[0] if queries else query

        try:
            if source == "pinterest":
                items = search_pinterest(
                    query=primary_query,
                    max_pages=min(5, (effective_limit // 10) + 1),
                    dry_run=dry_run
                )
                if isinstance(items, list):
                    for item in items:
                        key = item.get("source_url") or item.get("id")
                        if key and key not in seen_keys:
                            seen_keys.add(key)
                            collected_items.append(item)
                    has_more = len(items) >= 10
                elif isinstance(items, dict):
                    for item in items.get("items", []):
                        key = item.get("source_url") or item.get("id")
                        if key and key not in seen_keys:
                            seen_keys.add(key)
                            collected_items.append(item)
                    has_more = items.get("has_more", False)
                    cursor = items.get("next_cursor")

            elif source == "instagram":
                # Multi-page or multi-query collection for Instagram
                for q_var in queries[:2]:
                    if len(collected_items) >= effective_limit:
                        break
                    res = search_instagram_reels(
                        query=q_var,
                        cursor=cursor,
                        max_pages=min(4, (effective_limit // 12) + 1),
                        dry_run=dry_run
                    )
                    items = res.get("items", [])
                    for item in items:
                        key = item.get("source_url") or item.get("reel_id") or item.get("id")
                        if key and key not in seen_keys:
                            seen_keys.add(key)
                            collected_items.append(item)
                    if len(collected_items) >= effective_limit:
                        break

                has_more = len(collected_items) >= 20

            elif source == "youtube":
                res = search_youtube(
                    query=primary_query,
                    cursor=cursor,
                    max_pages=min(4, (effective_limit // 12) + 1),
                    dry_run=dry_run
                )
                items = res.get("items", [])
                for item in items:
                    key = item.get("video_embed_id") or item.get("source_url") or item.get("id")
                    if key and key not in seen_keys:
                        seen_keys.add(key)
                        collected_items.append(item)
                has_more = res.get("has_more", False)

            elif source == "reddit":
                res = search_reddit(
                    query=primary_query,
                    cursor=cursor,
                    max_pages=min(4, (effective_limit // 10) + 1),
                    dry_run=dry_run
                )
                items = res.get("items", [])
                for item in items:
                    key = item.get("source_url") or item.get("post_id") or item.get("id")
                    if key and key not in seen_keys:
                        seen_keys.add(key)
                        collected_items.append(item)
                has_more = res.get("has_more", False)

            elif source in ("x", "twitter"):
                res = search_twitter_ai(
                    query=primary_query,
                    cursor=cursor,
                    dry_run=dry_run
                )
                items = res.get("items", [])
                for item in items:
                    key = item.get("source_url") or item.get("post_id") or item.get("id")
                    if key and key not in seen_keys:
                        seen_keys.add(key)
                        collected_items.append(item)
                has_more = res.get("has_more", False)

            elif source in ("shopping", "google_shopping"):
                res = search_google_shopping(
                    query=primary_query,
                    dry_run=dry_run
                )
                items = res.get("items", [])
                for item in items:
                    key = item.get("product_url") or item.get("product_id") or item.get("id")
                    if key and key not in seen_keys:
                        seen_keys.add(key)
                        collected_items.append(item)
                has_more = len(items) >= 10

            elif source in ("google_business", "suppliers"):
                res = search_google_businesses(
                    query=primary_query,
                    dry_run=dry_run
                )
                items = res.get("items", [])
                for item in items:
                    key = item.get("place_id") or item.get("maps_url") or item.get("id")
                    if key and key not in seen_keys:
                        seen_keys.add(key)
                        collected_items.append(item)
                has_more = len(items) >= 10

        except Exception as exc:
            logger.error(f"Error fetching from source {source}: {exc}")
            status = "error"
            error_msg = str(exc)

        return {
            "source_name": source,
            "query_used": primary_query,
            "target_requested": target_count,
            "collected": len(collected_items),
            "unique": len(seen_keys),
            "status": status if not dry_run else "dry_run",
            "has_more": has_more,
            "cursor": cursor,
            "error": error_msg,
            "items": collected_items[:effective_limit]
        }

    def orchestrate_unified_search(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        target_per_source: int = 50,
        max_cap: int = 100,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Orchestrates multi-source collection, computes source tracking metrics,
        and round-robin interleaves the combined discovery feed.
        """
        requested_sources = sources or [
            "pinterest", "instagram", "youtube", "reddit", "x", "shopping", "google_business"
        ]

        source_metrics: List[Dict[str, Any]] = []
        source_item_buckets: Dict[str, List[Dict[str, Any]]] = {}

        for src in requested_sources:
            norm_src = src.lower().strip()
            res = self.search_source_with_pagination(
                source=norm_src,
                query=query,
                target_count=target_per_source,
                max_cap=max_cap,
                dry_run=dry_run
            )
            source_metrics.append({
                "source_name": norm_src,
                "collected": res["collected"],
                "unique": res["unique"],
                "status": res["status"],
                "has_more": res["has_more"],
                "error": res["error"]
            })
            source_item_buckets[norm_src] = res["items"]

        # Round-robin interleaving
        interleaved_results: List[Dict[str, Any]] = []
        max_bucket_len = max((len(b) for b in source_item_buckets.values()), default=0)

        for i in range(max_bucket_len):
            for src in requested_sources:
                norm_src = src.lower().strip()
                bucket = source_item_buckets.get(norm_src, [])
                if i < len(bucket):
                    interleaved_results.append(bucket[i])

        return {
            "query": query,
            "total_unified_items": len(interleaved_results),
            "source_metrics": source_metrics,
            "dry_run": dry_run,
            "items": interleaved_results
        }

    def resolve_taxonomy_context(self, query: str) -> Dict[str, Any]:
        """
        Leverages keyword_library to extract taxonomy categories, items, variants,
        supplier categories, and synonyms for the query.
        """
        clean_q = query.strip()
        synonyms = expand_search_query_with_synonyms(clean_q)
        matches = search_keyword_library(clean_q, max_results=5)

        context: Dict[str, Any] = {
            "query": clean_q,
            "synonyms": synonyms,
        }

        if matches:
            top_cat = matches[0]
            context["category_id"] = top_cat.get("category_id")
            context["category"] = top_cat.get("category_name")
            context["supplier_category"] = top_cat.get("supplier_category")

            sub_matches = top_cat.get("matches", [])
            if sub_matches:
                top_sub = sub_matches[0]
                context["subcategory"] = top_sub.get("subcategory")
                items = top_sub.get("items", [])
                if items:
                    context["item"] = items[0].get("name")
                    context["variants"] = items[0].get("variants", [])[:5]
        return context

    def deduplicate_results(
        self,
        results: List[NormalizedDiscoveryResult]
    ) -> Tuple[List[NormalizedDiscoveryResult], int]:
        """
        Deduplicates across sources:
        - URL normalization (stripping tracking query params and hashes).
        - Source Result ID tracking within the same source.
        - Composite image + title token hashing.
        - Preserves distinct products sharing catalog imagery (different product titles/specs).
        """
        seen_urls: Set[str] = set()
        seen_source_ids: Set[str] = set()
        seen_image_subjects: Dict[str, List[Set[str]]] = {}
        deduped: List[NormalizedDiscoveryResult] = []
        duplicate_count = 0

        for item in results:
            is_dup = False

            # 1. Check source-specific ID
            if item.source and item.source_result_id:
                src_key = f"{item.source}::{item.source_result_id}"
                if src_key in seen_source_ids:
                    is_dup = True
                else:
                    seen_source_ids.add(src_key)

            # 2. Check canonical URL & Media Identifiers
            url_to_check = item.canonical_url or item.original_url
            if url_to_check and not is_dup:
                # Specific YouTube video ID normalization to prevent false duplicates across watch/shorts/youtu.be
                yt_match = re.search(r"(?:v=|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})", url_to_check)
                if yt_match:
                    norm_url = f"https://www.youtube.com/watch?v={yt_match.group(1)}"
                else:
                    norm_url = re.sub(r"[?#].*$", "", url_to_check).rstrip("/").lower()

                if norm_url:
                    if norm_url in seen_urls:
                        is_dup = True
                    else:
                        seen_urls.add(norm_url)

            # 3. Composite image + title similarity check
            if not is_dup and item.image_url:
                img_norm = item.image_url.strip().split("?")[0].lower()
                title_tokens = set(re.findall(r"\w+", (item.title or "").lower()))
                meaningful_tokens = {t for t in title_tokens if len(t) > 2 and t not in {"the", "and", "for", "with"}}

                if img_norm in seen_image_subjects:
                    for existing_token_set in seen_image_subjects[img_norm]:
                        if meaningful_tokens and existing_token_set:
                            intersection = len(meaningful_tokens & existing_token_set)
                            union = len(meaningful_tokens | existing_token_set)
                            sim = intersection / union if union > 0 else 0
                            if sim > 0.80:
                                is_dup = True
                                break
                    if not is_dup:
                        seen_image_subjects[img_norm].append(meaningful_tokens)
                else:
                    seen_image_subjects[img_norm] = [meaningful_tokens]

            if is_dup:
                duplicate_count += 1
            else:
                deduped.append(item)

        return deduped, duplicate_count

    def calculate_relevance_and_confidence(
        self,
        item: NormalizedDiscoveryResult,
        query: str,
        taxonomy_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Computes normalized relevance [0.0, 1.0] and confidence [0.0, 1.0] scores.
        Sets provenance, media_status, and classifies inspiration_relevance_tier.
        """
        # Determine provenance
        if not item.provenance:
            item.provenance = ProvenanceEnum.LIVE_DISCOVERY

        # Determine media status
        if not item.media_status:
            if item.source == "reddit" and not (item.image_url or item.video_url):
                item.media_status = MediaStatusEnum.TEXT_DISCUSSION
            elif item.image_url or item.video_url:
                item.media_status = MediaStatusEnum.MEDIA_READY
            else:
                item.media_status = MediaStatusEnum.MEDIA_UNUSABLE

        # Classify inspiration relevance tier via relevance_matcher
        from app.services.relevance_service import relevance_matcher
        tags_list = getattr(item, 'matched_keywords', []) or getattr(item, 'material_tags', [])
        tags_str = " ".join(tags_list) if isinstance(tags_list, list) else str(tags_list or "")
        tier, reason = relevance_matcher.classify(
            query=query,
            title=item.title or "",
            description=item.description or "",
            tags=tags_str,
            category=taxonomy_context.get("category", "") if taxonomy_context else "",
            subcategory=taxonomy_context.get("subcategory", "") if taxonomy_context else ""
        )
        item.inspiration_relevance_tier = tier

        if tier == InspirationRelevanceTierEnum.TIER_5_REJECTED:
            item.relevance_score = 0.0
            item.confidence_score = 0.0
            return

        clean_q = query.strip().lower()
        q_tokens = [t for t in clean_q.split() if len(t) > 1]

        title_lower = (item.title or "").lower()
        desc_lower = (item.description or "").lower()

        score = 0.65

        # Title token matching
        if q_tokens:
            matched_tokens = sum(1 for t in q_tokens if t in title_lower)
            score += (matched_tokens / len(q_tokens)) * 0.25

        # Description / query containment
        if clean_q in desc_lower:
            score += 0.05
        elif any(t in desc_lower for t in q_tokens):
            score += 0.03

        # Rich media bonus
        if item.image_url or item.video_url:
            score += 0.05

        item.relevance_score = min(max(round(score, 3), 0.0), 1.0)

        # Confidence score based on source & verification
        conf = 0.75
        if item.verification_status == "VERIFIED":
            conf = 0.95
        elif item.verification_status == "POTENTIAL_GOOGLE_PLACE":
            conf = 0.85
        elif item.source == "google_shopping" and item.price is not None:
            conf = 0.90
        elif item.source in ("youtube", "pinterest", "instagram") and item.creator_name:
            conf = 0.85

        item.confidence_score = min(max(round(conf, 3), 0.0), 1.0)

    def _build_rate_limited_response(
        self,
        clean_q: str,
        norm_q: str,
        active_tab: DiscoveryTabEnum,
        resolved_tax: Dict[str, Any],
        req_id: str,
        decision: GuardDecision,
        page: int,
        page_size: int,
    ) -> UnifiedDiscoveryResponse:
        return UnifiedDiscoveryResponse(
            query=clean_q,
            normalized_query=norm_q,
            selected_taxonomy_context=resolved_tax,
            active_discovery_tab=active_tab,
            overall_status=DiscoveryOverallStatusEnum.RATE_LIMITED,
            total_results=0,
            unique_results=0,
            results=[],
            source_metrics={},
            source_statuses={},
            pagination=DiscoveryPagination(
                page=page,
                page_size=page_size,
                total_results=0,
                unique_results=0,
                total_pages=1,
                has_more=False,
                per_source_cursors={},
            ),
            warnings=[decision.reason or "Interactive rate limit exceeded."],
            errors=[{
                "guard": "rate_limit",
                "status_code": decision.status_code,
                "reason": decision.reason,
                "retry_after_seconds": decision.retry_after_seconds,
            }],
            request_id=req_id,
        )

    def _build_budget_exceeded_response(
        self,
        clean_q: str,
        norm_q: str,
        active_tab: DiscoveryTabEnum,
        resolved_tax: Dict[str, Any],
        req_id: str,
        reason: str,
        page: int,
        page_size: int,
        projected_credits: int = 0,
    ) -> UnifiedDiscoveryResponse:
        return UnifiedDiscoveryResponse(
            query=clean_q,
            normalized_query=norm_q,
            selected_taxonomy_context=resolved_tax,
            active_discovery_tab=active_tab,
            overall_status=DiscoveryOverallStatusEnum.FAILED,
            total_results=0,
            unique_results=0,
            results=[],
            source_metrics={},
            source_statuses={},
            pagination=DiscoveryPagination(
                page=page,
                page_size=page_size,
                total_results=0,
                unique_results=0,
                total_pages=1,
                has_more=False,
                per_source_cursors={},
            ),
            warnings=[reason],
            errors=[{
                "guard": "budget_exceeded",
                "reason": reason,
                "projected_credits": projected_credits,
            }],
            request_id=req_id,
        )

    def _assemble_discovery_response(
        self,
        clean_q: str,
        norm_q: str,
        active_tab: DiscoveryTabEnum,
        resolved_tax: Dict[str, Any],
        active_sources: List[str],
        source_statuses: Dict[str, SourceStatusReport],
        source_metrics: Dict[str, SourceExecutionMetrics],
        source_buckets: Dict[str, List[NormalizedDiscoveryResult]],
        pooled_results: List[NormalizedDiscoveryResult],
        warnings: List[str],
        errors: List[Dict[str, Any]],
        page: int,
        page_size: int,
        req_id: str,
    ) -> UnifiedDiscoveryResponse:
        # Deduplicate pooled items
        deduped_results, total_dups = self.deduplicate_results(pooled_results)

        # Update per-source unique and duplicate counts
        deduped_ids = {id(it) for it in deduped_results}
        for src, items in source_buckets.items():
            if src in source_metrics:
                survived = sum(1 for it in items if id(it) in deduped_ids)
                dups_in_src = len(items) - survived
                source_metrics[src].unique_result_count = survived
                source_metrics[src].duplicate_count = dups_in_src
            if src in source_statuses:
                survived = sum(1 for it in items if id(it) in deduped_ids)
                source_statuses[src].unique_result_count = survived

        # Calculate relevance and confidence
        for it in deduped_results:
            self.calculate_relevance_and_confidence(it, clean_q, resolved_tax)

        # Prevent YouTube from dominating combined multi-source results when other sources are available
        multi_source_non_yt = len(active_sources) > 1

        # Tab routing & filtering
        if active_tab == DiscoveryTabEnum.ALL:
            non_yt_total = sum(
                1 for src, b in source_buckets.items()
                if src != "youtube"
                for candidate in b
                if id(candidate) in deduped_ids
            )
            max_youtube_all = max(2, non_yt_total // 2) if (multi_source_non_yt and non_yt_total > 0) else None
            yt_added = 0

            # Round-robin interleaving across source buckets for diversity
            interleaved: List[NormalizedDiscoveryResult] = []
            max_bucket_len = max((len(b) for b in source_buckets.values()), default=0)
            seen_in_interleave: Set[int] = set()

            for i in range(max_bucket_len):
                for src in active_sources:
                    c_src = self.source_alias_map.get(src.lower().strip(), src.lower().strip())
                    if c_src == "youtube" and max_youtube_all is not None and yt_added >= max_youtube_all:
                        continue
                    bucket = source_buckets.get(c_src, [])
                    if i < len(bucket):
                        candidate = bucket[i]
                        if id(candidate) in deduped_ids and id(candidate) not in seen_in_interleave:
                            seen_in_interleave.add(id(candidate))
                            interleaved.append(candidate)
                            if c_src == "youtube":
                                yt_added += 1
            tab_results = interleaved
        else:
            # Filter by matching tab
            target_tab_val = active_tab.value
            matched_tab_items = [it for it in deduped_results if target_tab_val in it.relevant_tabs]
            # Sort by relevance score descending
            matched_tab_items.sort(key=lambda x: (x.relevance_score or 0.0), reverse=True)
            non_yt_tab = [it for it in matched_tab_items if it.source != "youtube"]
            if multi_source_non_yt and non_yt_tab:
                max_youtube_tab = max(2, len(non_yt_tab) // 2)
                yt_count = 0
                balanced_tab: List[NormalizedDiscoveryResult] = []
                for it in matched_tab_items:
                    if it.source == "youtube":
                        if yt_count >= max_youtube_tab:
                            continue
                        yt_count += 1
                    balanced_tab.append(it)
                tab_results = balanced_tab
            else:
                tab_results = matched_tab_items

        # Pagination
        total_count = len(tab_results)
        unique_count = len(tab_results)
        offset = (page - 1) * page_size
        paged_results = tab_results[offset : offset + page_size]

        has_more = (offset + page_size < total_count) or any(
            s.has_more for s in source_statuses.values() if s.status == SourceStatusEnum.SUCCESS
        )

        pagination = DiscoveryPagination(
            page=page,
            page_size=page_size,
            total_results=total_count,
            unique_results=unique_count,
            total_pages=(total_count + page_size - 1) // page_size if total_count > 0 else 1,
            has_more=has_more,
            per_source_cursors={
                s_name: s_stat.next_page_token for s_name, s_stat in source_statuses.items()
            }
        )

        # Overall execution status
        statuses = [s.status for s in source_statuses.values() if s.requested]
        successes = [s for s in statuses if s == SourceStatusEnum.SUCCESS]
        failures = [s for s in statuses if s == SourceStatusEnum.FAILED]
        rate_limits = [s for s in statuses if s == SourceStatusEnum.RATE_LIMITED]

        if not statuses or all(s == SourceStatusEnum.FAILED for s in statuses):
            overall_status = DiscoveryOverallStatusEnum.FAILED
        elif rate_limits and not successes:
            overall_status = DiscoveryOverallStatusEnum.RATE_LIMITED
        elif total_count == 0 and all(s in (SourceStatusEnum.EMPTY, SourceStatusEnum.NOT_CONFIGURED, SourceStatusEnum.DISABLED) for s in statuses):
            overall_status = DiscoveryOverallStatusEnum.EMPTY
        elif successes and (failures or rate_limits or any(s == SourceStatusEnum.NOT_CONFIGURED for s in statuses)):
            overall_status = DiscoveryOverallStatusEnum.PARTIAL_SUCCESS
        elif successes:
            overall_status = DiscoveryOverallStatusEnum.SUCCESS
        elif any(s == SourceStatusEnum.EMPTY for s in statuses):
            overall_status = DiscoveryOverallStatusEnum.EMPTY
        else:
            overall_status = DiscoveryOverallStatusEnum.PARTIAL_SUCCESS

        return UnifiedDiscoveryResponse(
            query=clean_q,
            normalized_query=norm_q,
            selected_taxonomy_context=resolved_tax,
            active_discovery_tab=active_tab,
            overall_status=overall_status,
            total_results=total_count,
            unique_results=unique_count,
            results=paged_results,
            source_metrics=source_metrics,
            source_statuses=source_statuses,
            pagination=pagination,
            warnings=warnings,
            errors=errors,
            request_id=req_id
        )

    def orchestrate_discovery(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        tab: Union[DiscoveryTabEnum, str] = DiscoveryTabEnum.ALL,
        page: int = 1,
        page_size: int = 30,
        target_per_source: int = 15,
        dry_run: bool = False,
        taxonomy_context: Optional[Dict[str, Any]] = None,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        is_authenticated: bool = False,
        enforce_guard: bool = False,
        query_expansions: int = 1,
    ) -> UnifiedDiscoveryResponse:
        """
        Master Multi-Source Architectural Discovery Orchestrator (Synchronous).
        Executes configured adapters sequentially, isolates per-source errors, normalizes
        into 3-dimensional classification schemas, removes duplicates,
        applies tab routing, and compiles granular execution metrics.
        """
        req_id = request_id or f"disc_{uuid.uuid4().hex[:12]}"
        clean_q = query.strip()
        norm_q = clean_q.lower()

        # Parse tab
        if isinstance(tab, str):
            try:
                active_tab = DiscoveryTabEnum(tab.lower())
            except ValueError:
                active_tab = DiscoveryTabEnum.ALL
        else:
            active_tab = tab or DiscoveryTabEnum.ALL

        # Taxonomy resolution
        resolved_tax = taxonomy_context or self.resolve_taxonomy_context(clean_q)
        if city:
            resolved_tax["city"] = city
        if lat is not None:
            resolved_tax["lat"] = lat
        if lon is not None:
            resolved_tax["lon"] = lon

        # Requested sources
        active_sources = sources or [
            "pinterest",
            "instagram",
            "youtube",
            "reddit",
            "google_search",
            "google_shopping",
            "google_places"
        ]

        # Request Safety & Budget Enforcement (Pre-execution)
        projected_credits = 0
        if enforce_guard:
            guard_dec = discovery_request_guard.check_request(
                user_id=user_id,
                client_ip=client_ip,
                is_authenticated=is_authenticated,
            )
            if not guard_dec.allowed:
                return self._build_rate_limited_response(
                    clean_q, norm_q, active_tab, resolved_tax, req_id, guard_dec, page, page_size
                )

            budget_sources = [
                self.source_alias_map.get(raw_src.lower().strip(), raw_src.lower().strip())
                for raw_src in active_sources
            ]
            executable_budget_sources = [
                c_src for c_src in budget_sources
                if c_src not in ("x", "twitter") and c_src in self.adapters
            ]
            if len(budget_sources) > provider_budget_manager.max_sources_per_request:
                budget_ok, budget_reason, projected_credits = provider_budget_manager.check_budget(
                    budget_sources,
                    page=page,
                    query_expansions=query_expansions,
                    dry_run=dry_run,
                    reserve=False,
                )
            else:
                budget_ok, budget_reason, projected_credits = provider_budget_manager.check_budget(
                    executable_budget_sources,
                    page=page,
                    query_expansions=query_expansions,
                    dry_run=dry_run,
                    reserve=(not dry_run),
                )
            if not budget_ok:
                return self._build_budget_exceeded_response(
                    clean_q, norm_q, active_tab, resolved_tax, req_id, budget_reason or "Budget cap exceeded", page, page_size, projected_credits
                )

        source_statuses: Dict[str, SourceStatusReport] = {}
        source_metrics: Dict[str, SourceExecutionMetrics] = {}
        source_buckets: Dict[str, List[NormalizedDiscoveryResult]] = {}
        pooled_results: List[NormalizedDiscoveryResult] = []
        warnings: List[str] = []
        errors: List[Dict[str, Any]] = []

        # Execute requested sources
        for raw_src in active_sources:
            src_norm = raw_src.lower().strip()
            canon_src = self.source_alias_map.get(src_norm, src_norm)

            # Check if source is explicitly disabled (e.g. x / twitter)
            if canon_src in ("x", "twitter"):
                source_statuses[canon_src] = SourceStatusReport(
                    source_name=canon_src,
                    status=SourceStatusEnum.DISABLED,
                    requested=True,
                    error_code="SOURCE_DISABLED",
                    error_message="X/Twitter integration is disabled for Phase 5B.",
                    duration_ms=0.0
                )
                source_metrics[canon_src] = SourceExecutionMetrics(
                    source_name=canon_src,
                    requested_result_count=target_per_source,
                    status=SourceStatusEnum.DISABLED,
                    error_code="SOURCE_DISABLED",
                    error_message="X/Twitter integration is disabled.",
                    duration_ms=0.0
                )
                continue

            adapter = self.adapters.get(canon_src)
            if not adapter:
                source_statuses[canon_src] = SourceStatusReport(
                    source_name=canon_src,
                    status=SourceStatusEnum.NOT_CONFIGURED,
                    requested=True,
                    error_code="UNKNOWN_SOURCE_ADAPTER",
                    error_message=f"No adapter registered for '{raw_src}'.",
                    duration_ms=0.0
                )
                source_metrics[canon_src] = SourceExecutionMetrics(
                    source_name=canon_src,
                    requested_result_count=target_per_source,
                    status=SourceStatusEnum.NOT_CONFIGURED,
                    error_code="UNKNOWN_SOURCE_ADAPTER",
                    error_message=f"No adapter registered for '{raw_src}'.",
                    duration_ms=0.0
                )
                continue

            t0 = time.time()
            try:
                items, status_rep, mets = adapter.fetch(
                    query=clean_q,
                    limit=target_per_source,
                    dry_run=dry_run,
                    taxonomy_context=resolved_tax
                )
            except Exception as exc:
                dur_ms = (time.time() - t0) * 1000
                logger.error(f"Unhandled adapter exception in '{canon_src}': {exc}", exc_info=True)
                status_rep = SourceStatusReport(
                    source_name=canon_src,
                    status=SourceStatusEnum.FAILED,
                    requested=True,
                    error_code="ADAPTER_UNHANDLED_EXCEPTION",
                    error_message=str(exc),
                    duration_ms=dur_ms
                )
                mets = SourceExecutionMetrics(
                    source_name=canon_src,
                    requested_result_count=target_per_source,
                    status=SourceStatusEnum.FAILED,
                    error_code="ADAPTER_UNHANDLED_EXCEPTION",
                    error_message=str(exc),
                    duration_ms=dur_ms
                )
                items = []

            source_statuses[canon_src] = status_rep
            source_metrics[canon_src] = mets
            source_buckets[canon_src] = items
            pooled_results.extend(items)

            # Collect errors and warnings
            if status_rep.status == SourceStatusEnum.NOT_CONFIGURED:
                warnings.append(f"Source '{canon_src}' is not configured: {status_rep.error_message or 'Missing credentials'}")
            elif status_rep.status in (SourceStatusEnum.FAILED, SourceStatusEnum.RATE_LIMITED, SourceStatusEnum.QUOTA_EXHAUSTED):
                errors.append({
                    "source": canon_src,
                    "status": status_rep.status.value,
                    "error_code": status_rep.error_code,
                    "error_message": status_rep.error_message
                })
                warnings.append(f"Source '{canon_src}' reported {status_rep.status.value}: {status_rep.error_message or ''}")

        return self._assemble_discovery_response(
            clean_q=clean_q,
            norm_q=norm_q,
            active_tab=active_tab,
            resolved_tax=resolved_tax,
            active_sources=active_sources,
            source_statuses=source_statuses,
            source_metrics=source_metrics,
            source_buckets=source_buckets,
            pooled_results=pooled_results,
            warnings=warnings,
            errors=errors,
            page=page,
            page_size=page_size,
            req_id=req_id,
        )

    async def orchestrate_discovery_async(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        tab: Union[DiscoveryTabEnum, str] = DiscoveryTabEnum.ALL,
        page: int = 1,
        page_size: int = 30,
        target_per_source: int = 15,
        dry_run: bool = False,
        taxonomy_context: Optional[Dict[str, Any]] = None,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        is_authenticated: bool = False,
        enforce_guard: bool = False,
        max_concurrency: int = 5,
        source_timeout: float = 10.0,
        query_expansions: int = 1,
    ) -> UnifiedDiscoveryResponse:
        """
        Master Multi-Source Architectural Discovery Orchestrator (Asynchronous).
        Concurrently executes configured adapters using asyncio.Semaphore to bound concurrency,
        directly awaits native async connectors, enforces strict per-source timeouts,
        isolates upstream failures, and normalizes discovery output.
        """
        req_id = request_id or f"disc_async_{uuid.uuid4().hex[:12]}"
        clean_q = query.strip()
        norm_q = clean_q.lower()

        # Parse tab
        if isinstance(tab, str):
            try:
                active_tab = DiscoveryTabEnum(tab.lower())
            except ValueError:
                active_tab = DiscoveryTabEnum.ALL
        else:
            active_tab = tab or DiscoveryTabEnum.ALL

        # Taxonomy resolution
        resolved_tax = taxonomy_context or self.resolve_taxonomy_context(clean_q)
        if city:
            resolved_tax["city"] = city
        if lat is not None:
            resolved_tax["lat"] = lat
        if lon is not None:
            resolved_tax["lon"] = lon

        # Requested sources
        active_sources = sources or [
            "pinterest",
            "instagram",
            "youtube",
            "reddit",
            "google_search",
            "google_shopping",
            "google_places"
        ]

        # Request Safety & Budget Enforcement (Pre-execution)
        projected_credits = 0
        if enforce_guard:
            guard_dec = discovery_request_guard.check_request(
                user_id=user_id,
                client_ip=client_ip,
                is_authenticated=is_authenticated,
            )
            if not guard_dec.allowed:
                return self._build_rate_limited_response(
                    clean_q, norm_q, active_tab, resolved_tax, req_id, guard_dec, page, page_size
                )

            budget_sources = [
                self.source_alias_map.get(raw_src.lower().strip(), raw_src.lower().strip())
                for raw_src in active_sources
            ]
            executable_budget_sources = [
                c_src for c_src in budget_sources
                if c_src not in ("x", "twitter") and c_src in self.adapters
            ]
            if len(budget_sources) > provider_budget_manager.max_sources_per_request:
                budget_ok, budget_reason, projected_credits = provider_budget_manager.check_budget(
                    budget_sources,
                    page=page,
                    query_expansions=query_expansions,
                    dry_run=dry_run,
                    reserve=False,
                )
            else:
                budget_ok, budget_reason, projected_credits = provider_budget_manager.check_budget(
                    executable_budget_sources,
                    page=page,
                    query_expansions=query_expansions,
                    dry_run=dry_run,
                    reserve=(not dry_run),
                )
            if not budget_ok:
                return self._build_budget_exceeded_response(
                    clean_q, norm_q, active_tab, resolved_tax, req_id, budget_reason or "Budget cap exceeded", page, page_size, projected_credits
                )

        source_statuses: Dict[str, SourceStatusReport] = {}
        source_metrics: Dict[str, SourceExecutionMetrics] = {}
        source_buckets: Dict[str, List[NormalizedDiscoveryResult]] = {}
        pooled_results: List[NormalizedDiscoveryResult] = []
        warnings: List[str] = []
        errors: List[Dict[str, Any]] = []

        semaphore = asyncio.Semaphore(max_concurrency)
        tasks_to_run = []
        started_adapter_calls = 0

        for raw_src in active_sources:
            src_norm = raw_src.lower().strip()
            canon_src = self.source_alias_map.get(src_norm, src_norm)

            if canon_src in ("x", "twitter"):
                source_statuses[canon_src] = SourceStatusReport(
                    source_name=canon_src,
                    status=SourceStatusEnum.DISABLED,
                    requested=True,
                    error_code="SOURCE_DISABLED",
                    error_message="X/Twitter integration is disabled for Phase 5B.",
                    duration_ms=0.0
                )
                source_metrics[canon_src] = SourceExecutionMetrics(
                    source_name=canon_src,
                    requested_result_count=target_per_source,
                    status=SourceStatusEnum.DISABLED,
                    error_code="SOURCE_DISABLED",
                    error_message="X/Twitter integration is disabled.",
                    duration_ms=0.0
                )
                continue

            adapter = self.adapters.get(canon_src)
            if not adapter:
                source_statuses[canon_src] = SourceStatusReport(
                    source_name=canon_src,
                    status=SourceStatusEnum.NOT_CONFIGURED,
                    requested=True,
                    error_code="UNKNOWN_SOURCE_ADAPTER",
                    error_message=f"No adapter registered for '{raw_src}'.",
                    duration_ms=0.0
                )
                source_metrics[canon_src] = SourceExecutionMetrics(
                    source_name=canon_src,
                    requested_result_count=target_per_source,
                    status=SourceStatusEnum.NOT_CONFIGURED,
                    error_code="UNKNOWN_SOURCE_ADAPTER",
                    error_message=f"No adapter registered for '{raw_src}'.",
                    duration_ms=0.0
                )
                continue

            async def _fetch_task(c_src: str, adp: BaseSourceAdapter):
                nonlocal started_adapter_calls
                async with semaphore:
                    started_adapter_calls += 1
                    t0 = time.time()
                    try:
                        items, status_rep, mets = await asyncio.wait_for(
                            adp.fetch_async(
                                query=clean_q,
                                limit=target_per_source,
                                dry_run=dry_run,
                                taxonomy_context=resolved_tax
                            ),
                            timeout=source_timeout
                        )
                        return c_src, items, status_rep, mets
                    except asyncio.TimeoutError:
                        dur_ms = (time.time() - t0) * 1000
                        logger.warning(f"Async source adapter '{c_src}' timed out after {source_timeout}s")
                        status_rep = SourceStatusReport(
                            source_name=c_src,
                            status=SourceStatusEnum.FAILED,
                            requested=True,
                            error_code="SOURCE_TIMEOUT",
                            error_class="timeout",
                            error_message=f"Source adapter timed out after {source_timeout}s.",
                            duration_ms=dur_ms
                        )
                        mets = SourceExecutionMetrics(
                            source_name=c_src,
                            requested_result_count=target_per_source,
                            status=SourceStatusEnum.FAILED,
                            error_code="SOURCE_TIMEOUT",
                            error_message=f"Source adapter timed out after {source_timeout}s.",
                            duration_ms=dur_ms
                        )
                        return c_src, [], status_rep, mets
                    except asyncio.CancelledError:
                        logger.warning(f"Async source adapter '{c_src}' was cancelled.")
                        raise
                    except Exception as exc:
                        dur_ms = (time.time() - t0) * 1000
                        logger.error(f"Unhandled async adapter exception in '{c_src}': {exc}", exc_info=True)
                        err_str = str(exc).lower()
                        if "credit" in err_str or "quota" in err_str or "budget" in err_str or "exhausted" in err_str:
                            e_class = "credits_exhausted"
                        elif "auth" in err_str or "unauthorized" in err_str or "forbidden" in err_str or "api_key" in err_str:
                            e_class = "auth_failure"
                        elif "rate" in err_str or "429" in err_str:
                            e_class = "rate_limit"
                        elif "disabled" in err_str:
                            e_class = "provider_disabled"
                        else:
                            e_class = "general_error"

                        status_rep = SourceStatusReport(
                            source_name=c_src,
                            status=SourceStatusEnum.FAILED,
                            requested=True,
                            error_code="ADAPTER_UNHANDLED_EXCEPTION",
                            error_class=e_class,
                            error_message=str(exc),
                            duration_ms=dur_ms
                        )
                        mets = SourceExecutionMetrics(
                            source_name=c_src,
                            requested_result_count=target_per_source,
                            status=SourceStatusEnum.FAILED,
                            error_code="ADAPTER_UNHANDLED_EXCEPTION",
                            error_message=str(exc),
                            duration_ms=dur_ms
                        )
                        return c_src, [], status_rep, mets

            tasks_to_run.append(asyncio.create_task(_fetch_task(canon_src, adapter)))

        # Execute all tasks concurrently
        if tasks_to_run:
            try:
                results = await asyncio.gather(*tasks_to_run, return_exceptions=False)
            except asyncio.CancelledError:
                for t in tasks_to_run:
                    if not t.done():
                        t.cancel()
                await asyncio.gather(*tasks_to_run, return_exceptions=True)
                if enforce_guard and projected_credits > 0 and started_adapter_calls == 0:
                    provider_budget_manager.release_credits(projected_credits)
                raise

            for c_src, items, status_rep, mets in results:
                source_statuses[c_src] = status_rep
                source_metrics[c_src] = mets
                source_buckets[c_src] = items
                pooled_results.extend(items)

                if status_rep.status == SourceStatusEnum.NOT_CONFIGURED:
                    warnings.append(f"Source '{c_src}' is not configured: {status_rep.error_message or 'Missing credentials'}")
                elif status_rep.status in (SourceStatusEnum.FAILED, SourceStatusEnum.RATE_LIMITED, SourceStatusEnum.QUOTA_EXHAUSTED):
                    errors.append({
                        "source": c_src,
                        "status": status_rep.status.value,
                        "error_code": status_rep.error_code,
                        "error_message": status_rep.error_message
                    })
                    warnings.append(f"Source '{c_src}' reported {status_rep.status.value}: {status_rep.error_message or ''}")
        elif enforce_guard and projected_credits > 0:
            provider_budget_manager.release_credits(projected_credits)

        return self._assemble_discovery_response(
            clean_q=clean_q,
            norm_q=norm_q,
            active_tab=active_tab,
            resolved_tax=resolved_tax,
            active_sources=active_sources,
            source_statuses=source_statuses,
            source_metrics=source_metrics,
            source_buckets=source_buckets,
            pooled_results=pooled_results,
            warnings=warnings,
            errors=errors,
            page=page,
            page_size=page_size,
            req_id=req_id,
        )


# Singleton instance
search_orchestration_service = SearchOrchestrationService()

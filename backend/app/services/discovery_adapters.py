"""
Nivora (Architect AI) — Discovery Source Adapters
Phase 5B — Stage 2

Implements dedicated, isolated source adapters for the 7 architectural discovery channels:
1. Pinterest (SocialCrawl)
2. Instagram (SocialCrawl Reels & Profiles)
3. YouTube (SocialCrawl YouTube)
4. Reddit (SocialCrawl Reddit)
5. Google Search (Programmable Search Engine / Web Adapter)
6. Google Shopping (SocialCrawl Shopping)
7. Google Places / Business (Google Places Platform API & SocialCrawl)

Each adapter:
- Accepts a normalized discovery query and taxonomy context.
- Generates source-appropriate queries.
- Invokes connector functions safely without exposing secrets.
- Normalizes raw payloads into `NormalizedDiscoveryResult` objects.
- Maps into the 3 independent classification dimensions.
- Produces `SourceStatusReport` and `SourceExecutionMetrics`.
- Preserves pagination tokens and error boundaries.
"""

import re
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime

from app.core.config import settings
from app.schemas.discovery import (
    SourceStatusEnum,
    DiscoveryTabEnum,
    ContentTypeEnum,
    DiscoveryClassificationEnum,
    MetadataClassificationEnum,
    SourceStatusReport,
    SourceExecutionMetrics,
    NormalizedDiscoveryResult,
    determine_relevant_discovery_tabs,
    ProvenanceEnum,
    MediaStatusEnum,
)

logger = logging.getLogger("architect_ai.discovery_adapters")


def classify_adapter_exception(e: Exception, default_error_code: str) -> Tuple[SourceStatusEnum, str, str]:
    """
    Classifies an adapter exception into appropriate SourceStatusEnum and error code.
    Detects rate limiting (429) and quota exhaustion (credits/balance/billing).
    """
    err_str = str(e).lower()
    if any(kw in err_str for kw in ["rate limit", "429", "too many requests", "throttle"]):
        return SourceStatusEnum.RATE_LIMITED, "RATE_LIMITED", str(e)
    if any(kw in err_str for kw in ["quota", "credits", "insufficient credits", "balance", "billing"]):
        return SourceStatusEnum.QUOTA_EXHAUSTED, "QUOTA_EXHAUSTED", str(e)
    return SourceStatusEnum.FAILED, default_error_code, str(e)


# ==============================================================================
# BASE SOURCE ADAPTER
# ==============================================================================

class BaseSourceAdapter(ABC):
    """
    Abstract contract for all discovery source adapters.
    """
    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if the required credentials/settings for this source exist."""
        pass

    @abstractmethod
    def build_queries(self, query: str, taxonomy_context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generates source-specific query variations preserving the user query."""
        pass

    @abstractmethod
    def fetch(
        self,
        query: str,
        cursor: Optional[str] = None,
        limit: int = 50,
        dry_run: bool = False,
        taxonomy_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[NormalizedDiscoveryResult], SourceStatusReport, SourceExecutionMetrics]:
        """
        Executes query against connector, normalizes items, and reports status/metrics.
        Must isolate errors safely without failing the entire orchestration.
        """
        pass

    async def fetch_async(
        self,
        query: str,
        cursor: Optional[str] = None,
        limit: int = 50,
        dry_run: bool = False,
        taxonomy_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[NormalizedDiscoveryResult], SourceStatusReport, SourceExecutionMetrics]:
        """
        Asynchronous fetch contract.
        By default, runs synchronous fetch in an executor thread.
        Adapters with native async connectors override this directly.
        """
        import asyncio
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.fetch(
                query=query,
                cursor=cursor,
                limit=limit,
                dry_run=dry_run,
                taxonomy_context=taxonomy_context
            )
        )


# ==============================================================================
# PINTEREST EVIDENCE-BASED CLASSIFIER
# ==============================================================================

def classify_pinterest_pin(
    title: Optional[str] = None,
    description: Optional[str] = None,
    board_name: Optional[str] = None,
    raw_content_type: Optional[str] = None,
    board: Optional[str] = None
) -> Tuple[Optional[str], Optional[DiscoveryClassificationEnum], Optional[MetadataClassificationEnum]]:
    """
    Evidence-based Pinterest classification across the three independent dimensions.
    Examines title, description, and board_name for concrete architectural indicators.
    Leaves classifications as None when evidence is insufficient.
    """
    effective_board = board_name or board or ""
    evidence = f"{title or ''} {description or ''} {effective_board}".lower().strip()
    if not evidence or len(evidence) < 5:
        fallback_ct = raw_content_type if raw_content_type else None
        return fallback_ct, DiscoveryClassificationEnum.INSPIRATION, None

    # 1. Floor plan or technical drawing
    drawing_keywords = [
        "floor plan", "blueprint", "cad drawing", "section drawing",
        "detail drawing", "elevation drawing", "architectural drawing",
        "layout plan", "site plan", "structural drawing", "schematic"
    ]
    if any(k in evidence for k in drawing_keywords):
        return (
            "architectural_project",
            DiscoveryClassificationEnum.INSPIRATION,
            MetadataClassificationEnum.DETAIL_DRAWING
        )

    # 2. Installation guide / tutorial
    install_keywords = [
        "installation guide", "how to install", "step by step installation",
        "fitting guide", "diy installation", "laying instructions",
        "fixing guide", "installation tutorial"
    ]
    if any(k in evidence for k in install_keywords):
        return (
            "installation_demo",
            DiscoveryClassificationEnum.TUTORIAL,
            MetadataClassificationEnum.INSTALLATION_GUIDE
        )

    # 3. Facade design
    facade_keywords = [
        "facade", "front elevation", "exterior elevation", "exterior cladding",
        "building envelope", "curtain wall", "louvers", "sunshade", "facade design"
    ]
    if any(k in evidence for k in facade_keywords):
        return (
            "architectural_project",
            DiscoveryClassificationEnum.INSPIRATION,
            MetadataClassificationEnum.FACADE_DETAIL
        )

    # 4. Interior design
    interior_keywords = [
        "interior design", "living room interior", "bedroom interior",
        "modular kitchen", "bathroom interior", "dining interior",
        "false ceiling design", "wardrobe interior", "interior decor"
    ]
    if any(k in evidence for k in interior_keywords):
        return (
            "architectural_project",
            DiscoveryClassificationEnum.INTERIOR_DESIGN_PROJECT,
            MetadataClassificationEnum.INTERIOR_DESIGN
        )

    # 5. Material specimen / sample
    material_keywords = [
        "material sample", "material specimen", "swatch", "tile sample",
        "granite slab", "marble sample", "terrazzo sample", "wood veneer sample",
        "fabric swatch", "color palette", "cseb block", "laterite block",
        "floor tiles", "handmade tiles", "cement tiles", "tile pattern", "tile texture",
        "marble texture", "granite texture", "wood texture", "flooring tiles"
    ]
    if any(k in evidence for k in material_keywords):
        return (
            "material_specimen",
            DiscoveryClassificationEnum.INSPIRATION,
            MetadataClassificationEnum.MATERIAL_SPECIFICATION
        )

    # 6. Product photograph (fixtures, sanitaryware, fittings, lighting, furniture)
    product_keywords = [
        "faucet", "hardware fitting", "cabinet handle", "shower head", "diverter",
        "sanitaryware", "pendant light", "chandelier fixture", "luminaire fixture",
        "sofa design", "dining table design", "lounge chair", "product design",
        "furniture", "dining table", "chair design", "seating furniture", "armchair"
    ]
    if any(k in evidence for k in product_keywords):
        return (
            "manufacturer_product",
            DiscoveryClassificationEnum.PRODUCT,
            MetadataClassificationEnum.PRODUCT_CATALOG
        )

    # 7. Architectural project (residences, villas, commercial buildings)
    project_keywords = [
        "villa architecture", "residence architecture", "architectural project",
        "house design", "bungalow design", "contemporary villa", "courtyard house",
        "residential architecture", "modern villa", "architectural walkthrough"
    ]
    if any(k in evidence for k in project_keywords):
        role = DiscoveryClassificationEnum.ARCHITECT_PORTFOLIO if any(k in evidence for k in ["architect", "studio", "firm", "by architect"]) else DiscoveryClassificationEnum.INSPIRATION
        return (
            "architectural_project",
            role,
            MetadataClassificationEnum.ARCHITECTURAL_PROJECT
        )

    # 8. Insufficient evidence fallback
    # If raw_content_type was provided upstream, respect it; otherwise leave content_type as None
    fallback_ct = raw_content_type if raw_content_type else None
    return fallback_ct, DiscoveryClassificationEnum.INSPIRATION, None


# ==============================================================================
# 1. PINTEREST ADAPTER
# ==============================================================================

class PinterestAdapter(BaseSourceAdapter):
    def __init__(self):
        super().__init__("pinterest")

    def is_configured(self) -> bool:
        from app.services.pinterest_service import is_socialcrawl_configured
        return is_socialcrawl_configured()

    def build_queries(self, query: str, taxonomy_context: Optional[Dict[str, Any]] = None) -> List[str]:
        clean = query.strip()
        if not clean:
            return ["architectural design inspiration"]
        return [
            f"{clean} architecture",
            f"{clean} wall design",
            f"{clean} construction inspiration",
            f"{clean} house projects",
            f"{clean} architectural design",
        ]

    def fetch(
        self,
        query: str,
        cursor: Optional[str] = None,
        limit: int = 50,
        dry_run: bool = False,
        taxonomy_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[NormalizedDiscoveryResult], SourceStatusReport, SourceExecutionMetrics]:
        start_time = time.time()
        queries = self.build_queries(query, taxonomy_context)
        primary_query = queries[0]

        if not self.is_configured():
            duration_ms = (time.time() - start_time) * 1000
            status_report = SourceStatusReport(
                source_name=self.source_name,
                status=SourceStatusEnum.NOT_CONFIGURED,
                requested=True,
                error_message="SOCIALCRAWL_API_KEY environment variable is missing for Pinterest.",
                duration_ms=duration_ms
            )
            metrics = SourceExecutionMetrics(
                source_name=self.source_name,
                requested_result_count=limit,
                status=SourceStatusEnum.NOT_CONFIGURED,
                error_message="Pinterest API not configured.",
                duration_ms=duration_ms
            )
            return [], status_report, metrics

        from app.services.pinterest_service import search_pinterest_page
        results: List[NormalizedDiscoveryResult] = []
        has_more = False
        next_cursor: Optional[str] = None
        error_code: Optional[str] = None
        error_msg: Optional[str] = None
        status = SourceStatusEnum.SUCCESS

        try:
            raw_res = search_pinterest_page(
                query=primary_query,
                cursor=cursor,
                dry_run=dry_run
            )
            if raw_res and isinstance(raw_res, dict):
                if raw_res.get("error"):
                    status, error_code, error_msg = classify_adapter_exception(Exception(str(raw_res["error"])), "PINTEREST_API_ERROR")
                else:
                    raw_items = raw_res.get("items", [])
                    has_more = bool(raw_res.get("has_more", False))
                    next_cursor = raw_res.get("next_cursor")

                    for item in raw_items:
                        pin_id = str(item.get("pin_id") or item.get("id") or "")
                        src_url = item.get("source_url") or (f"https://www.pinterest.com/pin/{pin_id}/" if pin_id else "")
                        canon_url = f"https://www.pinterest.com/pin/{pin_id}/" if pin_id else src_url

                        # Evidence-based classification
                        p_title = item.get("title")
                        p_desc = item.get("description")
                        p_board = item.get("board_name")
                        c_type, disc_role, meta_domain = classify_pinterest_pin(
                            title=p_title,
                            description=p_desc,
                            board_name=p_board,
                            raw_content_type=item.get("content_type")
                        )

                        norm_item = NormalizedDiscoveryResult(
                            source=self.source_name,
                            source_result_id=pin_id or None,
                            original_url=src_url,
                            canonical_url=canon_url,
                            title=p_title or f"{query.title()} Inspiration",
                            description=p_desc,
                            image_url=item.get("image_url"),
                            thumbnail_url=item.get("thumbnail_url") or item.get("image_url"),
                            creator_name=item.get("creator_name"),
                            creator_url=item.get("creator_url"),
                            published_at=item.get("created_at"),
                            retrieved_at=datetime.utcnow().isoformat(),
                            # Independent 3D Classification
                            content_type=c_type,
                            discovery_classification=disc_role,
                            metadata_classification=meta_domain,
                            # Taxonomy
                            category=taxonomy_context.get("category") if taxonomy_context else None,
                            subcategory=taxonomy_context.get("subcategory") if taxonomy_context else None,
                            item=taxonomy_context.get("item") if taxonomy_context else None,
                            source_attribution="Pinterest Pin",
                            discovery_query=primary_query,
                            verification_status="UNVERIFIED",
                            provenance=ProvenanceEnum.LIVE_DISCOVERY,
                            media_status=MediaStatusEnum.MEDIA_READY if item.get("image_url") else MediaStatusEnum.MEDIA_UNUSABLE,
                            source_metadata={
                                "board_name": p_board,
                                "saves_count": item.get("saves_count")
                            }
                        )
                        norm_item.relevant_tabs = determine_relevant_discovery_tabs(norm_item)
                        results.append(norm_item)

                    if not raw_items:
                        status = SourceStatusEnum.EMPTY
            elif raw_res is None or (isinstance(raw_res, (list, dict)) and not raw_res):
                status = SourceStatusEnum.EMPTY
            else:
                status = SourceStatusEnum.FAILED
                error_code = "MALFORMED_UPSTREAM_RESPONSE"
                error_msg = f"Unexpected upstream response format: expected dict, received {type(raw_res).__name__}."

        except Exception as e:
            logger.error(f"[PinterestAdapter] Execution error: {e}")
            status, error_code, error_msg = classify_adapter_exception(e, "PINTEREST_ADAPTER_ERROR")

        duration_ms = (time.time() - start_time) * 1000
        status_report = SourceStatusReport(
            source_name=self.source_name,
            status=status,
            requested=True,
            result_count=len(results),
            unique_result_count=len(results),
            pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
            has_more=has_more,
            next_page_token=next_cursor,
            error_code=error_code,
            error_message=error_msg,
            duration_ms=duration_ms
        )
        metrics = SourceExecutionMetrics(
            source_name=self.source_name,
            requested_result_count=limit,
            returned_result_count=len(results),
            unique_result_count=len(results),
            duplicate_count=0,
            pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
            pagination_availability=has_more,
            request_count=1,
            cache_hit=False,
            duration_ms=duration_ms,
            status=status,
            error_code=error_code,
            error_message=error_msg
        )
        return results[:limit], status_report, metrics


# ==============================================================================
# 2. INSTAGRAM ADAPTER
# ==============================================================================

class InstagramAdapter(BaseSourceAdapter):
    def __init__(self):
        super().__init__("instagram")

    def is_configured(self) -> bool:
        from app.services.socialcrawl_service import is_socialcrawl_configured
        return is_socialcrawl_configured()

    def build_queries(self, query: str, taxonomy_context: Optional[Dict[str, Any]] = None) -> List[str]:
        clean = query.strip()
        if not clean:
            return ["architectural design walkthrough"]
        return [
            f"{clean} architecture design",
            f"{clean} construction projects",
            f"{clean} design walkthrough",
            f"{clean} architectural reel",
        ]

    def fetch(
        self,
        query: str,
        cursor: Optional[str] = None,
        limit: int = 50,
        dry_run: bool = False,
        taxonomy_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[NormalizedDiscoveryResult], SourceStatusReport, SourceExecutionMetrics]:
        start_time = time.time()
        queries = self.build_queries(query, taxonomy_context)
        primary_query = queries[0]

        if not self.is_configured():
            duration_ms = (time.time() - start_time) * 1000
            status_report = SourceStatusReport(
                source_name=self.source_name,
                status=SourceStatusEnum.NOT_CONFIGURED,
                requested=True,
                error_message="SOCIALCRAWL_API_KEY environment variable is missing for Instagram.",
                duration_ms=duration_ms
            )
            metrics = SourceExecutionMetrics(
                source_name=self.source_name,
                requested_result_count=limit,
                status=SourceStatusEnum.NOT_CONFIGURED,
                error_message="Instagram API not configured.",
                duration_ms=duration_ms
            )
            return [], status_report, metrics

        from app.services.socialcrawl_service import search_instagram_reels
        results: List[NormalizedDiscoveryResult] = []
        has_more = False
        next_cursor: Optional[str] = None
        error_code: Optional[str] = None
        error_msg: Optional[str] = None
        status = SourceStatusEnum.SUCCESS

        try:
            raw_res = search_instagram_reels(
                query=primary_query,
                cursor=cursor,
                max_pages=1,
                dry_run=dry_run
            )
            if raw_res and isinstance(raw_res, dict):
                if raw_res.get("error"):
                    status, error_code, error_msg = classify_adapter_exception(Exception(str(raw_res["error"])), "INSTAGRAM_API_ERROR")
                else:
                    raw_items = raw_res.get("items", [])
                    has_more = bool(raw_res.get("has_more", False))
                    next_cursor = raw_res.get("next_cursor")

                    for item in raw_items:
                        reel_id = str(item.get("reel_id") or item.get("id") or "")
                        shortcode = item.get("shortcode") or reel_id
                        src_url = item.get("source_url") or (f"https://www.instagram.com/reel/{shortcode}/" if shortcode else "")
                        canon_url = f"https://www.instagram.com/reel/{shortcode}/" if shortcode else src_url

                        caption = item.get("caption") or ""
                        title = caption.split("\n")[0][:120].strip() or f"{query.title()} Architectural Reel"

                        # Infer classification from caption
                        caption_lower = caption.lower()
                        if any(w in caption_lower for w in ["progress", "under construction", "site work", "laying", "casting"]):
                            role = DiscoveryClassificationEnum.WORK_IN_PROGRESS
                            meta_domain = MetadataClassificationEnum.CONSTRUCTION_PROGRESS
                        elif any(w in caption_lower for w in ["completed", "handover", "walkthrough", "finished project"]):
                            role = DiscoveryClassificationEnum.COMPLETED_PROJECT
                            meta_domain = MetadataClassificationEnum.ARCHITECTURAL_PROJECT
                        else:
                            role = DiscoveryClassificationEnum.INSPIRATION
                            meta_domain = MetadataClassificationEnum.INTERIOR_DESIGN

                        norm_item = NormalizedDiscoveryResult(
                            source=self.source_name,
                            source_result_id=shortcode or reel_id or None,
                            original_url=src_url,
                            canonical_url=canon_url,
                            title=title,
                            description=caption,
                            image_url=item.get("thumbnail_url"),
                            thumbnail_url=item.get("thumbnail_url"),
                            video_url=item.get("video_url"),
                            creator_name=item.get("creator_name") or item.get("creator_handle"),
                            creator_url=item.get("creator_url") or (f"https://www.instagram.com/{item.get('creator_handle')}/" if item.get("creator_handle") else None),
                            published_at=item.get("date_posted"),
                            retrieved_at=datetime.utcnow().isoformat(),
                            # Classification
                            content_type="architectural_reel",
                            discovery_classification=role,
                            metadata_classification=meta_domain,
                            # Taxonomy
                            category=taxonomy_context.get("category") if taxonomy_context else None,
                            subcategory=taxonomy_context.get("subcategory") if taxonomy_context else None,
                            item=taxonomy_context.get("item") if taxonomy_context else None,
                            source_attribution="Instagram Reel",
                            discovery_query=primary_query,
                            verification_status="UNVERIFIED",
                            provenance=ProvenanceEnum.LIVE_DISCOVERY,
                            media_status=MediaStatusEnum.MEDIA_READY if (item.get("thumbnail_url") or item.get("video_url")) else MediaStatusEnum.MEDIA_UNUSABLE,
                            source_metadata={
                                "likes_count": item.get("likes_count"),
                                "views_count": item.get("views_count"),
                                "comments_count": item.get("comments_count")
                            }
                        )
                        norm_item.relevant_tabs = determine_relevant_discovery_tabs(norm_item)
                        results.append(norm_item)

                    if not raw_items:
                        status = SourceStatusEnum.EMPTY
            elif raw_res is None or (isinstance(raw_res, (list, dict)) and not raw_res):
                status = SourceStatusEnum.EMPTY
            else:
                status = SourceStatusEnum.FAILED
                error_code = "MALFORMED_UPSTREAM_RESPONSE"
                error_msg = f"Unexpected upstream response format: expected dict, received {type(raw_res).__name__}."

        except Exception as e:
            logger.error(f"[InstagramAdapter] Execution error: {e}")
            status, error_code, error_msg = classify_adapter_exception(e, "INSTAGRAM_ADAPTER_ERROR")

        duration_ms = (time.time() - start_time) * 1000
        status_report = SourceStatusReport(
            source_name=self.source_name,
            status=status,
            requested=True,
            result_count=len(results),
            unique_result_count=len(results),
            pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
            has_more=has_more,
            next_page_token=next_cursor,
            error_code=error_code,
            error_message=error_msg,
            duration_ms=duration_ms
        )
        metrics = SourceExecutionMetrics(
            source_name=self.source_name,
            requested_result_count=limit,
            returned_result_count=len(results),
            unique_result_count=len(results),
            duplicate_count=0,
            pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
            pagination_availability=has_more,
            request_count=1,
            cache_hit=False,
            duration_ms=duration_ms,
            status=status,
            error_code=error_code,
            error_message=error_msg
        )
        return results[:limit], status_report, metrics


# ==============================================================================
# 3. YOUTUBE ADAPTER
# ==============================================================================

class YouTubeAdapter(BaseSourceAdapter):
    def __init__(self):
        super().__init__("youtube")

    def is_configured(self) -> bool:
        from app.services.socialcrawl_service import is_socialcrawl_configured
        return is_socialcrawl_configured()

    def build_queries(self, query: str, taxonomy_context: Optional[Dict[str, Any]] = None) -> List[str]:
        clean = query.strip()
        if not clean:
            return ["architectural walkthrough house tour"]
        return [
            f"{clean} construction",
            f"{clean} installation",
            f"{clean} manufacturing",
            f"{clean} comparison",
            f"{clean} building projects",
            f"{clean} architectural project walkthrough",
        ]

    def fetch(
        self,
        query: str,
        cursor: Optional[str] = None,
        limit: int = 50,
        dry_run: bool = False,
        taxonomy_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[NormalizedDiscoveryResult], SourceStatusReport, SourceExecutionMetrics]:
        start_time = time.time()
        queries = self.build_queries(query, taxonomy_context)
        primary_query = queries[0]

        if not self.is_configured():
            duration_ms = (time.time() - start_time) * 1000
            status_report = SourceStatusReport(
                source_name=self.source_name,
                status=SourceStatusEnum.NOT_CONFIGURED,
                requested=True,
                error_message="SOCIALCRAWL_API_KEY environment variable is missing for YouTube.",
                duration_ms=duration_ms
            )
            metrics = SourceExecutionMetrics(
                source_name=self.source_name,
                requested_result_count=limit,
                status=SourceStatusEnum.NOT_CONFIGURED,
                error_message="YouTube API not configured.",
                duration_ms=duration_ms
            )
            return [], status_report, metrics

        from app.services.socialcrawl_service import search_youtube
        results: List[NormalizedDiscoveryResult] = []
        has_more = False
        next_cursor: Optional[str] = None
        error_code: Optional[str] = None
        error_msg: Optional[str] = None
        status = SourceStatusEnum.SUCCESS

        try:
            raw_res = search_youtube(
                query=primary_query,
                cursor=cursor,
                max_pages=1,
                dry_run=dry_run
            )
            if raw_res and isinstance(raw_res, dict):
                if raw_res.get("error"):
                    status, error_code, error_msg = classify_adapter_exception(Exception(str(raw_res["error"])), "YOUTUBE_API_ERROR")
                else:
                    raw_items = raw_res.get("items", [])
                    has_more = bool(raw_res.get("has_more", False))
                    next_cursor = raw_res.get("next_cursor")

                    for item in raw_items:
                        vid_id = str(item.get("video_embed_id") or item.get("video_id") or item.get("id") or "")
                        src_url = item.get("source_url") or (f"https://www.youtube.com/watch?v={vid_id}" if vid_id else "")
                        canon_url = f"https://www.youtube.com/watch?v={vid_id}" if vid_id else src_url

                        title = item.get("title") or f"{query.title()} Video Walkthrough"
                        title_lower = title.lower()

                        if any(w in title_lower for w in ["how to", "installation", "laying", "fitting", "tutorial", "step by step"]):
                            role = DiscoveryClassificationEnum.TUTORIAL
                            meta_domain = MetadataClassificationEnum.INSTALLATION_GUIDE
                        elif any(w in title_lower for w in ["walkthrough", "house tour", "architectural tour", "villa"]):
                            role = DiscoveryClassificationEnum.COMPLETED_PROJECT
                            meta_domain = MetadataClassificationEnum.ARCHITECTURAL_PROJECT
                        elif any(w in title_lower for w in ["vs", "review", "demonstration", "specification"]):
                            role = DiscoveryClassificationEnum.PRODUCT_DEMONSTRATION
                            meta_domain = MetadataClassificationEnum.MATERIAL_SPECIFICATION
                        else:
                            role = DiscoveryClassificationEnum.COMPLETED_PROJECT
                            meta_domain = MetadataClassificationEnum.ARCHITECTURAL_PROJECT

                        norm_item = NormalizedDiscoveryResult(
                            source=self.source_name,
                            source_result_id=vid_id or None,
                            original_url=src_url,
                            canonical_url=canon_url,
                            title=title,
                            description=item.get("description"),
                            image_url=item.get("thumbnail_url"),
                            thumbnail_url=item.get("thumbnail_url"),
                            video_url=src_url,
                            creator_name=item.get("channel_title") or item.get("creator_name"),
                            creator_url=item.get("channel_url") or item.get("creator_url"),
                            published_at=item.get("published_at"),
                            retrieved_at=datetime.utcnow().isoformat(),
                            # Classification
                            content_type="youtube_walkthrough",
                            discovery_classification=role,
                            metadata_classification=meta_domain,
                            # Taxonomy
                            category=taxonomy_context.get("category") if taxonomy_context else None,
                            subcategory=taxonomy_context.get("subcategory") if taxonomy_context else None,
                            item=taxonomy_context.get("item") if taxonomy_context else None,
                            source_attribution="YouTube Video",
                            discovery_query=primary_query,
                            verification_status="UNVERIFIED",
                            provenance=ProvenanceEnum.LIVE_DISCOVERY,
                            media_status=MediaStatusEnum.MEDIA_READY,
                            source_metadata={
                                "duration": item.get("duration"),
                                "is_short": item.get("is_short"),
                                "views_count": item.get("views_count")
                            }
                        )
                        norm_item.relevant_tabs = determine_relevant_discovery_tabs(norm_item)
                        results.append(norm_item)

                    if not raw_items:
                        status = SourceStatusEnum.EMPTY
            elif raw_res is None or (isinstance(raw_res, (list, dict)) and not raw_res):
                status = SourceStatusEnum.EMPTY
            else:
                status = SourceStatusEnum.FAILED
                error_code = "MALFORMED_UPSTREAM_RESPONSE"
                error_msg = f"Unexpected upstream response format: expected dict, received {type(raw_res).__name__}."

        except Exception as e:
            logger.error(f"[YouTubeAdapter] Execution error: {e}")
            status, error_code, error_msg = classify_adapter_exception(e, "YOUTUBE_ADAPTER_ERROR")

        duration_ms = (time.time() - start_time) * 1000
        status_report = SourceStatusReport(
            source_name=self.source_name,
            status=status,
            requested=True,
            result_count=len(results),
            unique_result_count=len(results),
            pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
            has_more=has_more,
            next_page_token=next_cursor,
            error_code=error_code,
            error_message=error_msg,
            duration_ms=duration_ms
        )
        metrics = SourceExecutionMetrics(
            source_name=self.source_name,
            requested_result_count=limit,
            returned_result_count=len(results),
            unique_result_count=len(results),
            duplicate_count=0,
            pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
            pagination_availability=has_more,
            request_count=1,
            cache_hit=False,
            duration_ms=duration_ms,
            status=status,
            error_code=error_code,
            error_message=error_msg
        )
        return results[:limit], status_report, metrics


# ==============================================================================
# 4. REDDIT ADAPTER
# ==============================================================================

class RedditAdapter(BaseSourceAdapter):
    def __init__(self):
        super().__init__("reddit")

    def is_configured(self) -> bool:
        from app.services.socialcrawl_service import is_socialcrawl_configured
        return is_socialcrawl_configured()

    def build_queries(self, query: str, taxonomy_context: Optional[Dict[str, Any]] = None) -> List[str]:
        clean = query.strip()
        if not clean:
            return ["architecture materials construction discussion"]
        return [
            f"{clean} comparisons and construction discussions",
            f"{clean} architecture materials discussion",
            f"{clean} cost durability experience",
            f"{clean} cost review",
            f"{clean} architecture materials review",
            f"{clean} construction details review",
        ]

    def fetch(
        self,
        query: str,
        cursor: Optional[str] = None,
        limit: int = 50,
        dry_run: bool = False,
        taxonomy_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[NormalizedDiscoveryResult], SourceStatusReport, SourceExecutionMetrics]:
        start_time = time.time()
        queries = self.build_queries(query, taxonomy_context)
        primary_query = queries[0]

        if not self.is_configured():
            duration_ms = (time.time() - start_time) * 1000
            status_report = SourceStatusReport(
                source_name=self.source_name,
                status=SourceStatusEnum.NOT_CONFIGURED,
                requested=True,
                error_message="SOCIALCRAWL_API_KEY environment variable is missing for Reddit.",
                duration_ms=duration_ms
            )
            metrics = SourceExecutionMetrics(
                source_name=self.source_name,
                requested_result_count=limit,
                status=SourceStatusEnum.NOT_CONFIGURED,
                error_message="Reddit API not configured.",
                duration_ms=duration_ms
            )
            return [], status_report, metrics

        from app.services.socialcrawl_service import search_reddit
        results: List[NormalizedDiscoveryResult] = []
        has_more = False
        next_cursor: Optional[str] = None
        error_code: Optional[str] = None
        error_msg: Optional[str] = None
        status = SourceStatusEnum.SUCCESS

        try:
            raw_res = search_reddit(
                query=primary_query,
                cursor=cursor,
                max_pages=1,
                dry_run=dry_run
            )
            if raw_res and isinstance(raw_res, dict):
                if raw_res.get("error"):
                    status, error_code, error_msg = classify_adapter_exception(Exception(str(raw_res["error"])), "REDDIT_API_ERROR")
                else:
                    raw_items = raw_res.get("items", [])
                    has_more = bool(raw_res.get("has_more", False))
                    next_cursor = raw_res.get("next_cursor")

                    for item in raw_items:
                        post_id = str(item.get("post_id") or item.get("id") or "")
                        src_url = item.get("source_url") or ""
                        sub_raw = str(item.get("subreddit") or item.get("subreddit_name") or "").strip()
                        if sub_raw.startswith("r/"):
                            sub_clean = sub_raw[2:]
                        else:
                            sub_clean = sub_raw
                        sub_formatted = f"r/{sub_clean}" if sub_clean else "r/architecture"

                        title = item.get("title") or f"{query.title()} Architectural Discussion"
                        title_lower = title.lower()

                        meta_domain = MetadataClassificationEnum.COST_BREAKDOWN if any(w in title_lower for w in ["cost", "price", "budget", "quote"]) else MetadataClassificationEnum.MATERIAL_SPECIFICATION

                        desc = item.get("description") or item.get("selftext") or item.get("text")
                        img_candidate = item.get("image_url") or item.get("thumbnail_url") or item.get("media_url")
                        img_str = img_candidate if (isinstance(img_candidate, str) and img_candidate.startswith("http")) else None

                        thumb_candidate = item.get("thumbnail_url") or item.get("image_url") or item.get("media_url")
                        thumb_str = thumb_candidate if (isinstance(thumb_candidate, str) and thumb_candidate.startswith("http")) else img_str

                        vid_candidate = item.get("video_url")
                        vid_str = vid_candidate if (isinstance(vid_candidate, str) and vid_candidate.startswith("http")) else None

                        author_name = item.get("creator_name") or (f"u/{item.get('author')}" if item.get("author") else "Reddit Contributor")
                        author_url = item.get("creator_url") or (f"https://www.reddit.com/user/{item.get('author')}/" if item.get("author") else None)
                        pub_at = str(item.get("published_at") or item.get("created_utc") or "") or None

                        score_val = item.get("upvotes") if item.get("upvotes") is not None else item.get("score")
                        comments_val = item.get("comments") if item.get("comments") is not None else item.get("num_comments")

                        norm_item = NormalizedDiscoveryResult(
                            source=self.source_name,
                            source_result_id=post_id or None,
                            original_url=src_url,
                            canonical_url=src_url,
                            title=title,
                            description=desc,
                            image_url=img_str,
                            thumbnail_url=thumb_str,
                            video_url=vid_str,
                            creator_name=author_name,
                            creator_url=author_url,
                            published_at=pub_at,
                            retrieved_at=datetime.utcnow().isoformat(),
                            # Classification
                            content_type="architectural_discussion",
                            discovery_classification=DiscoveryClassificationEnum.DISCUSSION,
                            metadata_classification=meta_domain,
                            # Taxonomy
                            category=taxonomy_context.get("category") if taxonomy_context else None,
                            subcategory=taxonomy_context.get("subcategory") if taxonomy_context else None,
                            item=taxonomy_context.get("item") if taxonomy_context else None,
                            source_attribution=f"Reddit ({sub_formatted})" if sub_formatted else "Reddit Discussion",
                            discovery_query=primary_query,
                            verification_status="COMMUNITY_REVIEW",
                            provenance=ProvenanceEnum.LIVE_DISCOVERY,
                            media_status=MediaStatusEnum.MEDIA_READY if (img_str or vid_str) else MediaStatusEnum.TEXT_DISCUSSION,
                            source_metadata={
                                "score": score_val,
                                "num_comments": comments_val,
                                "subreddit": sub_formatted,
                                "subreddit_name": sub_clean,
                                "is_self": item.get("is_self", not bool(img_str or vid_str)),
                                "gallery_images": item.get("gallery_images") or [],
                                "domain": item.get("domain") or "reddit.com",
                                "flair": item.get("flair"),
                            }
                        )
                        norm_item.relevant_tabs = determine_relevant_discovery_tabs(norm_item)
                        results.append(norm_item)

                    if not raw_items:
                        status = SourceStatusEnum.EMPTY
            elif raw_res is None or (isinstance(raw_res, (list, dict)) and not raw_res):
                status = SourceStatusEnum.EMPTY
            else:
                status = SourceStatusEnum.FAILED
                error_code = "MALFORMED_UPSTREAM_RESPONSE"
                error_msg = f"Unexpected upstream response format: expected dict, received {type(raw_res).__name__}."

        except Exception as e:
            logger.error(f"[RedditAdapter] Execution error: {e}")
            status, error_code, error_msg = classify_adapter_exception(e, "REDDIT_ADAPTER_ERROR")

        duration_ms = (time.time() - start_time) * 1000
        status_report = SourceStatusReport(
            source_name=self.source_name,
            status=status,
            requested=True,
            result_count=len(results),
            unique_result_count=len(results),
            pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
            has_more=has_more,
            next_page_token=next_cursor,
            error_code=error_code,
            error_message=error_msg,
            duration_ms=duration_ms
        )
        metrics = SourceExecutionMetrics(
            source_name=self.source_name,
            requested_result_count=limit,
            returned_result_count=len(results),
            unique_result_count=len(results),
            duplicate_count=0,
            pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
            pagination_availability=has_more,
            request_count=1,
            cache_hit=False,
            duration_ms=duration_ms,
            status=status,
            error_code=error_code,
            error_message=error_msg
        )
        return results[:limit], status_report, metrics


# ==============================================================================
# 5. GOOGLE SEARCH ADAPTER (General Web Text Search Contract)
# ==============================================================================

class GoogleSearchAdapter(BaseSourceAdapter):
    """
    Google Search Adapter.
    Requirements:
    - General text web search must not be represented as operational if it does not exist.
    - If CUSTOM_SEARCH_CX is not configured, report NOT_CONFIGURED.
    - Do not substitute image search for general web search.
    - Do not fabricate results.
    """
    def __init__(self):
        super().__init__("google_search")

    def is_configured(self) -> bool:
        # In this project, general Google web text search requires both API key and search engine CX ID
        cx = settings.get_google_image_search_cx()
        key = settings.get_google_image_search_key()
        return bool(cx and key and len(cx.strip()) > 5 and len(key.strip()) > 10)

    def build_queries(self, query: str, taxonomy_context: Optional[Dict[str, Any]] = None) -> List[str]:
        clean = query.strip()
        return [f"architectural {clean}".strip()]

    def _build_unconfigured_response(self, limit: int, duration_ms: float):
        status_report = SourceStatusReport(
            source_name=self.source_name,
            status=SourceStatusEnum.NOT_CONFIGURED,
            requested=True,
            result_count=0,
            unique_result_count=0,
            pages_fetched=0,
            has_more=False,
            error_code="CUSTOM_SEARCH_CX_NOT_CONFIGURED",
            error_message="Google Custom Search Engine CX is not configured. General web text search is unavailable.",
            duration_ms=duration_ms
        )
        metrics = SourceExecutionMetrics(
            source_name=self.source_name,
            requested_result_count=limit,
            returned_result_count=0,
            unique_result_count=0,
            duplicate_count=0,
            pages_fetched=0,
            pagination_availability=False,
            request_count=0,
            cache_hit=False,
            duration_ms=duration_ms,
            status=SourceStatusEnum.NOT_CONFIGURED,
            error_code="CUSTOM_SEARCH_CX_NOT_CONFIGURED",
            error_message="Google Custom Search Engine CX is not configured.",
        )
        return [], status_report, metrics

    def _normalize_cse_items(
        self,
        raw_items: List[Dict[str, Any]],
        primary_query: str,
        taxonomy_context: Optional[Dict[str, Any]],
    ) -> List[NormalizedDiscoveryResult]:
        results: List[NormalizedDiscoveryResult] = []
        for idx, item in enumerate(raw_items):
            link = item.get("link") or ""
            if not link:
                continue
            title = item.get("title") or primary_query
            snippet = item.get("snippet") or ""
            pagemap = item.get("pagemap") or {}
            cse_img = (pagemap.get("cse_image") or [{}])[0].get("src")
            norm_item = NormalizedDiscoveryResult(
                source=self.source_name,
                source_result_id=item.get("cacheId") or f"gs_{idx}_{abs(hash(link)) % 100000}",
                original_url=link,
                canonical_url=link,
                title=title,
                description=snippet,
                image_url=cse_img,
                thumbnail_url=cse_img,
                creator_name=item.get("displayLink") or "Web Source",
                retrieved_at=datetime.utcnow().isoformat(),
                content_type=ContentTypeEnum.ARCHITECTURAL_PROJECT.value,
                discovery_classification=DiscoveryClassificationEnum.INSPIRATION,
                metadata_classification=MetadataClassificationEnum.ARCHITECTURAL_PROJECT,
                category=taxonomy_context.get("category") if taxonomy_context else None,
                subcategory=taxonomy_context.get("subcategory") if taxonomy_context else None,
                item=taxonomy_context.get("item") if taxonomy_context else None,
                source_attribution=item.get("displayLink") or "Google Search",
                discovery_query=primary_query,
                verification_status="UNVERIFIED",
                provenance=ProvenanceEnum.LIVE_DISCOVERY,
                media_status=MediaStatusEnum.MEDIA_READY if cse_img else MediaStatusEnum.TEXT_DISCUSSION,
                source_metadata={"displayLink": item.get("displayLink")},
            )
            norm_item.relevant_tabs = determine_relevant_discovery_tabs(norm_item)
            results.append(norm_item)
        return results

    def fetch(
        self,
        query: str,
        cursor: Optional[str] = None,
        limit: int = 50,
        dry_run: bool = False,
        taxonomy_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[NormalizedDiscoveryResult], SourceStatusReport, SourceExecutionMetrics]:
        start_time = time.time()
        if not self.is_configured():
            return self._build_unconfigured_response(limit, (time.time() - start_time) * 1000)

        primary_query = self.build_queries(query, taxonomy_context)[0]
        if dry_run:
            dur = (time.time() - start_time) * 1000
            return (
                [],
                SourceStatusReport(source_name=self.source_name, status=SourceStatusEnum.EMPTY, requested=True, duration_ms=dur),
                SourceExecutionMetrics(source_name=self.source_name, requested_result_count=limit, status=SourceStatusEnum.EMPTY, duration_ms=dur),
            )

        import requests as sync_requests
        status = SourceStatusEnum.SUCCESS
        error_code = None
        error_msg = None
        results: List[NormalizedDiscoveryResult] = []
        try:
            resp = sync_requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": settings.get_google_image_search_key(),
                    "cx": settings.get_google_image_search_cx(),
                    "q": primary_query,
                    "num": min(max(1, limit), 10),
                },
                timeout=10,
            )
            if resp.status_code == 200:
                results = self._normalize_cse_items(resp.json().get("items", []), primary_query, taxonomy_context)
                if not results:
                    status = SourceStatusEnum.EMPTY
            else:
                raise RuntimeError(f"HTTP {resp.status_code}")
        except Exception as e:
            status, error_code, error_msg = classify_adapter_exception(e, "GOOGLE_SEARCH_ERROR")

        dur = (time.time() - start_time) * 1000
        return (
            results[:limit],
            SourceStatusReport(
                source_name=self.source_name, status=status, requested=True,
                result_count=len(results), unique_result_count=len(results),
                pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
                error_code=error_code, error_message=error_msg, duration_ms=dur,
            ),
            SourceExecutionMetrics(
                source_name=self.source_name, requested_result_count=limit,
                returned_result_count=len(results), unique_result_count=len(results),
                pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
                request_count=1, status=status, error_code=error_code, error_message=error_msg, duration_ms=dur,
            ),
        )

    async def fetch_async(
        self,
        query: str,
        cursor: Optional[str] = None,
        limit: int = 50,
        dry_run: bool = False,
        taxonomy_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[NormalizedDiscoveryResult], SourceStatusReport, SourceExecutionMetrics]:
        start_time = time.time()
        if not self.is_configured():
            return self._build_unconfigured_response(limit, (time.time() - start_time) * 1000)

        primary_query = self.build_queries(query, taxonomy_context)[0]
        if dry_run:
            dur = (time.time() - start_time) * 1000
            return (
                [],
                SourceStatusReport(source_name=self.source_name, status=SourceStatusEnum.EMPTY, requested=True, duration_ms=dur),
                SourceExecutionMetrics(source_name=self.source_name, requested_result_count=limit, status=SourceStatusEnum.EMPTY, duration_ms=dur),
            )

        import httpx
        status = SourceStatusEnum.SUCCESS
        error_code = None
        error_msg = None
        results: List[NormalizedDiscoveryResult] = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params={
                        "key": settings.get_google_image_search_key(),
                        "cx": settings.get_google_image_search_cx(),
                        "q": primary_query,
                        "num": min(max(1, limit), 10),
                    },
                )
            if resp.status_code == 200:
                results = self._normalize_cse_items(resp.json().get("items", []), primary_query, taxonomy_context)
                if not results:
                    status = SourceStatusEnum.EMPTY
            else:
                raise RuntimeError(f"HTTP {resp.status_code}")
        except Exception as e:
            status, error_code, error_msg = classify_adapter_exception(e, "GOOGLE_SEARCH_ERROR")

        dur = (time.time() - start_time) * 1000
        return (
            results[:limit],
            SourceStatusReport(
                source_name=self.source_name, status=status, requested=True,
                result_count=len(results), unique_result_count=len(results),
                pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
                error_code=error_code, error_message=error_msg, duration_ms=dur,
            ),
            SourceExecutionMetrics(
                source_name=self.source_name, requested_result_count=limit,
                returned_result_count=len(results), unique_result_count=len(results),
                pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
                request_count=1, status=status, error_code=error_code, error_message=error_msg, duration_ms=dur,
            ),
        )


# ==============================================================================
# 6. GOOGLE SHOPPING ADAPTER
# ==============================================================================

class GoogleShoppingAdapter(BaseSourceAdapter):
    def __init__(self):
        super().__init__("google_shopping")

    def is_configured(self) -> bool:
        from app.services.socialcrawl_service import is_socialcrawl_configured
        return is_socialcrawl_configured()

    def build_queries(self, query: str, taxonomy_context: Optional[Dict[str, Any]] = None) -> List[str]:
        clean = query.strip()
        if not clean:
            return ["architectural materials products"]
        
        exclusions = "-wallpaper -sticker -toy -lego -puzzle -3d-panel -poster -shirt"
        
        # Query synthesis for ALL 6,319 materials:
        # material name + one short context word from its subcategory (max 4 words).
        # Selecting Fly Ash Bricks must never silently become Concrete Blocks.
        sub = ""
        if taxonomy_context:
            sub = taxonomy_context.get("subcategory") or taxonomy_context.get("filter_subcategory") or ""
        
        clean_words = clean.split()
        synthesized = clean
        if len(clean_words) < 4 and sub:
            stopwords = {"and", "&", "the", "for", "with", "all", "other", "general"}
            sub_words = [w.strip() for w in re.split(r"[\s,/]+", sub.lower()) if len(w) >= 3 and w not in stopwords]
            clean_lower_set = {w.lower() for w in clean_words}
            for sw in sub_words:
                if sw not in clean_lower_set:
                    cand = f"{clean} {sw}"
                    if len(cand.split()) <= 4:
                        synthesized = cand
                        break

        queries = [
            f"{synthesized} {exclusions}".strip(),
            f"{clean} products {exclusions}".strip(),
            f"{synthesized}".strip(),
            clean
        ]
        
        # Deduplicate preserving order
        deduped = []
        seen = set()
        for q in queries:
            if q not in seen:
                seen.add(q)
                deduped.append(q)
        return deduped

    def fetch(
        self,
        query: str,
        cursor: Optional[str] = None,
        limit: int = 50,
        dry_run: bool = False,
        taxonomy_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[NormalizedDiscoveryResult], SourceStatusReport, SourceExecutionMetrics]:
        start_time = time.time()
        queries = self.build_queries(query, taxonomy_context)
        primary_query = queries[0]

        if not self.is_configured():
            duration_ms = (time.time() - start_time) * 1000
            status_report = SourceStatusReport(
                source_name=self.source_name,
                status=SourceStatusEnum.NOT_CONFIGURED,
                requested=True,
                error_message="SOCIALCRAWL_API_KEY environment variable is missing for Google Shopping.",
                duration_ms=duration_ms
            )
            metrics = SourceExecutionMetrics(
                source_name=self.source_name,
                requested_result_count=limit,
                status=SourceStatusEnum.NOT_CONFIGURED,
                error_message="Google Shopping API not configured.",
                duration_ms=duration_ms
            )
            return [], status_report, metrics

        from app.services.socialcrawl_service import search_google_shopping
        results: List[NormalizedDiscoveryResult] = []
        error_code: Optional[str] = None
        error_msg: Optional[str] = None
        status = SourceStatusEnum.SUCCESS
        tax_ctx = taxonomy_context or {}
        req_country = str(tax_ctx.get("country") or "IN").strip().upper()
        req_region = tax_ctx.get("region") or tax_ctx.get("state") or tax_ctx.get("city")

        try:
            raw_res = search_google_shopping(
                query=primary_query,
                country=req_country,
                dry_run=dry_run
            )
            if raw_res and isinstance(raw_res, dict):
                if raw_res.get("error"):
                    status, error_code, error_msg = classify_adapter_exception(Exception(str(raw_res["error"])), "SHOPPING_API_ERROR")
                else:
                    raw_items = raw_res.get("items", [])
                    for item in raw_items:
                        if not isinstance(item, dict):
                            continue
                        prod = item.get("product") if isinstance(item.get("product"), dict) else item
                        ext = prod.get("ext") if isinstance(prod.get("ext"), dict) else {}

                        prod_id = str(
                            item.get("product_id")
                            or prod.get("id")
                            or item.get("gid")
                            or ext.get("gid")
                            or ""
                        )
                        src_url = (
                            item.get("product_url")
                            or prod.get("url")
                            or item.get("url")
                            or item.get("source_url")
                            or ""
                        )
                        raw_title = prod.get("title") or item.get("title") or ""
                        if not raw_title and not src_url and not prod_id:
                            continue

                        # Prioritize actual commercial products; filter out unrelated toys, wallpapers, stickers
                        raw_title_lower = raw_title.lower()
                        is_brick_or_masonry_query = any(k in query.lower() for k in ["brick", "masonry", "aac", "block", "laterite", "porotherm", "wirecut"])
                        if is_brick_or_masonry_query:
                            unrelated_indicators = [
                                "wallpaper", "wall sticker", "wall decal", "peel and stick", 
                                "lego", "toy", "puzzle", "t-shirt", "costume", "figurine", "pillow cover", "bedsheet"
                            ]
                            if any(ind in raw_title_lower for ind in unrelated_indicators):
                                continue

                        raw_seller = (
                            item.get("seller")
                            or prod.get("seller")
                            or item.get("merchant_name")
                            or prod.get("merchant_name")
                            or item.get("merchant")
                        )
                        seller_name = (
                            raw_seller.strip()
                            if isinstance(raw_seller, str) and raw_seller.strip()
                            else None
                        )

                        # Strictly preserve actual price (scalar or {"current": ..., "currency": ...}); never fabricate
                        raw_price = item.get("price") if item.get("price") is not None else prod.get("price")
                        parsed_price: Optional[float] = None
                        parsed_currency: Optional[str] = item.get("currency")
                        if isinstance(raw_price, dict):
                            if raw_price.get("current") is not None:
                                try:
                                    parsed_price = float(raw_price.get("current"))
                                except (ValueError, TypeError):
                                    parsed_price = None
                            if not parsed_currency and raw_price.get("currency"):
                                parsed_currency = raw_price.get("currency")
                        elif raw_price is not None:
                            try:
                                parsed_price = float(raw_price)
                            except (ValueError, TypeError):
                                parsed_price = None

                        raw_imgs = prod.get("image_urls")
                        img_url = (
                            item.get("image_url")
                            or item.get("thumbnail_url")
                            or (raw_imgs[0] if isinstance(raw_imgs, list) and raw_imgs else None)
                        )
                        raw_rating = item.get("rating") if item.get("rating") is not None else prod.get("rating")
                        rating_val = raw_rating.get("average") if isinstance(raw_rating, dict) else raw_rating
                        reviews_val = (
                            item.get("reviews_count")
                            if item.get("reviews_count") is not None
                            else (raw_rating.get("count") if isinstance(raw_rating, dict) else prod.get("reviews_count"))
                        )
                        item_country = str(item.get("country") or prod.get("country") or req_country).strip().upper()
                        effective_currency = parsed_currency or ("INR" if (parsed_price is not None and item_country == "IN") else None)

                        norm_item = NormalizedDiscoveryResult(
                            source=self.source_name,
                            source_result_id=prod_id or None,
                            original_url=src_url,
                            canonical_url=src_url,
                            title=raw_title or f"{query.title()} Product",
                            description=item.get("description") or prod.get("description"),
                            image_url=img_url,
                            thumbnail_url=img_url,
                            creator_name=seller_name,
                            location=str(req_region) if req_region else item_country,
                            price=parsed_price,
                            currency=effective_currency,
                            business_category="Merchant / Retailer",
                            published_at=None,
                            retrieved_at=datetime.utcnow().isoformat(),
                            # Classification
                            content_type="manufacturer_product",
                            discovery_classification=DiscoveryClassificationEnum.PRODUCT,
                            metadata_classification=MetadataClassificationEnum.PRODUCT_CATALOG,
                            # Taxonomy
                            category=tax_ctx.get("category"),
                            subcategory=tax_ctx.get("subcategory"),
                            item=tax_ctx.get("item"),
                            source_attribution=f"Google Shopping ({seller_name})" if seller_name else "Google Shopping",
                            discovery_query=primary_query,
                            verification_status="UNVERIFIED",
                            provenance=ProvenanceEnum.LIVE_DISCOVERY,
                            media_status=MediaStatusEnum.MEDIA_READY if img_url else MediaStatusEnum.MEDIA_UNUSABLE,
                            source_metadata={
                                "seller": seller_name,
                                "brand": item.get("brand") or prod.get("brand"),
                                "rating": rating_val,
                                "reviews_count": reviews_val,
                                "availability": item.get("availability") or prod.get("availability"),
                                "country": item_country,
                                "region": req_region,
                            }
                        )
                        norm_item.relevant_tabs = determine_relevant_discovery_tabs(norm_item)
                        results.append(norm_item)

                    if not raw_items:
                        status = SourceStatusEnum.EMPTY
            elif raw_res is None or (isinstance(raw_res, (list, dict)) and not raw_res):
                status = SourceStatusEnum.EMPTY
            else:
                status = SourceStatusEnum.FAILED
                error_code = "MALFORMED_UPSTREAM_RESPONSE"
                error_msg = f"Unexpected upstream response format: expected dict, received {type(raw_res).__name__}."

        except Exception as e:
            logger.error(f"[GoogleShoppingAdapter] Execution error: {e}")
            status, error_code, error_msg = classify_adapter_exception(e, "SHOPPING_ADAPTER_ERROR")

        duration_ms = (time.time() - start_time) * 1000
        status_report = SourceStatusReport(
            source_name=self.source_name,
            status=status,
            requested=True,
            result_count=len(results),
            unique_result_count=len(results),
            pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
            has_more=False,  # Single-page product list
            error_code=error_code,
            error_message=error_msg,
            duration_ms=duration_ms
        )
        metrics = SourceExecutionMetrics(
            source_name=self.source_name,
            requested_result_count=limit,
            returned_result_count=len(results),
            unique_result_count=len(results),
            duplicate_count=0,
            pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
            pagination_availability=False,
            request_count=1,
            cache_hit=False,
            duration_ms=duration_ms,
            status=status,
            error_code=error_code,
            error_message=error_msg
        )
        return results[:limit], status_report, metrics


# ==============================================================================
# 7. GOOGLE PLACES / BUSINESS ADAPTER
# ==============================================================================

class GooglePlacesAdapter(BaseSourceAdapter):
    """
    Google Places API New integration.
    Preserves:
    - place IDs, addresses, business categories, phone numbers and websites.
    - Strictly maintains verification status: 'POTENTIAL_GOOGLE_PLACE'.
    - A discovered Places business is not automatically marked as VERIFIED.
    """
    def __init__(self):
        super().__init__("google_places")

    def is_configured(self) -> bool:
        from app.services.google_places_service import GooglePlacesService
        svc = GooglePlacesService()
        return svc.is_configured()

    def build_queries(self, query: str, taxonomy_context: Optional[Dict[str, Any]] = None) -> List[str]:
        clean = query.strip()
        if not clean:
            clean = "building materials"
        
        city = taxonomy_context.get("city") if taxonomy_context else None
        state = taxonomy_context.get("state") if taxonomy_context else None
        loc_parts = [p.strip() for p in [city, state] if p and p.strip()]
        loc_str = ", ".join(loc_parts)
        
        clean_lower = clean.lower()
        queries = []
        if any(term in clean_lower for term in ["brick", "block", "laterite", "porotherm", "wirecut", "masonry", "cseb"]):
            if loc_str:
                queries.append(f"{clean} suppliers in {loc_str}")
                queries.append(f"{clean} dealers and manufacturers in {loc_str}")
                queries.append(f"{clean} manufacturers and distributors in {loc_str}")
            else:
                queries.append(f"{clean} suppliers")
                queries.append(f"{clean} dealers and manufacturers")
        elif any(term in clean_lower for term in ["steel", "tmt", "rebar"]):
            if loc_str:
                queries.append(f"{clean} distributors and dealers in {loc_str}")
                queries.append(f"{clean} steel dealers in {loc_str}")
            else:
                queries.append(f"{clean} distributors and dealers")
                queries.append(f"{clean} steel dealers")
        elif any(term in clean_lower for term in ["cement", "mortar", "concrete"]):
            if loc_str:
                queries.append(f"{clean} dealers and manufacturers in {loc_str}")
                queries.append(f"{clean} suppliers in {loc_str}")
            else:
                queries.append(f"{clean} dealers and manufacturers")
                queries.append(f"{clean} suppliers")
        elif any(term in clean_lower for term in ["paint", "coating", "finish"]):
            if loc_str:
                queries.append(f"{clean} suppliers in {loc_str}")
                queries.append(f"{clean} dealers in {loc_str}")
            else:
                queries.append(f"{clean} suppliers")
                queries.append(f"{clean} dealers")
        elif any(term in clean_lower for term in ["window", "door", "glass", "aluminium", "aluminum", "upvc"]):
            if loc_str:
                queries.append(f"{clean} manufacturers and dealers in {loc_str}")
                queries.append(f"{clean} fabricators in {loc_str}")
            else:
                queries.append(f"{clean} manufacturers and dealers")
                queries.append(f"{clean} fabricators")
        else:
            if loc_str:
                queries.append(f"{clean} suppliers in {loc_str}")
                queries.append(f"{clean} dealers and distributors in {loc_str}")
            else:
                queries.append(f"{clean} suppliers")
                queries.append(f"{clean} dealers and distributors")
        return queries

    def fetch(
        self,
        query: str,
        cursor: Optional[str] = None,
        limit: int = 50,
        dry_run: bool = False,
        taxonomy_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[NormalizedDiscoveryResult], SourceStatusReport, SourceExecutionMetrics]:
        start_time = time.time()
        queries = self.build_queries(query, taxonomy_context)
        primary_query = queries[0]

        if not self.is_configured():
            duration_ms = (time.time() - start_time) * 1000
            status_report = SourceStatusReport(
                source_name=self.source_name,
                status=SourceStatusEnum.NOT_CONFIGURED,
                requested=True,
                error_message="GOOGLE_PLACES_API_KEY environment variable is not configured.",
                duration_ms=duration_ms
            )
            metrics = SourceExecutionMetrics(
                source_name=self.source_name,
                requested_result_count=limit,
                status=SourceStatusEnum.NOT_CONFIGURED,
                error_message="Google Places API not configured.",
                duration_ms=duration_ms
            )
            return [], status_report, metrics

        # In synchronous context, call Places connector or SocialCrawl business fallback
        from app.services.google_places_service import GooglePlacesService
        svc = GooglePlacesService()
        results: List[NormalizedDiscoveryResult] = []
        error_code: Optional[str] = None
        error_msg: Optional[str] = None
        status = SourceStatusEnum.SUCCESS

        city = taxonomy_context.get("city") if taxonomy_context else None
        lat = taxonomy_context.get("lat") if taxonomy_context else None
        lon = taxonomy_context.get("lon") if taxonomy_context else None

        try:
            import inspect
            raw_res = None
            maybe_coro = svc.search_nearby_suppliers(material_type=query, lat=lat, lon=lon, city=city)
            if inspect.isawaitable(maybe_coro):
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = None
                if loop and loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        raw_res = executor.submit(lambda: asyncio.run(maybe_coro)).result(timeout=10)
                else:
                    raw_res = asyncio.run(maybe_coro)
            else:
                raw_res = maybe_coro

            if raw_res and isinstance(raw_res, dict):
                if raw_res.get("error"):
                    status, error_code, error_msg = classify_adapter_exception(Exception(str(raw_res["error"])), "PLACES_API_ERROR")
                else:
                    places = raw_res.get("places", [])
                    for p in places:
                        place_id = str(p.get("google_place_id") or p.get("place_id") or "")
                        maps_url = p.get("google_maps_url") or p.get("maps_url") or ""

                        norm_item = NormalizedDiscoveryResult(
                            source=self.source_name,
                            source_result_id=place_id or None,
                            original_url=maps_url,
                            canonical_url=maps_url,
                            title=p.get("name") or f"{query.title()} Supplier",
                            description=p.get("stock_confirmation") or f"Trade supplier located in {p.get('address', city)}.",
                            phone=p.get("phone"),
                            website=p.get("website"),
                            address=p.get("address"),
                            location=p.get("address") or city,
                            business_category=p.get("business_type") or "Building Material Supplier",
                            published_at=None,
                            retrieved_at=datetime.utcnow().isoformat(),
                            # Classification
                            content_type="supplier_business",
                            discovery_classification=DiscoveryClassificationEnum.SUPPLIER,
                            metadata_classification=MetadataClassificationEnum.SUPPLIER_PROFILE,
                            # Taxonomy
                            category=taxonomy_context.get("category") if taxonomy_context else None,
                            subcategory=taxonomy_context.get("subcategory") if taxonomy_context else None,
                            item=taxonomy_context.get("item") if taxonomy_context else None,
                            source_attribution="Google Places",
                            discovery_query=primary_query,
                            # Strictly POTENTIAL_GOOGLE_PLACE (never false VERIFIED)
                            verification_status="POTENTIAL_GOOGLE_PLACE",
                            provenance=ProvenanceEnum.LIVE_DISCOVERY,
                            media_status=MediaStatusEnum.TEXT_DISCUSSION,
                            source_metadata={
                                "rating": p.get("rating"),
                                "user_ratings_total": p.get("user_ratings_total"),
                                "is_potential": True
                            }
                        )
                        norm_item.relevant_tabs = determine_relevant_discovery_tabs(norm_item)
                        results.append(norm_item)

                    if not places:
                        status = SourceStatusEnum.EMPTY
            elif raw_res is None or (isinstance(raw_res, (list, dict)) and not raw_res):
                status = SourceStatusEnum.EMPTY
            else:
                status = SourceStatusEnum.FAILED
                error_code = "MALFORMED_UPSTREAM_RESPONSE"
                error_msg = f"Unexpected upstream response format: expected dict, received {type(raw_res).__name__}."

        except Exception as e:
            logger.error(f"[GooglePlacesAdapter] Execution error: {e}")
            status, error_code, error_msg = classify_adapter_exception(e, "PLACES_ADAPTER_ERROR")

        duration_ms = (time.time() - start_time) * 1000
        status_report = SourceStatusReport(
            source_name=self.source_name,
            status=status,
            requested=True,
            result_count=len(results),
            unique_result_count=len(results),
            pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
            has_more=False,
            error_code=error_code,
            error_message=error_msg,
            duration_ms=duration_ms
        )
        metrics = SourceExecutionMetrics(
            source_name=self.source_name,
            requested_result_count=limit,
            returned_result_count=len(results),
            unique_result_count=len(results),
            duplicate_count=0,
            pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
            pagination_availability=False,
            request_count=1,
            cache_hit=False,
            duration_ms=duration_ms,
            status=status,
            error_code=error_code,
            error_message=error_msg
        )
        return results[:limit], status_report, metrics

    async def fetch_async(
        self,
        query: str,
        cursor: Optional[str] = None,
        limit: int = 50,
        dry_run: bool = False,
        taxonomy_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[NormalizedDiscoveryResult], SourceStatusReport, SourceExecutionMetrics]:
        """
        Natively awaits GooglePlacesService without ThreadPoolExecutor or asyncio.run.
        """
        start_time = time.time()
        queries = self.build_queries(query, taxonomy_context)
        primary_query = queries[0]

        if not self.is_configured():
            duration_ms = (time.time() - start_time) * 1000
            status_report = SourceStatusReport(
                source_name=self.source_name,
                status=SourceStatusEnum.NOT_CONFIGURED,
                requested=True,
                error_message="GOOGLE_PLACES_API_KEY environment variable is not configured.",
                duration_ms=duration_ms
            )
            metrics = SourceExecutionMetrics(
                source_name=self.source_name,
                requested_result_count=limit,
                status=SourceStatusEnum.NOT_CONFIGURED,
                error_message="Google Places API not configured.",
                duration_ms=duration_ms
            )
            return [], status_report, metrics

        from app.services.google_places_service import GooglePlacesService
        svc = GooglePlacesService()
        results: List[NormalizedDiscoveryResult] = []
        error_code: Optional[str] = None
        error_msg: Optional[str] = None
        status = SourceStatusEnum.SUCCESS

        city = taxonomy_context.get("city") if taxonomy_context else None
        lat = taxonomy_context.get("lat") if taxonomy_context else None
        lon = taxonomy_context.get("lon") if taxonomy_context else None

        try:
            import inspect
            res = svc.search_nearby_suppliers(material_type=query, lat=lat, lon=lon, city=city)
            if inspect.isawaitable(res):
                raw_res = await res
            else:
                raw_res = res

            if raw_res and isinstance(raw_res, dict):
                if raw_res.get("error"):
                    status, error_code, error_msg = classify_adapter_exception(Exception(str(raw_res["error"])), "PLACES_API_ERROR")
                else:
                    places = raw_res.get("places", [])
                    for p in places:
                        place_id = str(p.get("google_place_id") or p.get("place_id") or "")
                        maps_url = p.get("google_maps_url") or p.get("maps_url") or ""

                        norm_item = NormalizedDiscoveryResult(
                            source=self.source_name,
                            source_result_id=place_id or None,
                            original_url=maps_url,
                            canonical_url=maps_url,
                            title=p.get("name") or f"{query.title()} Supplier",
                            description=p.get("stock_confirmation") or f"Trade supplier located in {p.get('address', city)}.",
                            phone=p.get("phone"),
                            website=p.get("website"),
                            address=p.get("address"),
                            location=p.get("address") or city,
                            business_category=p.get("business_type") or "Building Material Supplier",
                            published_at=None,
                            retrieved_at=datetime.utcnow().isoformat(),
                            # Classification
                            content_type="supplier_business",
                            discovery_classification=DiscoveryClassificationEnum.SUPPLIER,
                            metadata_classification=MetadataClassificationEnum.SUPPLIER_PROFILE,
                            # Taxonomy
                            category=taxonomy_context.get("category") if taxonomy_context else None,
                            subcategory=taxonomy_context.get("subcategory") if taxonomy_context else None,
                            item=taxonomy_context.get("item") if taxonomy_context else None,
                            source_attribution="Google Places",
                            discovery_query=primary_query,
                            # Strictly POTENTIAL_GOOGLE_PLACE (never false VERIFIED)
                            verification_status="POTENTIAL_GOOGLE_PLACE",
                            provenance=ProvenanceEnum.LIVE_DISCOVERY,
                            media_status=MediaStatusEnum.TEXT_DISCUSSION,
                            source_metadata={
                                "rating": p.get("rating"),
                                "user_ratings_total": p.get("user_ratings_total"),
                                "is_potential": True
                            }
                        )
                        norm_item.relevant_tabs = determine_relevant_discovery_tabs(norm_item)
                        results.append(norm_item)

                    if not places:
                        status = SourceStatusEnum.EMPTY
            elif raw_res is None or (isinstance(raw_res, (list, dict)) and not raw_res):
                status = SourceStatusEnum.EMPTY
            else:
                status = SourceStatusEnum.FAILED
                error_code = "MALFORMED_UPSTREAM_RESPONSE"
                error_msg = f"Unexpected upstream response format: expected dict, received {type(raw_res).__name__}."

        except Exception as e:
            logger.error(f"[GooglePlacesAdapter] Async execution error: {e}")
            status, error_code, error_msg = classify_adapter_exception(e, "PLACES_ADAPTER_ERROR")

        duration_ms = (time.time() - start_time) * 1000
        status_report = SourceStatusReport(
            source_name=self.source_name,
            status=status,
            requested=True,
            result_count=len(results),
            unique_result_count=len(results),
            pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
            has_more=False,
            error_code=error_code,
            error_message=error_msg,
            duration_ms=duration_ms
        )
        metrics = SourceExecutionMetrics(
            source_name=self.source_name,
            requested_result_count=limit,
            returned_result_count=len(results),
            unique_result_count=len(results),
            duplicate_count=0,
            pages_fetched=1 if status != SourceStatusEnum.FAILED else 0,
            pagination_availability=False,
            request_count=1,
            cache_hit=False,
            duration_ms=duration_ms,
            status=status,
            error_code=error_code,
            error_message=error_msg
        )
        return results[:limit], status_report, metrics

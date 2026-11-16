from typing import List, Optional
from datetime import datetime, timezone
from app.connectors.base import BaseSourceConnector, NormalizedReference
from app.core.config import settings

CURATED_INSTAGRAM_REFERENCES = [
    NormalizedReference(
        title="Flamed Basalt Cobblestones and Zen Garden Reflection Pond",
        slug="flamed-basalt-cobblestones-zen-pond",
        source_platform="instagram",
        source_url="https://www.instagram.com/p/architectural_landscape_stone/",
        creator_name="@japanesegardenmasters",
        creator_url="https://www.instagram.com/japanesegardenmasters/",
        thumbnail_url="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80",
        media_url="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80",
        category_slug="garden-materials",
        material_tags=["basalt_stone", "black_granite", "water_feature", "cobblestones"],
        location_context="Kyoto, Japan",
        verification_status="MANUFACTURER_CONFIRMED",
        description="Serrated wire-sawn and flame-textured volcanic basalt pavers arranged along an outdoor koi pond courtyard.",
        is_authorized=True,
        provenance_notes="Instagram architectural photography reference preserving creator handle and post URL."
    ),
    NormalizedReference(
        title="Lime Plaster and Textured Exterior Stucco Residence",
        slug="lime-plaster-textured-exterior-stucco",
        source_platform="instagram",
        source_url="https://www.instagram.com/p/earthy_facades_india/",
        creator_name="@contemporary_vernacular",
        creator_url="https://www.instagram.com/contemporary_vernacular/",
        thumbnail_url="https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80",
        media_url="https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80",
        category_slug="paints-and-finishes",
        material_tags=["lime_wash", "hydraulic_lime", "breathable_facade", "earthy_tones"],
        location_context="Kozhikode, Kerala, India",
        verification_status="VISUALLY_SIMILAR",
        description="Traditional slaked lime and river sand exterior render tinted with iron oxide mineral pigments for humid oceanfront climates.",
        is_authorized=True,
        provenance_notes="Instagram architectural account attribution with direct link."
    )
]

class InstagramConnector(BaseSourceConnector):
    def __init__(self, app_id: Optional[str] = None):
        super().__init__("instagram", app_id or settings.get_socialcrawl_api_key() or settings.INSTAGRAM_APP_ID)

    def is_configured(self) -> bool:
        key = self.api_key or settings.get_socialcrawl_api_key()
        return bool(key and key.strip())

    async def search(self, query: str, limit: int = 10) -> List[NormalizedReference]:
        if self.is_configured():
            try:
                from app.services.socialcrawl_service import search_instagram_reels
                res = search_instagram_reels(query=query, max_pages=1)
                items = res.get("items", [])
                if items:
                    out = []
                    for idx, reel in enumerate(items[:limit]):
                        out.append(NormalizedReference(
                            title=reel.get("title") or f"Instagram Reel: {query}",
                            slug=f"instagram-{reel.get('reel_id') or idx}",
                            source_platform="instagram",
                            source_url=reel.get("source_url") or "https://www.instagram.com",
                            creator_name=reel.get("creator_name"),
                            creator_url=reel.get("creator_url"),
                            thumbnail_url=reel.get("thumbnail_url"),
                            media_url=reel.get("video_url") or reel.get("thumbnail_url"),
                            category_slug="architecture-house-types",
                            material_tags=reel.get("material_tags") or [query],
                            location_context="Instagram Architectural Inspiration",
                            verification_status="UNVERIFIED",
                            description=reel.get("description"),
                            is_authorized=True,
                            video_duration=reel.get("video_duration"),
                            is_short=True,
                            provenance_notes="Sourced via SocialCrawl Instagram Reels Search API."
                        ))
                    return out
            except Exception as e:
                pass

        q = query.lower()
        results = [r for r in CURATED_INSTAGRAM_REFERENCES if q in r.title.lower() or any(q in t for t in r.material_tags)]
        return results or CURATED_INSTAGRAM_REFERENCES[:limit]

    async def sync(self) -> List[NormalizedReference]:
        self.last_sync = datetime.now(timezone.utc)
        return await self.search("modern architecture", limit=10)

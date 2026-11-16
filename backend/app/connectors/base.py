from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

class NormalizedReference(BaseModel):
    title: str
    slug: str
    source_platform: str
    source_url: str
    creator_name: Optional[str] = None
    creator_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    media_url: Optional[str] = None
    video_embed_id: Optional[str] = None
    category_slug: Optional[str] = None
    material_tags: List[str] = []
    location_context: Optional[str] = None
    verification_status: str = "UNVERIFIED"
    description: Optional[str] = None
    is_authorized: bool = True
    provenance_notes: Optional[str] = None
    video_duration: Optional[str] = None
    is_short: bool = False
    source_domain: Optional[str] = None
    colors_and_finishes: Optional[str] = None
    image_attribution: Optional[str] = None

    def __contains__(self, key: str) -> bool:
        if key == "video_id":
            return bool(self.video_embed_id)
        return hasattr(self, key)

    def __getitem__(self, key: str):
        if key == "video_id":
            return self.video_embed_id
        return getattr(self, key)

class BaseSourceConnector(ABC):
    def __init__(self, platform_name: str, api_key: Optional[str] = None):
        self.platform_name = platform_name
        self.api_key = api_key
        self.last_sync: Optional[datetime] = None

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[NormalizedReference]:
        """Search the external platform for architectural references."""
        pass

    @abstractmethod
    async def sync(self) -> List[NormalizedReference]:
        """Perform periodic synchronization of curated architectural references."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if real API credentials are configured, False for demo mode."""
        pass

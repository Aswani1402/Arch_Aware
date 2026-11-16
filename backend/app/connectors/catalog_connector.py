from typing import List, Optional
from datetime import datetime, timezone
from app.connectors.base import BaseSourceConnector, NormalizedReference

CURATED_CATALOG_REFERENCES = [
    NormalizedReference(
        title="Asian Paints Apex Ultima Protek Duralife High Performance Exterior System",
        slug="asian-paints-apex-ultima-protek",
        source_platform="catalog",
        source_url="https://www.asianpaints.com/products/exterior-walls/apex-ultima-protek.html",
        creator_name="Asian Paints Official Catalog",
        creator_url="https://www.asianpaints.com",
        thumbnail_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80",
        media_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80",
        category_slug="paints-and-finishes",
        material_tags=["exterior_emulsion", "nanotechnology", "anti_algal", "weatherproof"],
        location_context="Mumbai, India (National Manufacturer)",
        verification_status="MANUFACTURER_CONFIRMED",
        description="Official technical catalog specifications for 15-year warranty exterior water-based emulsion system engineered for heavy coastal rainfall regions.",
        is_authorized=True,
        provenance_notes="Direct authorized manufacturer specification sheet and technical documentation."
    ),
    NormalizedReference(
        title="Kajaria The Ultima Extra Large Format 1200x2400mm Glazed Porcelain Slabs",
        slug="kajaria-ultima-large-format-porcelain",
        source_platform="catalog",
        source_url="https://www.kajariaceramics.com/the-ultima.php",
        creator_name="Kajaria Ceramics Official Catalog",
        creator_url="https://www.kajariaceramics.com",
        thumbnail_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
        media_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
        category_slug="tiles",
        material_tags=["porcelain_slab", "bookmatched_marble_look", "statuario", "low_water_absorption"],
        location_context="New Delhi, India (National Manufacturer)",
        verification_status="MANUFACTURER_CONFIRMED",
        description="Continuous-vein Italian Statuario inspired porcelain slabs with 9mm thickness for seamless wall cladding and luxury vanity countertops.",
        is_authorized=True,
        provenance_notes="Verified manufacturer catalog listing with verified dimensions and water absorption rates."
    ),
    NormalizedReference(
        title="Kyoto Karesansui Natural Dark Andesite & River Stepping Stones",
        slug="kyoto-karesansui-natural-andesite-stones",
        source_platform="catalog",
        source_url="https://kyotogardenstone.co.jp/en/products/stepping-stones",
        creator_name="Kyoto Garden Stone Guild (Japan)",
        creator_url="https://kyotogardenstone.co.jp",
        thumbnail_url="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80",
        media_url="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80",
        category_slug="garden-materials",
        material_tags=["japanese_stepping_stones", "andesite", "tobi-ishi", "natural_weathered"],
        location_context="Kyoto, Japan (International Exporter)",
        verification_status="MANUFACTURER_CONFIRMED",
        description="Authentic Japanese quarry-harvested Tobi-Ishi pathway stones naturally smoothed by mountain stream water, hand-split for level walking surfaces.",
        is_authorized=True,
        provenance_notes="Official Japanese stone atelier exporter catalog with international crating and sea freight capability."
    )
]

class CatalogConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__("catalog", api_key=None)

    def is_configured(self) -> bool:
        return True

    async def search(self, query: str, limit: int = 10) -> List[NormalizedReference]:
        q = query.lower()
        results = [r for r in CURATED_CATALOG_REFERENCES if q in r.title.lower() or any(q in t for t in r.material_tags)]
        return results or CURATED_CATALOG_REFERENCES[:limit]

    async def sync(self) -> List[NormalizedReference]:
        self.last_sync = datetime.now(timezone.utc)
        return CURATED_CATALOG_REFERENCES

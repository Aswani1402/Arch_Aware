from app.connectors.base import BaseSourceConnector, NormalizedReference
from app.connectors.youtube_connector import YouTubeConnector
from app.connectors.reddit_connector import RedditConnector
from app.connectors.pinterest_connector import PinterestConnector
from app.connectors.instagram_connector import InstagramConnector
from app.connectors.catalog_connector import CatalogConnector

CONNECTOR_REGISTRY = {
    "youtube": YouTubeConnector,
    "reddit": RedditConnector,
    "pinterest": PinterestConnector,
    "instagram": InstagramConnector,
    "catalog": CatalogConnector
}

def get_connector(platform: str) -> BaseSourceConnector:
    cls = CONNECTOR_REGISTRY.get(platform.lower())
    if not cls:
        raise ValueError(f"Unknown source platform connector: {platform}")
    return cls()

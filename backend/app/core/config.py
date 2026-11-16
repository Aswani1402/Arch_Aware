import json
import os
from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import Any, List

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ROOT_DIR = os.path.dirname(_BACKEND_DIR)
_DEFAULT_DB_PATH = os.path.join(_BACKEND_DIR, "architect_ai.db").replace("\\", "/")
_ENV_FILES = (os.path.join(_BACKEND_DIR, ".env"), os.path.join(_ROOT_DIR, ".env"), ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "MATERIQ"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "architect-ai-super-secret-dev-key-change-in-prod-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database: Absolute path to ensure consistency regardless of CWD
    DATABASE_URL: str = f"sqlite:///{_DEFAULT_DB_PATH}"

    # CORS (reference default aligned with NIVORA_CORS_ORIGINS in main.py)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # External APIs (Optional, with graceful fallback demo modes)
    GOOGLE_MAPS_API_KEY: str = ""
    GOOGLE_PLACES_API_KEY: str = ""
    YOUTUBE_API_KEY: str = ""
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    INSTAGRAM_APP_ID: str = ""
    PINTEREST_API_KEY: str = ""
    SOCIALCRAWL_API_KEY: str = ""
    SOCIALCRAWL_MAX_PAGES: int = 10
    SOCIALCRAWL_TIMEOUT_S: int = 25
    SOCIALCRAWL_MAX_RETRIES: int = 3
    SOCIALCRAWL_CACHE_TTL_SECONDS: int = 3600
    PINTEREST_MAX_PAGES: int = 10
    PINTEREST_TIMEOUT_S: int = 14
    PINTEREST_MAX_RETRIES: int = 3
    LLM_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_API_BASE_URL: str = ""
    LLM_MODEL: str = "gemini-1.5-flash"

    # Image Search Providers (Separate from Google Places vendor search)
    GOOGLE_CUSTOM_SEARCH_API_KEY: str = ""
    GOOGLE_CUSTOM_SEARCH_CX: str = ""
    GOOGLE_SEARCH_API_KEY: str = ""
    GOOGLE_SEARCH_CX: str = ""
    CUSTOM_SEARCH_API_KEY: str = ""
    CUSTOM_SEARCH_CX: str = ""
    UNSPLASH_ACCESS_KEY: str = ""
    PEXELS_API_KEY: str = ""

    def get_places_api_key(self) -> str:
        return self.GOOGLE_PLACES_API_KEY or self.GOOGLE_MAPS_API_KEY or ""

    def get_google_image_search_key(self) -> str:
        return self.CUSTOM_SEARCH_API_KEY or self.GOOGLE_CUSTOM_SEARCH_API_KEY or self.GOOGLE_SEARCH_API_KEY or ""

    def get_google_image_search_cx(self) -> str:
        return self.CUSTOM_SEARCH_CX or self.GOOGLE_CUSTOM_SEARCH_CX or self.GOOGLE_SEARCH_CX or ""

    def get_unsplash_key(self) -> str:
        return self.UNSPLASH_ACCESS_KEY or ""

    def get_llm_api_key(self) -> str:
        return self.LLM_API_KEY or self.GEMINI_API_KEY or self.OPENAI_API_KEY or ""

    def get_youtube_api_key(self) -> str:
        return self.YOUTUBE_API_KEY or ""

    def get_socialcrawl_api_key(self) -> str:
        return os.environ.get("SOCIALCRAWL_API_KEY") or self.SOCIALCRAWL_API_KEY or ""

    # Global Discovery Kill Switch
    DISCOVERY_KILL_SWITCH: bool = False

    # Sourcing Settings
    DEFAULT_SEARCH_RADIUS_KM: float = 25.0
    FALLBACK_RADIUS_LEVEL_1_KM: float = 50.0
    FALLBACK_RADIUS_LEVEL_2_KM: float = 100.0

    # Demo Mode
    DEMO_MODE: bool = True

    # Trusted Reverse Proxies (for X-Forwarded-For verification)
    TRUSTED_PROXIES: List[str] = []

    @field_validator("TRUSTED_PROXIES", mode="before")
    @classmethod
    def _parse_trusted_proxies(cls, value: Any) -> List[str]:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            if raw.startswith("["):
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        return [str(v).strip() for v in parsed if str(v).strip()]
                except Exception:
                    pass
            return [entry.strip() for entry in raw.split(",") if entry.strip()]
        if isinstance(value, (list, tuple, set)):
            return [str(v).strip() for v in value if str(v).strip()]
        return []

    class Config:
        env_file = _ENV_FILES
        case_sensitive = True
        extra = "allow"

settings = Settings()

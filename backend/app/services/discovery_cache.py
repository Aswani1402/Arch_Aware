"""
Nivora — Bounded Cache-First Discovery Store (Phase 3 / Phase 9)

Thread-safe, bounded TTL + LRU cache for UnifiedDiscoveryResponse objects.
Prevents repeated provider credit consumption for identical normalized queries.
"""

from collections import OrderedDict
import threading
import time
from typing import Any, Dict, List, Optional, Tuple


class BoundedDiscoveryCache:
    """Thread-safe bounded LRU + TTL cache for discovery responses."""

    def __init__(self, max_entries: int = 256, ttl_seconds: int = 3600):
        self.max_entries = max(1, max_entries)
        self.ttl_seconds = max(1, ttl_seconds)
        self._store: OrderedDict[str, Tuple[float, Dict[str, Any]]] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    @staticmethod
    def build_key(
        query: str,
        sources: Optional[List[str]] = None,
        tab: str = "all",
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        material: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        page: int = 1,
        page_size: int = 30,
    ) -> str:
        norm_q = " ".join((query or "").strip().lower().split())
        norm_sources = ",".join(sorted({s.strip().lower() for s in (sources or ["all"]) if s and s.strip()}))
        parts = [
            f"q={norm_q}",
            f"src={norm_sources}",
            f"tab={(tab or 'all').strip().lower()}",
            f"cat={(category or '').strip().lower()}",
            f"sub={(subcategory or '').strip().lower()}",
            f"mat={(material or '').strip().lower()}",
            f"city={(city or '').strip().lower()}",
            f"state={(state or '').strip().lower()}",
            f"p={page}",
            f"ps={page_size}",
        ]
        return "|".join(parts)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        now = time.time()
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self._misses += 1
                return None
            expires_at, payload = entry
            if now >= expires_at:
                del self._store[key]
                self._misses += 1
                return None
            self._store.move_to_end(key)
            self._hits += 1
            return payload

    def set(self, key: str, payload: Dict[str, Any]) -> None:
        now = time.time()
        with self._lock:
            # Prune expired entries opportunistically
            expired_keys = [k for k, (exp, _) in self._store.items() if now >= exp]
            for ek in expired_keys:
                del self._store[ek]

            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = (now + self.ttl_seconds, payload)

            while len(self._store) > self.max_entries:
                self._store.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
            self._hits = 0
            self._misses = 0

    def stats(self) -> Dict[str, Any]:
        now = time.time()
        with self._lock:
            expired_keys = [k for k, (exp, _) in self._store.items() if now >= exp]
            for ek in expired_keys:
                del self._store[ek]
            return {
                "entries": len(self._store),
                "max_entries": self.max_entries,
                "ttl_seconds": self.ttl_seconds,
                "hits": self._hits,
                "misses": self._misses,
            }


discovery_cache = BoundedDiscoveryCache()


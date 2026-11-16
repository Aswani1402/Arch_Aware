"""
Nivora — Interactive Discovery Request Guard & Provider Budget Manager
Phase 5B — Stage 2.1

Architectural Design & Safety Invariants:
1. DiscoveryRequestGuard:
   - Server-side sliding-window rate-limiting for interactive user searches.
   - Dual-tier enforcement: Authenticated user limit vs. Anonymous client fallback.
   - Cryptographically safe client identification:
     * Does NOT trust arbitrary client-supplied headers (e.g. X-User-Id, arbitrary query params).
     * Uses cryptographically verified user identity (e.g. from validated JWT session).
     * For unauthenticated requests, hashes client IP with a cryptographic salt (SHA-256).
     * Never stores raw IP addresses or personally identifiable information (PII) in memory.
   - Strict pre-execution enforcement: checks and blocks requests BEFORE any provider calls occur.
   - Blocked requests consume zero provider credits.

2. ProviderBudgetManager:
   - Enforces per-request and cumulative provider credit safety caps.
   - Tracks projected and actual provider credit consumption:
     * Pinterest: 1 credit per request
     * Instagram Reels: 1 credit per page
     * YouTube: 1 credit per page
     * Reddit: 1 credit per page
     * Google Shopping: 5 credits per product search
     * Google Places: 5 credits (SocialCrawl) / 0 credits (Places API)
   - Enforces limits:
     * max_sources_per_request (default: 7)
     * max_expansions_per_source (default: 3)
     * max_pagination_depth (default: 2)
     * max_credits_per_request (default: 20)
     * daily_interactive_credit_cap (default: 500)
   - Preserves background crawler budget (MAX_DAILY_API_CALLS = 12 in daily_collection_service.py).

3. Multi-Worker & In-Memory Limitations:
   - Operates in-process using memory structures (collections.deque).
   - In multi-worker Uvicorn deployments (--workers N), each worker maintains an independent sliding window.
   - State does not persist across server restarts or worker recycling.
   - Production multi-worker parity requires an external shared store (e.g. Redis).
"""

import time
import os
import hashlib
import logging
import threading
import ipaddress
from collections import deque
from typing import Dict, List, Optional, Tuple, Any, Union
from pydantic import BaseModel, ConfigDict, Field
from starlette.requests import Request
from app.core.config import settings

logger = logging.getLogger("architect_ai.discovery_guard")


def _parse_trusted_networks(
    trusted_proxies: Optional[List[str]] = None,
) -> List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
    """Parses configured trusted proxy IPs or CIDR ranges into ipaddress network objects."""
    raw_entries = trusted_proxies if trusted_proxies is not None else getattr(settings, "TRUSTED_PROXIES", [])
    networks: List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]] = []
    for entry in raw_entries or []:
        if not entry or not isinstance(entry, str):
            continue
        cleaned = entry.strip()
        if not cleaned:
            continue
        try:
            networks.append(ipaddress.ip_network(cleaned, strict=False))
        except ValueError:
            logger.warning(f"[DiscoveryRequestGuard] Ignoring invalid trusted proxy entry: {cleaned!r}")
    return networks


def _normalize_ip(value: Optional[str]) -> Optional[str]:
    """Validates an IPv4/IPv6 address string and returns its canonical representation, or None if invalid."""
    if not value or not isinstance(value, str):
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    try:
        return ipaddress.ip_address(cleaned).compressed
    except ValueError:
        return None


def _is_trusted_proxy_ip(
    ip_str: str,
    trusted_networks: List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]],
) -> bool:
    """Returns True if the validated IP address falls within any configured trusted proxy network."""
    if not trusted_networks:
        return False
    try:
        ip_obj = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return any(ip_obj in net for net in trusted_networks)


def resolve_client_ip(
    peer_ip: Optional[str],
    forwarded_for: Optional[str] = None,
    trusted_proxies: Optional[List[str]] = None,
) -> str:
    """
    Resolves the verified client IP at the HTTP/ASGI boundary.
    - X-Forwarded-For is trusted ONLY when the immediate connection peer_ip matches TRUSTED_PROXIES.
    - When peer_ip is untrusted (or TRUSTED_PROXIES is empty), forwarding headers are ignored completely.
    - When trusted, parses X-Forwarded-For right-to-left, validating IP syntax for every hop,
      rejecting malformed chains cleanly by falling back to peer_ip, and returning the rightmost
      non-trusted client hop.
    """
    valid_peer = _normalize_ip(peer_ip) or "127.0.0.1"
    if not forwarded_for:
        return valid_peer

    trusted_networks = _parse_trusted_networks(trusted_proxies)
    if not _is_trusted_proxy_ip(valid_peer, trusted_networks):
        return valid_peer

    raw_hops = [h.strip() for h in forwarded_for.split(",")]
    if not raw_hops or any(not h for h in raw_hops):
        return valid_peer

    validated_hops: List[str] = []
    for hop in raw_hops:
        norm_hop = _normalize_ip(hop)
        if norm_hop is None:
            # Malformed IP anywhere in X-Forwarded-For -> treat header as untrusted
            return valid_peer
        validated_hops.append(norm_hop)

    # Walk right-to-left skipping configured trusted proxies to find true origin hop
    for hop_ip in reversed(validated_hops):
        if not _is_trusted_proxy_ip(hop_ip, trusted_networks):
            return hop_ip

    return validated_hops[0]


def extract_verified_client_ip(
    request: Request,
    trusted_proxies: Optional[List[str]] = None,
) -> str:
    """
    Extracts and validates client IP from an ASGI/FastAPI Request using the actual peer address
    (request.client.host) and TRUSTED_PROXIES configuration.
    """
    peer_ip = request.client.host if getattr(request, "client", None) else None
    forwarded_for = request.headers.get("x-forwarded-for") if getattr(request, "headers", None) is not None else None
    return resolve_client_ip(peer_ip=peer_ip, forwarded_for=forwarded_for, trusted_proxies=trusted_proxies)


class GuardDecision(BaseModel):
    """
    Result of a rate limit or budget inspection.
    """
    allowed: bool
    status_code: int = 200
    retry_after_seconds: Optional[int] = None
    reason: Optional[str] = None
    client_identifier: str = ""
    remaining_quota: int = 0

    model_config = ConfigDict(from_attributes=True)


class DiscoveryRequestGuard:
    """
    Sliding-window in-memory request guard for interactive discovery searches.
    Guarantees that unauthenticated and authenticated users cannot flood external APIs.
    """

    def __init__(
        self,
        user_rate_limit: int = 60,      # 60 requests per hour for authenticated users
        anon_rate_limit: int = 15,      # 15 requests per hour for anonymous clients
        window_seconds: int = 3600,     # 1 hour window
        salt: Optional[str] = None
    ):
        self.user_rate_limit = user_rate_limit
        self.anon_rate_limit = anon_rate_limit
        self.window_seconds = window_seconds
        self._salt = salt or os.environ.get("DISCOVERY_GUARD_SALT") or "nivora_guard_secret_salt_2026"
        # Mapping: client_identifier -> deque of request timestamps
        self._request_history: Dict[str, deque] = {}
        self._lock = threading.Lock()
        self._check_counter = 0

    def derive_client_identifier(
        self,
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        is_authenticated: bool = False
    ) -> Tuple[str, bool]:
        """
        Derives an anonymized, collision-resistant client identifier.
        Rules:
        - Authenticated user IDs are prefixed with 'usr_' and hashed.
        - Anonymous IPs are salted and hashed; raw IP is NEVER stored.
        - Client-supplied user_id without verified authentication is treated as anonymous.
        """
        if is_authenticated and user_id and str(user_id).strip():
            clean_uid = str(user_id).strip()
            hashed_uid = hashlib.sha256(f"user:{clean_uid}:{self._salt}".encode()).hexdigest()[:16]
            return f"usr_{hashed_uid}", True

        # Fallback to anonymous client IP
        raw_ip = (client_ip or "127.0.0.1").strip()
        # Extract leftmost hop if comma-separated string is passed directly, then validate IP syntax
        candidate_ip = raw_ip.split(",")[0].strip()
        clean_ip = _normalize_ip(candidate_ip) or "127.0.0.1"
        hashed_ip = hashlib.sha256(f"ip:{clean_ip}:{self._salt}".encode()).hexdigest()[:16]
        return f"anon_{hashed_ip}", False

    def _evict_stale_keys(self, cutoff: float, active_key: str) -> None:
        """Removes expired client keys to prevent unbounded dictionary growth."""
        stale_keys = [
            k for k, dq in self._request_history.items()
            if k != active_key and (not dq or dq[-1] < cutoff)
        ]
        for k in stale_keys:
            del self._request_history[k]

    def check_request(
        self,
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        is_authenticated: bool = False
    ) -> GuardDecision:
        """
        Evaluates whether the client request is permitted under the sliding window limit.
        Does NOT record the request if blocked (prevents lockout loops).
        Thread-safe and periodically evicts stale keys.
        """
        client_key, is_auth = self.derive_client_identifier(
            user_id=user_id,
            client_ip=client_ip,
            is_authenticated=is_authenticated
        )
        limit = self.user_rate_limit if is_auth else self.anon_rate_limit
        now = time.time()
        cutoff = now - self.window_seconds

        with self._lock:
            self._check_counter += 1
            if self._check_counter % 50 == 0 or len(self._request_history) > 500:
                self._evict_stale_keys(cutoff, client_key)

            if client_key not in self._request_history:
                self._request_history[client_key] = deque()

            history = self._request_history[client_key]

            # Prune timestamps older than the sliding window
            while history and history[0] < cutoff:
                history.popleft()

            current_count = len(history)

            if current_count >= limit:
                oldest = history[0]
                retry_after = max(1, int(self.window_seconds - (now - oldest)))
                logger.warning(
                    f"[DiscoveryRequestGuard] Rate limit exceeded for {client_key} "
                    f"({current_count}/{limit} reqs). Retry after {retry_after}s."
                )
                return GuardDecision(
                    allowed=False,
                    status_code=429,
                    retry_after_seconds=retry_after,
                    reason=f"Interactive discovery rate limit exceeded. Retry after {retry_after} seconds.",
                    client_identifier=client_key,
                    remaining_quota=0
                )

            # Request is allowed; record the timestamp
            history.append(now)
            remaining = max(0, limit - len(history))

            return GuardDecision(
                allowed=True,
                status_code=200,
                retry_after_seconds=None,
                reason=None,
                client_identifier=client_key,
                remaining_quota=remaining
            )

    def check_http_request(
        self,
        request: Request,
        current_user: Any = None,
        trusted_proxies: Optional[List[str]] = None,
    ) -> GuardDecision:
        """
        HTTP/ASGI boundary entry point for interactive discovery request rate limiting.
        - Derives client IP from request.client.host and validates X-Forwarded-For ONLY against TRUSTED_PROXIES.
        - Derives authenticated identity ONLY from a verified current_user object (ignoring X-User-Id or arbitrary headers).
        """
        verified_ip = extract_verified_client_ip(request, trusted_proxies=trusted_proxies)
        user_id = None
        is_authenticated = False
        if current_user is not None:
            raw_uid = getattr(current_user, "id", None) or getattr(current_user, "email", None)
            if raw_uid is not None and str(raw_uid).strip():
                user_id = str(raw_uid).strip()
                is_authenticated = True
        return self.check_request(
            user_id=user_id,
            client_ip=verified_ip,
            is_authenticated=is_authenticated,
        )

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "user_rate_limit_per_hour": self.user_rate_limit,
                "anon_rate_limit_per_hour": self.anon_rate_limit,
                "window_seconds": self.window_seconds,
                "tracked_clients": len(self._request_history),
                "storage": "in_memory_process_local",
            }

    def reset(self) -> None:
        """Clears in-memory history (for tests and isolation)."""
        with self._lock:
            self._request_history.clear()
            self._check_counter = 0


class ProviderBudgetManager:
    """
    Enforces per-request and cumulative provider credit limits.
    Prevents single discovery queries from triggering excessive upstream API calls.
    """

    PROVIDER_CREDIT_COSTS: Dict[str, int] = {
        "pinterest": 1,
        "instagram": 1,
        "youtube": 1,
        "reddit": 1,
        "google_search": 0,       # 0 credit (Custom Search API or unconfigured)
        "google_shopping": 5,     # 5 credits per SocialCrawl product search
        "google_places": 0,       # 0 credit (direct Google Places Platform API)
        "x": 0,                   # Disabled source
        "twitter": 0,             # Disabled source
    }

    def __init__(
        self,
        max_sources_per_request: int = 7,
        max_expansions_per_source: int = 3,
        max_pagination_depth: int = 2,
        max_credits_per_request: int = 20,
        daily_interactive_credit_cap: int = 500
    ):
        self.max_sources_per_request = max_sources_per_request
        self.max_expansions_per_source = max_expansions_per_source
        self.max_pagination_depth = max_pagination_depth
        self.max_credits_per_request = max_credits_per_request
        self.daily_interactive_credit_cap = daily_interactive_credit_cap

        self._daily_credits_used = 0
        self._daily_reset_timestamp = time.time()
        self._lock = threading.Lock()

    def calculate_projected_credits(self, sources: List[str]) -> int:
        """
        Calculates the projected credit cost for a discovery request across sources.
        """
        total = 0
        for src in sources:
            norm_src = src.lower().strip()
            total += self.PROVIDER_CREDIT_COSTS.get(norm_src, 1)
        return total

    def check_budget(
        self,
        sources: List[str],
        page: int = 1,
        query_expansions: int = 1,
        dry_run: bool = False,
        cached: bool = False,
        reserve: bool = False
    ) -> Tuple[bool, Optional[str], int]:
        """
        Checks whether the requested parameters exceed request or daily budget caps.
        When reserve=True and not dry_run/cached, atomically reserves projected credits under lock
        to prevent concurrent overspending.
        Dry-run and cache hits consume 0 credits.
        Returns: (allowed: bool, reason: Optional[str], projected_credits: int)
        """
        with self._lock:
            from app.core.config import settings
            if getattr(settings, "DISCOVERY_KILL_SWITCH", False) or os.environ.get("DISCOVERY_KILL_SWITCH", "0") in ("1", "true", "True"):
                return False, "Global discovery kill switch is active. Outbound provider requests are halted.", 0

            # Daily reset check (24h window)
            now = time.time()
            if now - self._daily_reset_timestamp >= 86400:
                self._daily_credits_used = 0
                self._daily_reset_timestamp = now

            # Pagination depth check
            if page < 1 or page > self.max_pagination_depth:
                msg = f"Requested page {page} exceeds maximum pagination depth of {self.max_pagination_depth}."
                logger.warning(f"[ProviderBudgetManager] {msg}")
                return False, msg, 0

            # Query expansion check
            if query_expansions < 1 or query_expansions > self.max_expansions_per_source:
                msg = f"Requested {query_expansions} query expansions per source, exceeding valid range [1, {self.max_expansions_per_source}]."
                logger.warning(f"[ProviderBudgetManager] {msg}")
                return False, msg, 0

            # Source count limit
            if len(sources) > self.max_sources_per_request:
                msg = f"Request requested {len(sources)} sources, exceeding maximum limit of {self.max_sources_per_request}."
                logger.warning(f"[ProviderBudgetManager] {msg}")
                return False, msg, 0

            if dry_run or cached:
                return True, None, 0

            projected = self.calculate_projected_credits(sources) * max(1, query_expansions)

            # Per-request credit limit
            if projected > self.max_credits_per_request:
                msg = f"Projected credit cost {projected} exceeds max per-request limit of {self.max_credits_per_request}."
                logger.warning(f"[ProviderBudgetManager] {msg}")
                return False, msg, projected

            # Daily cumulative credit cap
            if self._daily_credits_used + projected > self.daily_interactive_credit_cap:
                msg = f"Daily interactive credit cap of {self.daily_interactive_credit_cap} reached."
                logger.warning(f"[ProviderBudgetManager] {msg}")
                return False, msg, projected

            if reserve and projected > 0:
                self._daily_credits_used += projected

            return True, None, projected

    def record_consumption(self, credits_used: int) -> None:
        """
        Records actual credits consumed following execution when not pre-reserved.
        """
        with self._lock:
            self._daily_credits_used += max(0, credits_used)

    def release_credits(self, credits: int) -> None:
        """
        Releases pre-reserved credits when execution did not occur (e.g., cancelled before adapter call).
        Never decreases daily consumption below zero.
        """
        with self._lock:
            self._daily_credits_used = max(0, self._daily_credits_used - max(0, credits))

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            now = time.time()
            if now - self._daily_reset_timestamp >= 86400:
                self._daily_credits_used = 0
                self._daily_reset_timestamp = now
            return {
                "daily_interactive_credit_cap": self.daily_interactive_credit_cap,
                "daily_credits_used": self._daily_credits_used,
                "daily_credits_remaining": max(0, self.daily_interactive_credit_cap - self._daily_credits_used),
                "max_credits_per_request": self.max_credits_per_request,
                "max_sources_per_request": self.max_sources_per_request,
                "max_pagination_depth": self.max_pagination_depth,
                "max_expansions_per_source": self.max_expansions_per_source,
            }

    def reset(self) -> None:
        """Resets credit accounting (for tests)."""
        with self._lock:
            self._daily_credits_used = 0
            self._daily_reset_timestamp = time.time()


# Global Singleton Instances
discovery_request_guard = DiscoveryRequestGuard()
provider_budget_manager = ProviderBudgetManager()


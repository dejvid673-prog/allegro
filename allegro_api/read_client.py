"""Fixed-verb, fixed-endpoint read-only Allegro client.

This module deliberately has no OAuth issuance, token persistence, MCP tools or
write API. Tokens are supplied server-side by a separately authenticated broker.
Its configured seller_id is only an assertion until checked with Allegro.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import (
    HTTPRedirectHandler, Request, build_opener,
)
from uuid import UUID

HOSTS = {
    "production": "https://api.allegro.pl",
    "sandbox": "https://api.allegro.pl.allegrosandbox.pl",
}
MEDIA_TYPE = "application/vnd.allegro.public.v1+json"
SCOPE_OFFERS = "allegro:api:sale:offers:read"
SCOPE_ORDERS = "allegro:api:orders:read"
SCOPE_SHIPMENTS = "allegro:api:shipments:read"
MAX_BODY_BYTES = 1024 * 1024
MAX_LIMIT = 100
MAX_OFFSET = 1_000_000
DEFAULT_TIMEOUT = 10.0


class ConnectionAccessDenied(PermissionError):
    """Actor is not allowed to use the specified connection."""


class MissingScope(PermissionError):
    """Connection lacks the required READ scope."""


class ReadApiError(Exception):
    """Sanitized error; never includes request, Authorization or raw body."""

    def __init__(self, status: int | None):
        self.status = status
        label = f"HTTP {status}" if status is not None else "transport or payload error"
        super().__init__(f"Allegro READ failed ({label})")


class RateLimited(ReadApiError):
    def __init__(self, retry_after_seconds: int | None):
        super().__init__(429)
        self.retry_after_seconds = retry_after_seconds


@dataclass(frozen=True)
class Connection:
    connection_id: str
    seller_id: str
    environment: str
    allowed_actors: frozenset[str]
    scopes: frozenset[str]


@dataclass(frozen=True)
class Response:
    status: int
    headers: Mapping[str, str]
    body: bytes


class ConnectionRegistry:
    """Server-side allowlist; passed actor IDs must come from trusted auth."""

    def __init__(self, connections: list[Connection]):
        self._by_id: dict[str, Connection] = {}
        for item in connections:
            if not isinstance(item, Connection):
                raise ValueError("connection must be a Connection")
            if (not isinstance(item.connection_id, str) or not item.connection_id.strip()
                    or len(item.connection_id) > 100
                    or not isinstance(item.seller_id, str) or not item.seller_id.strip()
                    or item.environment not in HOSTS
                    or not isinstance(item.allowed_actors, frozenset)
                    or not item.allowed_actors
                    or any(not isinstance(a, str) or not a.strip() for a in item.allowed_actors)
                    or not isinstance(item.scopes, frozenset)
                    or any(not isinstance(s, str) or not s for s in item.scopes)):
                raise ValueError("invalid server-side Allegro connection configuration")
            if item.connection_id in self._by_id:
                raise ValueError("duplicate connection_id")
            self._by_id[item.connection_id] = item

    def authorize(self, connection_id: str, actor_id: str, scope: str) -> Connection:
        if not isinstance(connection_id, str) or not isinstance(actor_id, str):
            raise ConnectionAccessDenied("Connection access denied")
        entry = self._by_id.get(connection_id)
        if entry is None or actor_id not in entry.allowed_actors:
            raise ConnectionAccessDenied("Connection access denied")
        if scope not in entry.scopes:
            raise MissingScope("Required read scope not granted")
        return entry


class _BlockRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, url):
        return None


class UrllibGetTransport:
    """Actual HTTPS transport; refuses HTTP redirects and response overread.

    Nothing is sent until a caller explicitly calls a typed client method.
    """

    def __init__(self):
        self._opener = build_opener(_BlockRedirects())

    def __call__(self, url: str, headers: Mapping[str, str], timeout: float) -> Response:
        request = Request(url, headers=dict(headers), method="GET")
        try:
            with self._opener.open(request, timeout=timeout) as result:
                body = result.read(MAX_BODY_BYTES + 1)
                return Response(int(result.status), dict(result.headers.items()), body)
        except HTTPError as exc:
            # Error contents deliberately ignored: they may contain account data.
            return Response(int(exc.code), dict(exc.headers.items()) if exc.headers else {}, b"")
        except (URLError, OSError, TimeoutError) as exc:
            raise ReadApiError(None) from None


def _safe_limit_offset(limit: int, offset: int) -> None:
    if type(limit) is not int or not 1 <= limit <= MAX_LIMIT:
        raise ValueError("limit must be a positive integer <= 100")
    if type(offset) is not int or not 0 <= offset <= MAX_OFFSET:
        raise ValueError("offset must be an integer between 0 and 1000000")


def _offer_id(value: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{1,32}", value) is None:
        raise ValueError("offer_id must contain only decimal digits")
    return value


def _order_uuid(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("order_id must be a UUID string")
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ValueError("order_id must be a UUID string") from None
    if str(parsed) != value:
        raise ValueError("order_id must be a canonical lowercase UUID")
    return value


def _retry_after(headers: Mapping[str, str]) -> int | None:
    # Any malformed, unsafe or too-long hint stays unspecified; do not sleep.
    for name, value in headers.items():
        if name.casefold() != "retry-after":
            continue
        if isinstance(value, str) and re.fullmatch(r"[0-9]{1,4}", value):
            number = int(value)
            return number if 0 <= number <= 3600 else None
    return None


class AllegroReadClient:
    """GET-only high-level resource methods; do not publish raw responses to LLM."""

    def __init__(
        self,
        registry: ConnectionRegistry,
        token_provider: Callable[[str], str],
        transport: Callable[[str, Mapping[str, str], float], Response] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        if not isinstance(registry, ConnectionRegistry) or not callable(token_provider):
            raise ValueError("read client requires server-side registry and token broker")
        if type(timeout) not in (int, float) or not 0 < timeout <= 15:
            raise ValueError("invalid HTTP timeout")
        if transport is not None and not callable(transport):
            raise ValueError("invalid transport")
        self._registry = registry
        self._get_token = token_provider
        self._transport = transport if transport is not None else UrllibGetTransport()
        self._timeout = float(timeout)

    def _read(
        self, connection_id: str, actor_id: str, scope: str, path: str,
        params: dict[str, int] | None = None,
    ) -> dict:
        # Authorize before touching token provider or network.
        entry = self._registry.authorize(connection_id, actor_id, scope)
        token: str
        try:
            token = self._get_token(entry.connection_id)
        except Exception:
            raise ReadApiError(None) from None
        if not isinstance(token, str) or not token or any(ch.isspace() for ch in token):
            raise ReadApiError(None)
        url = HOSTS[entry.environment] + path
        if params:
            url += "?" + urlencode(params)
        headers = {
            "Authorization": "Bearer " + token,
            "Accept": MEDIA_TYPE,
            "Accept-Language": "pl-PL",
            "User-Agent": "7DEJV-Allegro-ReadOnly/0.2",
        }
        try:
            result = self._transport(url, headers, self._timeout)
        except Exception:
            raise ReadApiError(None) from None
        if not isinstance(result, Response) or type(result.status) is not int:
            raise ReadApiError(None)
        if result.status == 429:
            raise RateLimited(_retry_after(result.headers))
        if result.status != 200:
            raise ReadApiError(result.status)
        if not isinstance(result.body, bytes) or len(result.body) > MAX_BODY_BYTES:
            raise ReadApiError(None)
        try:
            obj = json.loads(result.body)
        except (ValueError, UnicodeDecodeError):
            raise ReadApiError(None) from None
        if not isinstance(obj, dict):
            raise ReadApiError(None)
        return obj

    def offers(self, connection_id: str, actor_id: str, limit: int = 20, offset: int = 0) -> dict:
        _safe_limit_offset(limit, offset)
        return self._read(connection_id, actor_id, SCOPE_OFFERS, "/sale/offers",
                          {"limit": limit, "offset": offset})

    def offer(self, connection_id: str, actor_id: str, offer_id: str) -> dict:
        return self._read(connection_id, actor_id, SCOPE_OFFERS,
                          "/sale/product-offers/" + _offer_id(offer_id))

    def orders(self, connection_id: str, actor_id: str, limit: int = 20, offset: int = 0) -> dict:
        _safe_limit_offset(limit, offset)
        return self._read(connection_id, actor_id, SCOPE_ORDERS, "/order/checkout-forms",
                          {"limit": limit, "offset": offset})

    def order(self, connection_id: str, actor_id: str, order_id: str) -> dict:
        return self._read(connection_id, actor_id, SCOPE_ORDERS,
                          "/order/checkout-forms/" + _order_uuid(order_id))

    def order_events(self, connection_id: str, actor_id: str, limit: int = 20) -> dict:
        _safe_limit_offset(limit, 0)
        return self._read(connection_id, actor_id, SCOPE_ORDERS,
                          "/order/events", {"limit": limit})

    def delivery_proposals(self, connection_id: str, actor_id: str, order_id: str) -> dict:
        return self._read(connection_id, actor_id, SCOPE_SHIPMENTS,
                          "/shipment-management/delivery-proposals/" + _order_uuid(order_id))

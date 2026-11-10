"""Trusted-host wrapper for account-bound, redacted Allegro READ.

NOT an MCP server. The authenticated orchestration backend must bind actor_id,
connection_id and verified seller identity. No user/LLM-supplied 'verified' flag
is allowed, and no account is trusted by default. Never export raw client tools.
"""
from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from allegro_api.agent_projection import (
    project_offer, project_offers_page, project_order, project_orders_page,
)
from allegro_api.read_client import (
    AllegroReadClient, ConnectionRegistry, SCOPE_OFFERS, SCOPE_ORDERS,
)


class SellerIdentityNotVerified(PermissionError):
    """Generic denial; intentionally no account identifiers or user data."""


class SafeAllegroReadService:
    """In-process projected READ service, blocked until trusted identity binding."""

    def __init__(
        self,
        client: AllegroReadClient,
        registry: ConnectionRegistry,
        *,
        authenticated_actor: str,
        verified_sellers: Mapping[str, str] | None = None,
    ):
        if not isinstance(client, AllegroReadClient):
            raise ValueError("AllegroReadClient required")
        if not isinstance(registry, ConnectionRegistry):
            raise ValueError("ConnectionRegistry required")
        if client._registry is not registry:
            raise ValueError("mismatched connection registry")
        if (not isinstance(authenticated_actor, str)
                or not authenticated_actor or len(authenticated_actor) > 120):
            raise ValueError("trusted authenticated actor required")
        verified = {} if verified_sellers is None else dict(verified_sellers)
        if any(not isinstance(k, str) or not isinstance(v, str)
               or not k or not v for k, v in verified.items()):
            raise ValueError("invalid trusted seller mapping")
        self._client = client
        self._registry = registry
        self._actor = authenticated_actor
        self._verified = MappingProxyType(verified)

    def _guard(self, connection_id: str, scope: str) -> None:
        # First enforce actor permissions, then check trusted seller identity.
        conn = self._registry.authorize(connection_id, self._actor, scope)
        if self._verified.get(connection_id) != conn.seller_id:
            raise SellerIdentityNotVerified("Allegro connection not verified")

    def offers(self, connection_id: str, limit: int = 20, offset: int = 0) -> dict:
        self._guard(connection_id, SCOPE_OFFERS)
        return project_offers_page(self._client.offers(connection_id, self._actor, limit, offset))

    def offer(self, connection_id: str, offer_id: str) -> dict:
        self._guard(connection_id, SCOPE_OFFERS)
        return project_offer(self._client.offer(connection_id, self._actor, offer_id))

    def orders(self, connection_id: str, limit: int = 20, offset: int = 0) -> dict:
        self._guard(connection_id, SCOPE_ORDERS)
        return project_orders_page(self._client.orders(connection_id, self._actor, limit, offset))

    def order(self, connection_id: str, order_id: str) -> dict:
        self._guard(connection_id, SCOPE_ORDERS)
        return project_order(self._client.order(connection_id, self._actor, order_id))

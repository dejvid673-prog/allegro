"""Seller identity check against authenticated Allegro GET /me.

Only a trusted host may call this with authenticated_actor. Raw GET /me contains
e-mail/NIP/company details and must never enter MCP prompts, logs or LLM output.
No token issuance, persistence, OAuth flow or account connection is performed.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from allegro_api.read_client import (
    AllegroReadClient, ConnectionRegistry, SCOPE_PROFILE,
)


class SellerVerificationFailed(PermissionError):
    """Generic account mismatch; external response is never echoed."""


@dataclass(frozen=True)
class VerifiedSellerIdentity:
    connection_id: str
    seller_id: str
    environment: str


def verify_connection_seller(
    client: AllegroReadClient,
    registry: ConnectionRegistry,
    connection_id: str,
    authenticated_actor: str,
) -> VerifiedSellerIdentity:
    """Compare declared seller with exact account owning the OAuth token.

    Production use requires authenticated actor identity from an independent
    trusted host, a token broker and a consented OAuth session. Never pass actor
    identity or server claims from an LLM/tool argument.
    """
    if (not isinstance(client, AllegroReadClient)
            or not isinstance(registry, ConnectionRegistry)
            or client._registry is not registry):
        raise ValueError("trusted client and same connection registry required")
    # Enforce actor + profile READ scope before token provider / network.
    connection = registry.authorize(connection_id, authenticated_actor, SCOPE_PROFILE)
    # GET /me is the only API read needed to prove identity.
    raw = client.me(connection_id, authenticated_actor)
    seen = raw.get("id")
    if (not isinstance(seen, str)
            or re.fullmatch(r"[0-9]{1,32}", seen) is None
            or seen != connection.seller_id):
        raise SellerVerificationFailed("Allegro seller identity mismatch")
    return VerifiedSellerIdentity(
        connection_id=connection.connection_id,
        seller_id=seen,
        environment=connection.environment,
    )

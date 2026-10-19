"""Local stdio MCP server exposing read-only knowledge and offline business audit.

No HTTP listener, tokens, seller-account requests or marketplace write tools.
Offline business preflight inspects only caller-supplied hypothetical data.
"""
from __future__ import annotations

from mcp.server import MCPServer

from allegro_domain.assortment import audit_assortment_snapshot
from allegro_domain.costs import audit_cost_snapshot
from allegro_domain.market import compare_market_snapshots
from allegro_domain.repricing import propose_price_change
from allegro_domain.shipment_monitor import audit_shipment_events
from allegro_domain.shipments import audit_shipment_plan

from allegro_mcp.offline_catalog import (
    catalog_status,
    find_read_endpoints,
    get_read_endpoint,
)

mcp = MCPServer("7DEJV Allegro Offline Operator (preflight only)")


@mcp.tool()
def allegro_catalog_status() -> dict:
    """Report the age and provenance of the locally stored Allegro API snapshot."""
    return catalog_status()


@mcp.tool()
def allegro_find_read_endpoints(query: str, limit: int = 10) -> dict:
    """Find GET operations documented in the OLD local snapshot; no network access."""
    return find_read_endpoints(query, limit)


@mcp.tool()
def allegro_get_read_endpoint(path: str) -> dict:
    """Inspect one exact GET operation; this does NOT fetch seller account data."""
    return get_read_endpoint(path)


@mcp.tool()
def allegro_shipment_preflight_offline(order: dict, parcels: list[dict]) -> dict:
    """Validate a supplied hypothetical parcel plan; NEVER create a shipment."""
    return audit_shipment_plan(order, parcels)


@mcp.tool()
def allegro_cost_preflight_offline(cost_snapshot: dict) -> dict:
    """Validate supplied NET costs and simulate margin; NEVER change offer prices."""
    return audit_cost_snapshot(cost_snapshot)


@mcp.tool()
def allegro_assortment_audit_offline(offers: list[dict], product_master: list[dict]) -> dict:
    """Compare per-account offer price, stock and GTIN with supplied expectations. No writes."""
    return audit_assortment_snapshot(offers, product_master)


@mcp.tool()
def allegro_price_change_proposal_offline(
    current_offer: dict, proposed_price_gross: str, projected_cost_snapshot: dict
) -> dict:
    """Simulate a single price change using a fully documented NEW NET cost snapshot; no write."""
    return propose_price_change(current_offer, proposed_price_gross, projected_cost_snapshot)


@mcp.tool()
def allegro_market_comparison_offline(
    own_offers: list[dict], competitor_observations: list[dict]
) -> dict:
    """Compare declared, caller-supplied market observations. Never scrape or reprice."""
    return compare_market_snapshots(own_offers, competitor_observations)


@mcp.tool()
def allegro_shipment_events_audit_offline(
    shipments: list[dict], as_of: str | None = None
) -> dict:
    """Audit declared label, first-scan and COD evidence. No real carrier confirmation."""
    return audit_shipment_events(shipments, as_of)


if __name__ == "__main__":
    mcp.run()  # stdio only; do not expose over unauthenticated HTTP

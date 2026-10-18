"""Local stdio MCP server exposing only the pinned Allegro knowledge base.

No HTTP listener, tokens, seller-account requests or marketplace write tools.
Offline business preflight inspects only caller-supplied hypothetical data.
"""
from __future__ import annotations

from mcp.server import MCPServer

from allegro_domain.costs import audit_cost_snapshot
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


if __name__ == "__main__":
    mcp.run()  # stdio only; do not expose over unauthenticated HTTP

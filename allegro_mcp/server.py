"""Local stdio MCP server exposing only the pinned Allegro knowledge base.

No HTTP listener, tokens, seller-account API requests or marketplace write tools.
"""
from __future__ import annotations

from mcp.server import MCPServer

from allegro_mcp.offline_catalog import (
    catalog_status,
    find_read_endpoints,
    get_read_endpoint,
)

mcp = MCPServer("7DEJV Allegro Knowledge (offline)")


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


if __name__ == "__main__":
    mcp.run()  # stdio only; do not expose over unauthenticated HTTP

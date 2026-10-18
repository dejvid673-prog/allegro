"""Protocol smoke test using the official MCP Python v2 SDK, in-memory client (five offline tools)."""
import asyncio

from mcp import Client

from allegro_mcp.server import mcp


async def main() -> None:
    async with Client(mcp) as client:
        names = {tool.name for tool in (await client.list_tools()).tools}
        expected = {
            "allegro_catalog_status",
            "allegro_find_read_endpoints",
            "allegro_get_read_endpoint",
            "allegro_shipment_preflight_offline",
            "allegro_cost_preflight_offline",
        }
        assert names == expected, f"unexpected tool exposure: {names}"
        result = await client.call_tool("allegro_catalog_status", {})
        assert not result.is_error, "offline MCP catalog tool failed"
        match = await client.call_tool(
            "allegro_find_read_endpoints", {"query": "offer", "limit": 2}
        )
        assert not match.is_error, "offline endpoint search failed"
        sample_order = {
            "status": "READY_FOR_PROCESSING",
            "items": [{"sku": "chalk", "kind": "CHALK_BAG", "quantity": 1}],
            "service": {"verified": True, "max_weight_grams": 31500, "supports_cod": True},
            "cod_required": False, "shipment_status": "NOT_CREATED",
        }
        packed = [{"items": [{"sku": "chalk", "quantity": 1}],
                   "packed_weight_grams": 24200, "verified": True}]
        shipping = await client.call_tool(
            "allegro_shipment_preflight_offline", {"order": sample_order, "parcels": packed}
        )
        assert not shipping.is_error, "offline shipment validation failed"
        from allegro_domain.costs import COST_FIELDS
        zero_cost = {
            "currency": "PLN", "taxBasis": "NET", "complete": True,
            "salesPriceGross": "123.00", "salesRevenueNet": "100.00",
            "minimumContributionMarginNet": "10.00",
            **{key: {"value": "0.00", "status": "ZERO_CONFIRMED",
                     "sourceRef": "offline-fixture", "effectiveAt": "2026-10-18T10:00:00Z"}
               for key in COST_FIELDS},
        }
        cost_result = await client.call_tool(
            "allegro_cost_preflight_offline", {"cost_snapshot": zero_cost}
        )
        assert not cost_result.is_error, "offline margin calculation failed"
    print("MCP in-memory protocol smoke PASS: exactly 5 offline tools (3 catalog, 2 domain)")


if __name__ == "__main__":
    asyncio.run(main())

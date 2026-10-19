"""Protocol smoke test using the official MCP Python v2 SDK, in-memory client (nine offline tools)."""
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
            "allegro_assortment_audit_offline",
            "allegro_price_change_proposal_offline",
            "allegro_market_comparison_offline",
            "allegro_shipment_events_audit_offline",
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
        assortment = await client.call_tool(
            "allegro_assortment_audit_offline", {
                "offers": [{
                    "connection_id": "a", "offer_id": "100", "sku": "chalk",
                    "gtin": "5901234123457", "stock": 2,
                    "price_gross": "123.00", "status": "ACTIVE",
                }],
                "product_master": [{
                    "sku": "chalk", "gtin": "5901234123457",
                    "expected_stock_by_connection": {"a": 2},
                    "expected_price_by_connection": {"a": "123.00"},
                }],
            }
        )
        assert not assortment.is_error, "offline assortment tool failed"
        proposal = await client.call_tool(
            "allegro_price_change_proposal_offline", {
                "current_offer": {
                    "connection_id": "a", "offer_id": "100", "sku": "chalk",
                    "price_gross": "120.00",
                },
                "proposed_price_gross": "123.00",
                "projected_cost_snapshot": zero_cost,
            }
        )
        assert not proposal.is_error, "offline repricing proposal failed"
        from datetime import datetime, timezone
        market = await client.call_tool(
            "allegro_market_comparison_offline", {
                "own_offers": [{
                    "connection_id": "a", "offer_id": "100", "sku": "chalk",
                    "gtin": "5901234123457", "net_weight_grams": 25000,
                    "units_per_offer": 1, "condition": "NEW",
                    "price_gross": "55.00", "shipping_gross": "12.00",
                }],
                "competitor_observations": [{
                    "offer_ref": "export-1", "source_type": "USER_PROVIDED_EXPORT",
                    "source_ref": "fixture", "observed_at": datetime.now(timezone.utc).isoformat(),
                    "gtin": "5901234123457", "net_weight_grams": 25000,
                    "units_per_offer": 1, "condition": "NEW",
                    "price_gross": "54.00", "shipping_gross": "12.00",
                }],
            }
        )
        assert not market.is_error, "offline market comparison failed"
        shipping_audit = await client.call_tool(
            "allegro_shipment_events_audit_offline", {
                "shipments": [{
                    "connection_id": "a", "order_id": "order", "shipment_id": "ship",
                    "tracking_number": "tracking", "status": "LABEL_CREATED",
                    "label_created_at": "2026-10-18T10:00:00Z", "first_scan_at": None,
                    "first_scan_verified": False, "cod_required": False,
                }],
                "as_of": "2026-10-19T12:00:00Z",
            }
        )
        assert not shipping_audit.is_error, "offline shipment event audit failed"
    print("MCP in-memory protocol smoke PASS: exactly 9 offline tools (3 catalog, 6 domain)")


if __name__ == "__main__":
    asyncio.run(main())

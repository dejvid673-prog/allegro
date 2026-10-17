"""Protocol smoke test using the official MCP Python v2 SDK, in-memory client."""
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
        }
        assert names == expected, f"unexpected tool exposure: {names}"
        result = await client.call_tool("allegro_catalog_status", {})
        assert not result.is_error, "offline MCP catalog tool failed"
        match = await client.call_tool(
            "allegro_find_read_endpoints", {"query": "offer", "limit": 2}
        )
        assert not match.is_error, "offline endpoint search failed"
    print("MCP in-memory protocol smoke PASS: exactly 3 offline knowledge tools")


if __name__ == "__main__":
    asyncio.run(main())

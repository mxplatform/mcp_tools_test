import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

from app import tools

async def test_mcp_server(url):
    async with streamablehttp_client(url) as (reader, writer, session_id):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            tools = await session.list_tools()
            for key, value in tools:
                if key == "tools":
                    print("Available tools:")
                    for tool in value:
                        print(f"- {tool.name}")
                        if hasattr(tool, "inputSchema") and tool.inputSchema:
                            print("  Arguments:")
                            for arg, spec in tool.inputSchema.get("properties", {}).items():
                                print(f"    - {arg}: {spec.get('type', 'unknown')} ")
asyncio.run(test_mcp_server("http://localhost:8080/mcp"))
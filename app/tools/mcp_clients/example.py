# from __future__ import annotations

# import asyncio

# from ..registry import get_registry
# from .client import MCPManager


# async def demo():
#     mgr = MCPManager()
#     await mgr.connect("serverA", url="https://mcp-a.example.com", token="TOKEN_A")
#     await mgr.connect("serverB", url="https://mcp-b.example.com", token="TOKEN_B")

#     registry = get_registry()
#     print("Registered tools:", registry.list_tools())

#     tool = registry.get_tool("serverA.some_tool")
#     if tool and getattr(tool, "ainvoke", None):
#         res = await tool.ainvoke({"param": 1})
#         print("remote result", res)


# if __name__ == "__main__":
#     asyncio.run(demo())

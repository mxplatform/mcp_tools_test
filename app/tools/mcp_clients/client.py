"""Minimal MCP client integration.

Manage multiple MCP server connections and register remote tools into
the global registry so they behave like local async tools.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

import mcp

from ..registry import get_registry
from .base import MCPClient, MCPTool


class MCPManager:
    """Manage connections to multiple MCP servers and register their tools.

    Usage:
        mgr = MCPManager()
        await mgr.connect("server-a", url="https://...", token="...")
        await mgr.connect("server-b", url=..., token=...)

    Each remote tool is registered in the global registry using the key
    "{server_id}.{tool_name}". Tools can be removed by calling
    `disconnect(server_id)` which unregisters the tools belonging to that
    server.
    """

    def __init__(self) -> None:
        """Create an empty MCPManager.

        _clients maps server_id to the SDK client instance. _registered maps
        server_id to the list of registered tool names in the global registry.
        """
        self._clients: Dict[str, Any] = {}
        self._registered: Dict[str, List[str]] = {}

    async def connect(self, server_id: str, url: str, token: Optional[str] = None) -> None:
        """Connect to an MCP server and register its tools.

        Args:
            server_id: Logical identifier for the server used to prefix tool names.
            url: Base URL of the MCP server.
            token: Optional authentication token passed to the SDK client.

        Raises:
            Any exception raised by the underlying SDK when creating a client
            will propagate to the caller.
        """
        if server_id in self._clients:
            await self._refresh_server(server_id)
            return

        client: MCPClient = (
            mcp.Client(base_url=url, token=token) if hasattr(mcp, "Client") else mcp.connect(url=url, token=token)
        )
        self._clients[server_id] = client
        await self._discover_register(server_id, client)

    async def _discover_register(self, server_id: str, client: Any) -> None:
        """Discover remote tools on `client` and register adapters.

        The method is intentionally permissive about the SDK shape: it
        supports list-like descriptors or objects with attributes. Registered
        tool names are prefixed with the `server_id` to avoid global collisions.
        """
        registry = get_registry()
        # Expect the SDK client to provide `list_tools()` which may be sync
        # or async and return an iterable of tool descriptors.
        maybe = client.list_tools()
        tool_list: List[Any]
        if asyncio.iscoroutine(maybe) or asyncio.isfuture(maybe):
            tool_list = await maybe
        else:
            tool_list = maybe

        registered_names: List[str] = []

        for t in tool_list:
            name = getattr(t, "name", None) or (t.get("name") if isinstance(t, dict) else None)
            desc = (
                str(getattr(t, "description", None) or (t.get("description") if isinstance(t, dict) else ""))
                or "(remote tool)"
            )
            call_attr = getattr(t, "call", None) or (t.get("call") if isinstance(t, dict) else None)
            if not name or not call_attr:
                continue

            tool = MCPTool(server_id=server_id, name=name, description=desc, call_func=call_attr)
            registry.register_tool(tool)
            registered_names.append(tool.name)

        self._registered[server_id] = registered_names

    async def _refresh_server(self, server_id: str) -> None:
        """Refresh the tool list for an already-connected server.

        This unregisters previously registered tools for the server and
        re-discovers the current set from the SDK client.
        """
        client = self._clients.get(server_id)
        if client is None:
            return
        await self.disconnect(server_id, keep_client=True)
        await self._discover_register(server_id, client)

    async def disconnect(self, server_id: str, keep_client: bool = False) -> None:
        """Unregister tools for a server and optionally close the SDK client.

        Args:
            server_id: Logical server id whose tools will be unregistered.
            keep_client: If True, keep the SDK client in the manager; otherwise
                attempt to close/disconnect it and remove it from the manager.
        """
        registry = get_registry()
        names = self._registered.get(server_id, [])
        for n in names:
            registry.unregister_tool(n)
        self._registered.pop(server_id, None)

        client = self._clients.get(server_id)
        if client and not keep_client:
            close = getattr(client, "close", None) or getattr(client, "disconnect", None)
            if callable(close):
                maybe = close()
                if asyncio.iscoroutine(maybe):
                    await maybe
            self._clients.pop(server_id, None)

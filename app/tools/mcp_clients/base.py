"""MCP tool adapter base.

Contains MCPTool, a small adapter that implements the project's
AsyncBaseTool interface for remote MCP-exposed tools. This file was
extracted from the original `client.py` to keep responsibilities
separated and make the adapter reusable.
"""

from __future__ import annotations

import asyncio
from typing import Any, Coroutine, Iterable, Protocol, runtime_checkable

from langchain.tools import StructuredTool

from ..protocols import AsyncBaseTool


@runtime_checkable
class MCPClient(Protocol):
    """Protocol describing the minimal MCP SDK client shape we expect.

    Implementations should provide a `list_tools()` method which returns
    either an iterable of tool descriptors or an awaitable resolving to one.
    A `close()` or `disconnect()` method is expected for cleanup.
    """

    def list_tools(self) -> Iterable[Any] | Coroutine[Any, Any, Iterable[Any]]:  # pragma: no cover - simple protocol
        ...

    def close(self) -> None:  # pragma: no cover - optional cleanup
        ...

    def disconnect(self) -> None:  # pragma: no cover - optional cleanup
        ...


class MCPTool(AsyncBaseTool):
    def __init__(self, server_id: str, name: str, description: str, call_func: Any):
        super().__init__(name=f"{server_id}.{name}", description=description)
        self.remote_name = name
        self.server_id = server_id
        self._call_func = call_func

    async def call_async(self, *args: Any, **kwargs: Any) -> Any:
        if asyncio.iscoroutinefunction(self._call_func):
            return await self._call_func(*args, **kwargs)
        return await asyncio.to_thread(self._call_func, *args, **kwargs)

    def get_langchain_tool(self) -> Any:
        return StructuredTool.from_function(name=self.name, description=self.description, func=self.call_async)

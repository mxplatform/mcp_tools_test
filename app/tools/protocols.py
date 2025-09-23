import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Protocol, runtime_checkable


@runtime_checkable
class Tool(Protocol):
    """Protocol defining the interface for all tools (sync and async)."""

    name: str
    description: str
    is_async: bool = False

    def get_langchain_tool(self) -> Any:
        """Return a LangChain compatible tool instance."""
        ...

    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        """Synchronous tool execution."""
        ...


class AsyncTool(Tool):
    """Protocol for async tools (MCP, API calls, etc.)."""

    is_async: bool = True

    async def ainvoke(self, *args: Any, **kwargs: Any) -> Any:
        """Async tool execution."""
        ...


class BaseTool(ABC):
    """Abstract base class for all tools."""

    def __init__(self, name: str, description: str, is_async: bool = False):
        self.name = name
        self.description = description
        self.is_async = is_async

    @abstractmethod
    def get_langchain_tool(self) -> Any:
        """Convert to LangChain tool format."""
        pass


class AsyncBaseTool(BaseTool):
    """Base class for async tools.

    If a synchronous callable is provided via `sync_func` the default
    call_async will run it inside an asyncio thread using asyncio.to_thread.
    If a subclass wants to provide a fully async implementation it can
    override call_async as usual.
    """

    def __init__(
        self, name: str, description: str, sync_func: Optional[Callable[..., Any]] = None, lc_tool: Optional[Any] = None
    ):
        super().__init__(name, description, is_async=True)
        # Optional synchronous function this adapter should run in a thread
        self._sync_func: Optional[Callable[..., Any]] = sync_func
        # Optional LangChain tool object to return from get_langchain_tool
        self._lc_tool: Optional[Any] = lc_tool

    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        """Default synchronous invoke: call provided sync function.

        Subclasses that provide a different sync entrypoint can override.
        """
        if self._sync_func is None:
            raise NotImplementedError("No sync function available")
        return self._sync_func(*args, **kwargs)

    async def ainvoke(self, *args: Any, **kwargs: Any) -> Any:
        """Default async invoke: delegate to call_async."""
        return await self.call_async(*args, **kwargs)

    async def call_async(self, *args: Any, **kwargs: Any) -> Any:
        """Default async implementation: run provided sync function in a thread.

        Raises NotImplementedError if no sync function was provided and the
        method isn't overridden by a subclass.
        """
        if self._sync_func is None:
            raise NotImplementedError("AsyncBaseTool.call_async not implemented and no sync_func provided")
        return await asyncio.to_thread(self._sync_func, *args, **kwargs)

    def get_langchain_tool(self) -> Any:
        """Return the provided LangChain tool object if set, otherwise raise.

        Implementations that produce LangChain tools should set lc_tool when
        instantiating AsyncBaseTool.
        """
        if self._lc_tool is not None:
            return self._lc_tool
        raise NotImplementedError("No LangChain tool available for this AsyncBaseTool")

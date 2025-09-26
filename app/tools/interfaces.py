from abc import ABC, abstractmethod
from typing import Any, Protocol, Type, runtime_checkable

from pydantic import BaseModel


@runtime_checkable
class Tool(Protocol):
    """Protocol defining the interface for all tools."""

    name: str
    description: str

    def invoke(self, **kwargs: Any) -> Any:
        """Synchronous tool execution."""
        ...

    def get_langchain_tool(self) -> Any:
        """Return a LangChain compatible tool instance."""
        ...


class BaseTool(Tool, ABC):
    """Abstract base class for synchronous tools."""

    def __init__(self, name: str, description: str, args_schema: Type[BaseModel]):
        self.name = name
        self.description = description
        self.args_schema = args_schema

    @abstractmethod
    def invoke(self, **kwargs: Any) -> Any:
        """Synchronous tool execution."""
        pass

    @abstractmethod
    def get_langchain_tool(self) -> Any:
        """Return a LangChain compatible tool instance."""
        pass

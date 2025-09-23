"""Decorators for selecting and registering tools.

These helpers are intentionally lightweight: they attach class-level
selection metadata and, in the case of `tool`, also register a tool
instance with the global registry. Storing the decorators in a separate
module keeps the registry implementation focused and avoids clutter.
"""
from typing import Callable, Type, TypeVar

from .protocols import Tool
from .registry import get_registry

T = TypeVar("T")


def tool(tool_instance: Tool) -> Callable[[Type[T]], Type[T]]:
    """Decorator to register a tool with a class.

    This registers the tool instance in the global registry and records the
    tool name on the decorated class under the `_selected_tools` attribute.
    """

    def decorator(cls: Type[T]) -> Type[T]:
        if not hasattr(cls, "_selected_tools"):
            setattr(cls, "_selected_tools", [])
        getattr(cls, "_selected_tools").append(tool_instance.name)
        get_registry().register_tool(tool_instance)
        return cls

    return decorator


def use_tools(*tool_names: str) -> Callable[[Type[T]], Type[T]]:
    """Decorator to select specific tools for a class.

    The decorator records the selected tool names on the class for later
    resolution by ToolSelector or other consumers.
    """

    def decorator(cls: Type[T]) -> Type[T]:
        if not hasattr(cls, "_selected_tools"):
            setattr(cls, "_selected_tools", [])
        getattr(cls, "_selected_tools").extend(tool_names)
        return cls

    return decorator


def use_group(group_name: str) -> Callable[[Type[T]], Type[T]]:
    """Decorator to select all tools in a group for a class."""

    def decorator(cls: Type[T]) -> Type[T]:
        if not hasattr(cls, "_selected_groups"):
            setattr(cls, "_selected_groups", [])
        getattr(cls, "_selected_groups").append(group_name)
        return cls

    return decorator


def use_sql_tools(*tool_names: str) -> Callable[[Type[T]], Type[T]]:
    """Convenience decorator for SQL tools."""
    return use_tools(*tool_names)


def use_analytics_tools(*tool_names: str) -> Callable[[Type[T]], Type[T]]:
    """Convenience decorator for analytics tools."""
    return use_tools(*tool_names)

from typing import Dict, List, Optional, Set, TypeVar

from .protocols import Tool

T = TypeVar("T")


class ToolRegistry:
    """Central registry for managing tools and tool groups.

    Attributes:
        _tools (Dict[str, Tool]): Registered tools by name.
        _groups (Dict[str, Set[str]]): Registered groups mapping group names to sets of tool names.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}
        self._groups: Dict[str, Set[str]] = {}

    def register_tool(self, tool_instance: Tool) -> None:
        """Register a tool instance.

        Args:
            tool_instance (Tool): The tool instance to register.
        """
        self._tools[tool_instance.name] = tool_instance

    def register_group(self, group_name: str, tool_names: List[str]) -> None:
        """Register a group of tools.

        Args:
            group_name (str): The name of the group.
            tool_names (List[str]): List of tool names to include in the group.
        """
        self._groups[group_name] = set(tool_names)

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name.

        Args:
            name (str): The name of the tool.

        Returns:
            Optional[Tool]: The tool instance if found, else None.
        """
        return self._tools.get(name)

    def get_tools(self, names: List[str]) -> List[Tool]:
        """Get multiple tools by names.

        Args:
            names (List[str]): List of tool names.

        Returns:
            List[Tool]: List of found tool instances.
        """
        return [self._tools[name] for name in names if name in self._tools]

    def get_group(self, group_name: str) -> List[Tool]:
        """Get all tools in a group.

        Args:
            group_name (str): The name of the group.

        Returns:
            List[Tool]: List of tool instances in the group.
        """
        if group_name not in self._groups:
            return []
        tool_names = self._groups[group_name]
        return [self._tools[name] for name in tool_names if name in self._tools]

    def list_tools(self) -> List[str]:
        """List all registered tool names.

        Returns:
            List[str]: List of tool names.
        """
        return list(self._tools.keys())

    def list_groups(self) -> List[str]:
        """List all registered group names.

        Returns:
            List[str]: List of group names.
        """
        return list(self._groups.keys())

    def unregister_tool(self, name: str) -> None:
        """Remove a tool from the registry by name if present."""
        if name in self._tools:
            del self._tools[name]


# Global registry instance
_registry: ToolRegistry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Get the global tool registry.

    Returns:
        ToolRegistry: The global registry instance.
    """
    return _registry

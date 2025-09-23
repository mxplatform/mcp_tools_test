"""Tool selection and binding helper for graph classes.

This module provides ToolSelector, a single responsibility class that
resolves Tool objects from the global registry based on class-level
selections (_selected_tools and _selected_groups) and converts them to
LangChain-compatible tool objects. It also exposes lazy binding to an
owner's LLM (if the LLM supports bind_tools).
"""
from typing import Any, List, Optional

from .protocols import Tool
from .registry import get_registry


class ToolSelector:
    """Resolve and manage tools for an owning graph-like object.

    The selector expects an "owner" object (e.g. a BaseGraph instance)
    that may have an `llm` attribute and class-level attributes set by
    decorators: `_selected_tools` and `_selected_groups`.

    Attributes:
        owner: The object that owns this selector (typically a graph instance).
        tool_objs: Raw Tool objects resolved from the registry.
        tools: LangChain-compatible tool objects returned by Tool.get_langchain_tool().
        _bound_llm: Cached result of owner.llm.bind_tools(self.tools) when available.
    """

    def __init__(self, owner: Any) -> None:
        self.owner: Any = owner
        self.tool_objs: List[Tool] = []
        self.tools: List[Any] = []
        self._bound_llm: Optional[Any] = None
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Resolve tools from the global registry and prepare LangChain tools.

        Simplified: collect tools listed on the owner's class (by name or group)
        and convert them to LangChain-compatible tools. Removed auto-registration,
        deduplication and extra logging to keep behavior explicit and predictable.
        """
        registry = get_registry()
        selected: List[Tool] = []

        if hasattr(self.owner.__class__, "_selected_tools"):
            names = getattr(self.owner.__class__, "_selected_tools", [])
            selected.extend(registry.get_tools(names))

        if hasattr(self.owner.__class__, "_selected_groups"):
            for group_name in getattr(self.owner.__class__, "_selected_groups", []):
                selected.extend(registry.get_group(group_name))

        # Deduplicate tools by name while preserving registration order. This
        # ensures remote MCP tools and local tools can coexist without
        # producing duplicate LangChain tool entries.
        seen = set()
        deduped: List[Tool] = []
        for t in selected:
            if t.name in seen:
                continue
            seen.add(t.name)
            deduped.append(t)

        self.tool_objs = deduped
        self.tools = [t.get_langchain_tool() for t in self.tool_objs]
        self._bound_llm = None

    def refresh_tools(self) -> None:
        """Public method to recompute selected tools at runtime."""
        self._setup_tools()

    def bind_tools(self) -> Optional[Any]:
        """Bind the current tools to the owner's LLM if supported.

        Returns the bound LLM object or None if binding isn't supported or fails.
        """
        llm: Optional[Any] = getattr(self.owner, "llm", None)
        if llm is None or not hasattr(llm, "bind_tools"):
            return None
        try:
            self._bound_llm = llm.bind_tools(self.tools)
            return self._bound_llm
        except Exception:
            self._bound_llm = None
            return None

    @property
    def bound_llm(self) -> Optional[Any]:
        """Lazily bind tools to the owner's LLM on first access and cache the result."""
        if self._bound_llm is None:
            return self.bind_tools()
        return self._bound_llm

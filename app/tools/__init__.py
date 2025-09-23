from typing import Any, Callable, Optional

from .analytics.factory import AnalyticsToolFactory
from .decorators import tool, use_analytics_tools, use_group, use_sql_tools, use_tools
from .groups import setup_tool_groups
from .protocols import AsyncBaseTool, AsyncTool, BaseTool, Tool
from .registry import get_registry
from .sql.config import CONFIG_MAP
from .sql.factory import SQLToolFactory


def initialize_tools(db: Optional[Any], llm: Any) -> None:
    """Initialize and register all tools used by the application.

    Args:
        db: Either a SQLDatabase instance or a callable that returns one (db provider).
        llm: Language-model or client object passed to analytics tool factories.
    """
    _registry: Any = get_registry()

    if db is None:
        db_provider: Optional[Callable[[], Any]] = None
    elif callable(db):
        db_provider = db  # already a provider
    else:

        def _provider() -> Any:
            return db

        db_provider = _provider

    sql_factory = SQLToolFactory(db=db_provider, register=False)
    sql_tools = sql_factory.create_tools(names=list(CONFIG_MAP.keys()))
    for tool_item in sql_tools:
        _registry.register_tool(tool_item)

    analytics_factory = AnalyticsToolFactory(llm=llm, register=False)
    analytics_tools = analytics_factory.create_tools()
    for tool_item in analytics_tools:
        _registry.register_tool(tool_item)

    setup_tool_groups()


__all__ = [
    "get_registry",
    "use_tools",
    "use_group",
    "tool",
    "use_sql_tools",
    "use_analytics_tools",
    "setup_tool_groups",
    "initialize_tools",
    "Tool",
    "AsyncTool",
    "BaseTool",
    "AsyncBaseTool",
]

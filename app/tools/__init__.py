from langchain_aws.chat_models import ChatBedrockConverse
from langchain_community.utilities import SQLDatabase

from .analytics import AnalyticsTool
from .decorators import tool, use_analytics_tools, use_group, use_sql_tools, use_tools
from .groups import setup_tool_groups
from .interfaces import BaseTool, Tool
from .registry import get_registry
from .sql import SQLTool, SQLToolFactory


def initialize_tools(db: SQLDatabase, llm: ChatBedrockConverse) -> None:
    """Initialize and register all tools.

    Simplified - no provider pattern, no complex abstractions.
    """
    registry = get_registry()

    # Create SQL tools
    sql_factory = SQLToolFactory(db=db)
    sql_tools = sql_factory.create_all_tools()

    for sql_tool in sql_tools:
        registry.register_tool(sql_tool)

    # Create analytics tool directly
    analytics_tool = AnalyticsTool.create_tool(llm=llm)
    registry.register_tool(analytics_tool)

    # Setup tool groups
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
    "BaseTool",
    "Tool",
    "AnalyticsTool",
    "SQLTool",
    "SQLToolFactory",
]

from typing import List

from langchain_aws.chat_models import ChatBedrockConverse
from langchain_community.utilities import SQLDatabase
from langchain_mcp_adapters.tools import to_fastmcp

from .analytics import AnalyticsTool
from .decorators import tool, use_analytics_tools, use_group, use_sql_tools, use_tools
from .groups import setup_tool_groups
from .interfaces import BaseTool, Tool
from .registry import get_registry
from .sql import SQLTool, SQLToolFactory


def initialize_tools(db: SQLDatabase, llm: ChatBedrockConverse) -> List[Tool]:
    """Initialize and register all tools.

    Simplified - no provider pattern, no complex abstractions.
    """
    # Create SQL tools
    sql_factory = SQLToolFactory(db=db)
    sql_tools = sql_factory.create_all_tools()

    # Create analytics tool directly
    analytics_tool = AnalyticsTool.create_tool(llm=llm)
    tools = sql_tools + [analytics_tool]

    mcp_tools = []
    for _tool in tools:
        try:
            mcp_tools.append(to_fastmcp(_tool.get_langchain_tool()))
        except Exception as e:
            print(f"Failed to adapt tool {_tool.name}: {e}")

    return mcp_tools


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

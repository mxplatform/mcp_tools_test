from typing import Any, Callable, List, Optional

from langchain_mcp_adapters.tools import to_fastmcp

from .analytics.factory import AnalyticsToolFactory
from .protocols import AsyncBaseTool
from .sql.config import CONFIG_MAP
from .sql.factory import SQLToolFactory


def initialize_tools(db: Optional[Any], llm: Any) -> List[AsyncBaseTool]:
    """Initialize and register all tools used by the application.

    Args:
        db: Either a SQLDatabase instance or a callable that returns one (db provider).
        llm: Language-model or client object passed to analytics tool factories.
    """

    if db is None:
        db_provider: Optional[Callable[[], Any]] = None
    elif callable(db):
        db_provider = db
    else:

        def _provider() -> Any:
            return db

        db_provider = _provider

    sql_factory = SQLToolFactory(db=db_provider)
    sql_tools = sql_factory.create_tools(names=list(CONFIG_MAP.keys()))

    analytics_factory = AnalyticsToolFactory(llm=llm)
    analytics_tools = analytics_factory.create_tools()

    tools = sql_tools + analytics_tools

    mcp_tools = []
    for tool in tools:
        try:
            mcp_tools.append(to_fastmcp(tool.get_langchain_tool()))
        except Exception as e:
            print(f"Failed to adapt tool {tool.name}: {e}")

    return mcp_tools

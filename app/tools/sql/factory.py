import logging
from pathlib import Path
from typing import List

from langchain_community.utilities import SQLDatabase

from ..registry import get_registry
from .base import SQLTool
from .config import CONFIG_MAP

logger = logging.getLogger(__name__)


class SQLToolFactory:
    """Creates SQL tools from query and description files."""

    def __init__(self, db: SQLDatabase):
        self.db = db
        self.sql_dir = Path(__file__).parent / "queries"
        self.desc_dir = Path(__file__).parent.parent / "descriptions"

    def create_tool(self, name: str) -> SQLTool:
        """Create a single SQL tool."""
        if name not in CONFIG_MAP:
            raise ValueError(f"Unknown SQL tool: {name}")

        config = CONFIG_MAP[name]
        sql_file = self.sql_dir / f"{name}.sql"
        desc_file = self.desc_dir / f"{name}.md"

        if not sql_file.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_file}")
        if not desc_file.exists():
            raise FileNotFoundError(f"Description file not found: {desc_file}")

        return SQLTool.from_files(
            name=name,
            args_schema=config.args_schema,
            sql_file=str(sql_file),
            description_file=str(desc_file),
            db=self.db,
            output_schema=config.output_schema,
        )

    def create_all_tools(self) -> List[SQLTool]:
        """Create all configured SQL tools."""
        tools = []
        for name in CONFIG_MAP.keys():
            try:
                tool = self.create_tool(name)
                tools.append(tool)
            except Exception as e:
                logger.error(f"Failed to create SQL tool {name}: {e}")
        return tools

    def autodiscover_and_register(self) -> List[SQLTool]:
        """Discover SQL files and register matching tools."""
        registry = get_registry()
        tools = []

        for sql_file in self.sql_dir.glob("*.sql"):
            name = sql_file.stem
            if name in CONFIG_MAP:
                try:
                    tool = self.create_tool(name)
                    registry.register_tool(tool)
                    tools.append(tool)
                    logger.info(f"Auto-registered SQL tool: {name}")
                except Exception as e:
                    logger.error(f"Failed to auto-register {name}: {e}")

        return tools

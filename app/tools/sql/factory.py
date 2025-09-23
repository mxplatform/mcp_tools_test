from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.tools.factories.base import FactoryBase
from app.tools.schemas import CampaignLookupParams, CampaignRecentParams, KPIQueryArgs
from app.tools.sql.base import SQLTool
from app.tools.sql.config import CONFIG_MAP

logger = logging.getLogger(__name__)


@dataclass
class SQLToolFactory(FactoryBase):
    """
    Factory for creating and validating SQLTool instances.

    Attributes inherited from FactoryBase:
        desc_base: Base path for description files.
        register: If True, registers tools in the registry.
        registry: Optional custom registry instance.
        strict: If True, raises error on missing files.

    Additional attributes:
        db: Database connection or engine.
        sql_base: Base path for SQL query files.
    """

    db: Any = None
    sql_base: Optional[Path] = None

    def _default_paths(self) -> Tuple[Path, Path]:
        """Return default SQL queries and shared descriptions paths."""
        current_file = Path(__file__)
        sql_base = current_file.parent / "queries"
        desc_base = current_file.parent.parent / "descriptions"
        return sql_base, desc_base

    def known_names(self) -> Sequence[str]:
        """Return the list of known SQL tool names from CONFIG_MAP."""
        return list(CONFIG_MAP.keys())

    def validate(self, names: Optional[Sequence[str]] = None) -> Dict[str, List[str]]:
        """Validate existence of SQL and description files for given tool names.

        Extends FactoryBase.validate with SQL file checks.
        """
        sql_base, desc_base = self._resolve_paths()
        issues: Dict[str, List[str]] = {"missing_sql": [], "missing_descriptions": []}
        target_names = list(names) if names is not None else list(CONFIG_MAP.keys())
        for name in target_names:
            sql_file = sql_base / f"{name}.sql"
            desc_file = desc_base / f"{name}.md"
            if not sql_file.exists():
                issues["missing_sql"].append(str(sql_file))
            if not desc_file.exists():
                issues["missing_descriptions"].append(str(desc_file))
        return issues

    def _create_tool(self, name: str) -> SQLTool:
        """Create a SQLTool by reading its SQL and description files and using CONFIG_MAP."""
        cfg = CONFIG_MAP.get(name)
        if cfg is None:
            raise ValueError(f"Unknown SQL tool: {name}")

        sql_base, desc_base = self._resolve_paths()
        sql_file = sql_base / f"{name}.sql"
        desc_file = desc_base / f"{name}.md"

        if not sql_file.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_file}")
        if not desc_file.exists():
            raise FileNotFoundError(f"Description file not found: {desc_file}")

        return SQLTool.from_files(
            name=name,
            db=self.db,
            args_schema=cfg.args_schema,
            sql_file=str(sql_file),
            description_file=str(desc_file),
            output_schema=cfg.output_schema,
        )

    def create_tools_auto_discovery(self, schema_map: Optional[Dict[str, type]] = None) -> List[SQLTool]:
        """Keep auto-discovery logic for SQL tools (unchanged)."""
        sql_base, desc_base = self._resolve_paths()
        default_schema_map: Dict[str, type] = {
            "get_recent_campaigns": CampaignRecentParams,
            "lookup_campaigns": CampaignLookupParams,
            "get_campaign_metrics": KPIQueryArgs,
        }
        schema_map = schema_map or default_schema_map

        discovered: List[SQLTool] = []

        for sql_path in sql_base.glob("*.sql"):
            tool_name = sql_path.stem
            desc_path = desc_base / f"{tool_name}.md"

            if not desc_path.exists():
                logger.debug("Auto-discovery: skipping %s (missing description)", tool_name)
                continue
            if tool_name not in schema_map:
                logger.debug("Auto-discovery: skipping %s (no schema provided)", tool_name)
                continue

            cfg = CONFIG_MAP.get(tool_name)
            output_schema = cfg.output_schema if cfg is not None else None

            tool = SQLTool.from_files(
                name=tool_name,
                db=self.db,
                args_schema=schema_map[tool_name],
                sql_file=str(sql_path),
                description_file=str(desc_path),
                output_schema=output_schema,
            )
            discovered.append(tool)

        return discovered

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence, Tuple

from app.tools.analytics.base import AnalyticsTool
from app.tools.analytics.pandas_tool import PandasAnalytics
from app.tools.factories.base import FactoryBase

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsToolFactory(FactoryBase):
    """
    Factory for creating analytics tool instances (e.g., pandas-based analytics).

    Inherits common behavior from FactoryBase. The factory can validate descriptions
    and optionally register created tools.
    """

    llm: Any = None

    def _default_paths(self) -> Tuple[Path, Path]:
        """Return analytics and shared description directories."""
        current_file = Path(__file__)
        analytics_desc = current_file.parent / "descriptions"
        shared_desc = current_file.parent.parent / "descriptions"
        return analytics_desc, shared_desc

    def known_names(self) -> Sequence[str]:
        """Return the default analytics tool names exposed by this factory."""
        return ["analyse_data"]

    def _create_tool(self, name: str) -> AnalyticsTool:
        """Create a single AnalyticsTool by name using PandasAnalytics."""
        if name != "analyse_data":
            raise ValueError(f"Unknown analytics tool: {name}")

        pa = PandasAnalytics(llm=self.llm)
        tools = pa.create_tools()
        if not tools:
            raise RuntimeError(f"Failed to create analytics tool: {name}")
        return tools[0]

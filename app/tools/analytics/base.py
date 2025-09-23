from __future__ import annotations

from typing import Any, Callable, Optional, Type

from langchain.tools import StructuredTool
from pydantic import BaseModel

from ..protocols import AsyncBaseTool


class AnalyticsTool(AsyncBaseTool):
    """Base class for analytics tools that can be used synchronously or asynchronously.

    It accepts a callable (sync or async) and an args_schema (Pydantic model).
    If a synchronous callable is provided it will be run in a thread by the
    default AsyncBaseTool.call_async implementation. We expose a LangChain
    StructuredTool that calls this tool's call_async so LangChain treats it
    as async-capable; if that fails we fall back to a sync StructuredTool.
    """

    def __init__(self, name: str, description: str, func: Callable[..., Any], args_schema: Type[BaseModel]):
        super().__init__(name=name, description=description, sync_func=func)

        self.func = func
        self.args_schema = args_schema

        try:
            self._sync_lc_tool: Optional[StructuredTool] = StructuredTool.from_function(
                name=name, description=description, func=self.func, args_schema=self.args_schema
            )
        except Exception:
            self._sync_lc_tool = None

        try:
            self._lc_tool: Optional[StructuredTool] = StructuredTool.from_function(
                name=name, description=description, func=self.call_async, args_schema=self.args_schema
            )
        except Exception:
            self._lc_tool = self._sync_lc_tool

import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

from langchain.tools import StructuredTool
from langchain_community.utilities import SQLDatabase
from pydantic import BaseModel
from sqlalchemy import text

from app.tools.protocols import AsyncBaseTool


class SQLTool(AsyncBaseTool):
    """Base class for SQL-based tools.

    Accepts either a SQLDatabase instance or a callable that returns one. The
    actual connection is created lazily on first use and cached on the tool
    instance to avoid reconnecting on every tool call. This tool is async-capable
    by default: the synchronous SQL runner is attached as the default sync_func
    and call_async will run it in a thread.
    """

    def __init__(
        self,
        name: str,
        description: str,
        query: str,
        args_schema: Type[BaseModel],
        db: Union[SQLDatabase, Callable[[], SQLDatabase]],
        output_schema: Optional[List[Dict[str, str]]] = None,
    ):
        super().__init__(name=name, description=description, sync_func=None)

        self.query = query
        self.args_schema = args_schema
        self._db_provider: Union[SQLDatabase, Callable[[], SQLDatabase]] = db
        self._db_instance: Optional[SQLDatabase] = None
        self.output_schema = output_schema

        def _run_sql(**kwargs: Any) -> Any:
            logging.debug(f"Executing SQL query for {self.name}: {self.query}")
            logging.debug(f"With parameters: {kwargs}")

            try:
                args = self.args_schema(**kwargs)

                db_inst = self._get_db()

                with db_inst._engine.begin() as connection:
                    result = connection.execute(text(self.query), args.model_dump())
                    columns = list(result.keys())
                    rows = result.fetchall()

                if self.output_schema:
                    column_types = self.output_schema
                    try:
                        columns = [
                            item["column"] if isinstance(item, dict) else getattr(item, "column", str(item))
                            for item in self.output_schema
                        ]
                    except Exception:
                        pass
                else:
                    try:
                        meta_cols = getattr(result._metadata, "_columns", {})
                        column_types = [
                            {"column": c, "type": str(meta_cols[c].type) if c in meta_cols else "string"}
                            for c in columns
                        ]
                    except Exception:
                        column_types = [{"column": c, "type": "string"} for c in columns]

                if rows:
                    data = [dict(zip(columns, [str(value) for value in row])) for row in rows]
                    return json.dumps(
                        {"columns": columns, "column_types": column_types, "data": data, "row_count": len(data)}
                    )
                else:
                    return json.dumps({"columns": columns, "column_types": column_types, "data": [], "row_count": 0})

            except Exception as e:
                logging.error(f"SQL execution failed for {self.name}: {e}")
                return f"SQL execution failed: {e}"

        self._sync_func = _run_sql

        try:
            self._sync_lc_tool = StructuredTool.from_function(
                name=self.name, description=self.description, func=_run_sql, args_schema=self.args_schema
            )
        except Exception:
            self._sync_lc_tool = None

        try:
            async_lc = StructuredTool.from_function(
                name=self.name,
                description=self.description,
                func=self.call_async,
                args_schema=self.args_schema,
                output_schema=self.output_schema,
            )
            try:
                setattr(async_lc, "output_schema", self.output_schema)
            except Exception:
                pass
            try:
                setattr(async_lc, "_declared_output_schema", self.output_schema)
            except Exception:
                pass

            self._lc_tool = async_lc
        except Exception:
            self._lc_tool = getattr(self, "_sync_lc_tool", None)

    def _get_db(self) -> SQLDatabase:
        """Return the cached SQLDatabase instance, creating it if necessary."""
        if self._db_instance is not None:
            return self._db_instance
        provider = self._db_provider
        if callable(provider):
            self._db_instance = provider()
        else:
            self._db_instance = provider
        return self._db_instance

        raise NotImplementedError("No LangChain tool available for this SQLTool")

    @classmethod
    def from_files(
        cls,
        name: str,
        db: Union[SQLDatabase, Callable[[], SQLDatabase]],
        args_schema: Type[BaseModel],
        sql_file: str,
        description_file: str,
        output_schema: Optional[List[Dict[str, str]]] = None,
    ) -> "SQLTool":
        """Convenience constructor to create tool from SQL and description files."""
        sql_path = Path(sql_file)
        desc_path = Path(description_file)

        if not sql_path.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_file}")
        if not desc_path.exists():
            raise FileNotFoundError(f"Description file not found: {description_file}")

        return cls(
            name=name,
            description=desc_path.read_text().strip(),
            query=sql_path.read_text().strip(),
            args_schema=args_schema,
            db=db,
            output_schema=output_schema,
        )

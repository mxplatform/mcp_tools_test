import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from langchain.tools import StructuredTool
from langchain_community.utilities import SQLDatabase
from pydantic import BaseModel
from sqlalchemy import text
from typing_extensions import override

from ..interfaces import BaseTool


class SQLTool(BaseTool):
    """Base class for SQL-based tools."""

    def __init__(
        self,
        name: str,
        description: str,
        query: str,
        args_schema: Type[BaseModel],
        db: Optional[SQLDatabase] = None,
        output_schema: Optional[List[Dict[str, str]]] = None,
    ):
        super().__init__(name=name, description=description, args_schema=args_schema)
        self.query = query
        self.db: Optional[SQLDatabase] = db
        self.output_schema = output_schema

        self._lc_tool = StructuredTool.from_function(
            name=name, description=description, func=self.invoke, args_schema=args_schema
        )

    @classmethod
    def from_files(
        cls,
        name: str,
        args_schema: Type[BaseModel],
        sql_file: str,
        description_file: str,
        db: Optional[SQLDatabase] = None,
        output_schema: Optional[List[Dict[str, str]]] = None,
    ) -> "SQLTool":
        """Create tool from SQL and description files."""
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

    @override
    def invoke(self, **kwargs: Any) -> Any:
        """Execute SQL query synchronously."""
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
                        {"column": c, "type": str(meta_cols[c].type) if c in meta_cols else "string"} for c in columns
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
            logging.exception(f"SQL execution failed for {self.name}: {e}")
            return f"SQL execution failed: {e}"

    @override
    def get_langchain_tool(self) -> Any:
        """Return the LangChain tool."""
        return self._lc_tool

    def _get_db(self) -> SQLDatabase:
        """Return the SQLDatabase instance, initializing if needed."""
        if isinstance(self.db, SQLDatabase):
            return self.db
        if self.db is None:
            raise ValueError("No database connection provided to SQLTool")
        else:
            raise ValueError("Invalid database connection provided to SQLTool")

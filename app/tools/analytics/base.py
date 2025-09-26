from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from typing import Any, Type

import pandas as pd
from langchain.tools import StructuredTool
from langchain_aws.chat_models import ChatBedrockConverse
from langchain_experimental.agents import create_pandas_dataframe_agent
from pydantic import BaseModel
from typing_extensions import override

from ..interfaces import BaseTool
from ..schemas import AnalyseDataInput


class AnalyticsTool(BaseTool):
    """Base class for analytics tools that can be used synchronously or asynchronously."""

    def __init__(self, name: str, description: str, args_schema: Type[BaseModel], llm: ChatBedrockConverse):
        super().__init__(name=name, description=description, args_schema=args_schema)

        self.llm = llm
        self._lc_tool = StructuredTool.from_function(
            name=name, description=description, func=self.invoke, args_schema=args_schema
        )

    @classmethod
    def create_tool(
        cls,
        llm: ChatBedrockConverse,
    ) -> AnalyticsTool:
        """Create an AnalyticsTool instance from a description file."""
        name = "analyse_data"
        desc_file = Path(__file__).parent.parent / "descriptions" / f"{name}.md"

        if desc_file.exists():
            description = desc_file.read_text().strip()
        else:
            description = "Analyze data using natural language queries with Python and pandas."

        return cls(
            name=name,
            description=description,
            args_schema=AnalyseDataInput,
            llm=llm,
        )

    @override
    def invoke(self, **kwargs: Any) -> Any:
        """Execute data analysis using pandas agent.

        Accepts the same keyword-args signature as BaseTool.invoke and extracts
        `query` and `df_data` from the provided arguments or from the args_schema model.
        """
        try:
            args = self.args_schema(**kwargs)
            query = getattr(args, "query", kwargs.get("query", ""))
            df_data = getattr(args, "df_data", kwargs.get("df_data", ""))
        except Exception:
            query = kwargs.get("query", "")
            df_data = kwargs.get("df_data", "")
            return {"error": "No data provided. Please pass DataFrame as CSV using df.to_csv(index=False)."}

        if self.llm is None:
            return {"error": "No LLM provided. Please initialise AnalyticsTool with an LLM to use this tool."}

        try:
            df = pd.read_csv(StringIO(df_data))

            structured_query = f"""
            {query}

            IMPORTANT:
            - Make sure pandas and json modules are imported.
            - When filtering by date, use actual date columns, parsed as datetime.
            - For each numerical result, provide a label with the exact calculated value.
            - Do not print or return the full DataFrame.
            - Use only the passed DataFrame for analysis.
            - Return the sums as JSON or a structured dictionary only.
            - Do NOT print or generate separate narrative numbers.
            """

            agent = create_pandas_dataframe_agent(
                llm=self.llm,
                df=df,
                verbose=False,
                allow_dangerous_code=True,
                return_intermediate_steps=False,
            )

            try:
                result = agent.invoke({"input": structured_query})
                output = result.get("output", str(result))
                try:
                    parsed = json.loads(output)
                    return {"result": parsed}
                except Exception:
                    return {"result": output}

            except Exception as agent_error:
                return {
                    "error": f"Analysis failed: {str(agent_error)}. Try simplifying your query or check data format."
                }

        except pd.errors.EmptyDataError:
            return {"error": "Error: The provided data appears to be empty or invalid CSV format."}
        except pd.errors.ParserError as parse_error:
            return {"error": f"Error parsing CSV data: {str(parse_error)}"}
        except Exception as e:
            return {"error": f"Error analysing data: {str(e)}"}

    @override
    def get_langchain_tool(self) -> StructuredTool:
        """Return a LangChain compatible tool instance."""
        return self._lc_tool

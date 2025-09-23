from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from typing import Any, List, Optional

import pandas as pd
from langchain.tools import StructuredTool
from langchain_experimental.agents import create_pandas_dataframe_agent

from ..schemas import AnalyseDataInput
from .base import AnalyticsTool


class PandasAnalytics:
    """Class-based implementation that provides analytics tools backed by a pandas agent.

    Usage:
        pa = PandasAnalytics(llm)
        analytics_tools = pa.create_tools()  # returns List[AnalyticsTool]
        lc_tools = pa.get_langchain_tools()   # returns List[StructuredTool]

    The class keeps the LLM as state so bound methods can be passed directly to
    AnalyticsTool instances (so method resolution and self are preserved).
    """

    def __init__(self, llm: Optional[Any] = None) -> None:
        self.llm = llm

        analytics_desc = Path(__file__).parent / "descriptions" / "analyse_data.md"
        shared_desc = Path(__file__).parent.parent / "descriptions" / "analyse_data.md"
        if analytics_desc.exists():
            self.description = analytics_desc.read_text().strip()
        elif shared_desc.exists():
            self.description = shared_desc.read_text().strip()
        else:
            self.description = "Analyse data using natural language queries with Python and pandas."

    def _analyse_data(self, query: str, df_data: str = "") -> Any:
        """Execute data analysis using pandas agent.

        This implementation mirrors the previous function-based implementation but is an
        instance method so it can close over self.llm and other instance state.
        """
        if not df_data:
            return {"error": "No data provided. Please pass DataFrame as CSV using df.to_csv(index=False)."}

        if self.llm is None:
            return {"error": "No LLM provided. Please initialise PandasAnalytics with an LLM to use this tool."}

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

    def create_tools(self) -> List[AnalyticsTool]:
        """Return AnalyticsTool instances provided by this class.

        Currently returns a single tool named 'analyse_data'.
        """
        tool = AnalyticsTool(
            name="analyse_data",
            description=self.description,
            func=self._analyse_data,
            args_schema=AnalyseDataInput,
        )
        return [tool]

    def get_langchain_tools(self) -> List[StructuredTool]:
        """Return LangChain StructuredTool instances for registration or binding."""
        return [t.get_langchain_tool() for t in self.create_tools()]

    def get_langchain_tool(self) -> StructuredTool:
        """Return the primary StructuredTool (convenience helper)."""
        return self.get_langchain_tools()[0]

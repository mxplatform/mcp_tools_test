"""Small helper script to call the `get_campaign_metrics` tool via MCP.

Creates a MultiMCPClient (configured for a local Streamable HTTP MCP),
connects, discovers the `get_campaign_metrics` tool, runs it with a
date range, and converts the returned payload into a pandas DataFrame.

Run with:
    uv run python run_mcp.py
"""
from __future__ import annotations

import asyncio
import inspect
import json
from typing import Any

import pandas as pd
from langchain_mcp_adapters.clients import MultiMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

client = MultiMCPClient({"local_tools": {"url": "http://localhost:8080/mcp", "transport": "streamable_http"}})


async def main() -> None:
    """Connect to the configured MCP endpoint, run the tool and build a DataFrame."""

    async with client.session("local_tools") as session:
        lc_tools = await load_mcp_tools(session)

        # Find the tool by name
        mcp_tool = next((t for t in lc_tools if getattr(t, "name", None) == "get_campaign_metrics"), None)
        if mcp_tool is None:
            raise RuntimeError("Tool 'get_campaign_metrics' not found on MCP server")

        args: dict[str, Any] = {"account_id": "920", "start_date": "2024-01-01", "end_date": "2024-12-31"}

        # Prefer an async entrypoint if available
        if hasattr(mcp_tool, "run"):
            fn = getattr(mcp_tool, "run")
            if inspect.iscoroutinefunction(fn):
                result = await fn(args)  # type: ignore[arg-type]
            else:
                result = fn(args)  # type: ignore[call-arg]
        elif hasattr(mcp_tool, "ainvoke"):
            result = await mcp_tool.ainvoke(args)
        elif hasattr(mcp_tool, "invoke"):
            result = mcp_tool.invoke(args)
        else:
            raise RuntimeError("Tool has no callable entrypoint (run/ainvoke/invoke)")

        # Normalise result (StructuredTool often returns (content, artifacts))
        content = result[0] if isinstance(result, (list, tuple)) and len(result) > 0 else result

        # Parse returned content into a Python object
        try:
            payload = json.loads(content) if isinstance(content, str) else content
        except Exception:
            # fallback for legacy stringified Python structures
            payload = eval(content) if isinstance(content, str) else content

        if not isinstance(payload, dict) or "data" not in payload:
            raise RuntimeError(f"Unexpected payload format: {payload}")

        df = pd.DataFrame(payload["data"])
        print(df.head())


if __name__ == "__main__":
    asyncio.run(main())

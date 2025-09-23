"""Minimal FastMCP HTTP Streamable server exposing local tools.

This module builds a small MCP server using the official python SDK
`mcp[cli]` (FastMCP). It discovers tools from the local
`app.tools` registry and exposes them over the Streamable HTTP
transport so external clients can connect without using stdio.

The server also loads markdown files from `app/tools/descriptions` and
attaches them as tool descriptions so remote LLMs can see helpful
instructions when discovering tools.

This file intentionally contains only wiring and no heavy business
logic — the PoC goal is to expose the existing tool objects that live
in `app.tools`.
"""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from .tools.clickhouse import build_clickhouse_uri
from langchain_community.utilities import SQLDatabase
from langchain_aws import ChatBedrockConverse
from .tools import initialize_tools

load_dotenv('.env')


LOG = logging.getLogger(__name__)


def run_server(host: str = "0.0.0.0", port: int = 8080) -> None:
    """Start an MCP server exposing tools via Streamable HTTP.

    This function:
    - Initializes the local tool registry (no DB by default).
    - Loads descriptions from `app/tools/descriptions` and monkey-patches
        tool descriptions where a matching file exists.
    - Starts a FastMCP server using the streamable HTTP transport.
    """

    LOG.info("Creating database and LLM instances")
    db = SQLDatabase.from_uri(build_clickhouse_uri())
    llm = ChatBedrockConverse(
        model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0", 
        region_name="us-east-1"
    )

    LOG.info("Initializing tools")
    tools = initialize_tools(db=None, llm=None)

    LOG.info("Starting MCP server on %s:%d", host, port)
    mcp = FastMCP(host=host, port=port, tools=tools)

    LOG.info("Starting Streamable HTTP transport")
    mcp.run(transport="streamable-http")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    try:
        run_server()
    except KeyboardInterrupt:
        LOG.info("Server stopped by KeyboardInterrupt")

if __name__ == "__main__":
	main()


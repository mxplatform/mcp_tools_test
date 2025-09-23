"""MCP client integration package (renamed to avoid collision with external SDK).

Re-export the manager and tool adapter.
"""

from .base import MCPTool
from .client import MCPManager

__all__ = ["MCPManager", "MCPTool"]

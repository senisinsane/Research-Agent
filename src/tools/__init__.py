"""
Search tools for the Web Research Agent.

Provides multiple search providers with automatic fallback support.
"""

from src.tools.registry import get_available_tools, get_tool_by_name

__all__ = ["get_available_tools", "get_tool_by_name"]

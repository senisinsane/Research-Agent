"""
Tool registry for managing available search tools.

Provides functions to get available tools based on configuration.
"""

from collections.abc import Callable

from src.config import get_settings
from src.logging_config import get_logger
from src.tools.duckduckgo_search import web_search_ddg
from src.tools.serpapi_search import serpapi_search, serpapi_search_news
from src.tools.tavily_search import tavily_search, tavily_search_news

logger = get_logger(__name__)

# All available tools mapped by name
_TOOL_REGISTRY: dict[str, Callable] = {
    "tavily_search": tavily_search,
    "tavily_search_news": tavily_search_news,
    "serpapi_search": serpapi_search,
    "serpapi_search_news": serpapi_search_news,
    "web_search_ddg": web_search_ddg,
}


def get_available_tools() -> list[Callable]:
    """
    Get list of available search tools based on configuration.

    Tools are ordered by preference:
    1. Tavily (best for AI agents) - if API key configured
    2. SerpAPI (Google results) - if API key configured
    3. DuckDuckGo (free fallback) - always available

    Returns:
        List of tool functions that can be used by the agent.
    """
    settings = get_settings()
    tools = []

    # Add Tavily tools if configured (highest priority)
    if settings.has_tavily:
        tools.extend([tavily_search, tavily_search_news])
        logger.info("Tavily search tools enabled")
    else:
        logger.debug("Tavily not configured, skipping")

    # Add SerpAPI tools if configured
    if settings.has_serpapi:
        tools.extend([serpapi_search, serpapi_search_news])
        logger.info("SerpAPI search tools enabled")
    else:
        logger.debug("SerpAPI not configured, skipping")

    # Always add DuckDuckGo as fallback
    tools.append(web_search_ddg)
    logger.info("DuckDuckGo search tool enabled (fallback)")

    logger.info(f"Total tools available: {len(tools)}")
    return tools


def get_tool_by_name(name: str) -> Callable | None:
    """
    Get a specific tool by name.

    Args:
        name: The name of the tool to retrieve.

    Returns:
        The tool function if found, None otherwise.
    """
    return _TOOL_REGISTRY.get(name)

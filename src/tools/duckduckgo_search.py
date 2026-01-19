"""
DuckDuckGo search tool implementation.

Free search provider that doesn't require an API key.
Used as a fallback when other providers are unavailable.
"""

import warnings

from langchain_core.tools import tool

from src.config import get_settings
from src.logging_config import get_logger

# Suppress deprecation warnings about package rename
warnings.filterwarnings("ignore", message=".*duckduckgo_search.*renamed.*")

logger = get_logger(__name__)


def _get_ddgs_client():
    """Get DuckDuckGo search client, preferring the new ddgs package."""
    try:
        from ddgs import DDGS
        return DDGS()
    except ImportError:
        try:
            from duckduckgo_search import DDGS
            return DDGS()
        except ImportError:
            raise ImportError(
                "DuckDuckGo search package not installed. "
                "Run: pip install ddgs"
            )


@tool
def web_search_ddg(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo (free, no API key required).

    Use this tool for general web searches when other search tools are unavailable.

    Args:
        query: The search query string. Be specific and targeted.
        max_results: Maximum number of results to return (default: 5, max: 10).

    Returns:
        A formatted string containing search results with titles, snippets, and URLs.
    """
    settings = get_settings()
    max_results = min(max_results, settings.search_max_results)

    try:
        ddgs = _get_ddgs_client()
        results = list(ddgs.text(query, max_results=max_results))

        if not results:
            logger.warning(f"DuckDuckGo: No results found for query: {query}")
            return f"No results found for: '{query}'. Try rephrasing your search query."

        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            body = result.get("body", "No description available")
            url = result.get("href", result.get("link", "No URL"))

            formatted_results.append(
                f"[{i}] {title}\n"
                f"    Summary: {body}\n"
                f"    Source: {url}"
            )

        output = f"DuckDuckGo results for: '{query}'\n" + "=" * 50 + "\n"
        output += "\n\n".join(formatted_results)

        logger.debug(f"DuckDuckGo: Found {len(results)} results for: {query}")
        return output

    except ImportError as e:
        return f"DuckDuckGo search unavailable: {e}"
    except Exception as e:
        logger.error(f"DuckDuckGo search failed for '{query}': {e}")
        return f"DuckDuckGo search error: {e}. Try using tavily_search or serpapi_search instead."

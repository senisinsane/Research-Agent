"""
Tavily search tool implementation.

Tavily is optimized for AI agents and provides high-quality search results.
"""

from langchain_core.tools import tool

from src.config import get_settings
from src.exceptions import SearchError, SearchProviderUnavailableError
from src.logging_config import get_logger

logger = get_logger(__name__)


def _get_tavily_client():
    """Get configured Tavily client."""
    settings = get_settings()
    
    if not settings.has_tavily:
        raise SearchProviderUnavailableError(
            "Tavily API key not configured",
            provider="tavily",
        )
    
    try:
        from tavily import TavilyClient
        return TavilyClient(api_key=settings.tavily_api_key)
    except ImportError as e:
        raise SearchProviderUnavailableError(
            "Tavily package not installed. Run: pip install tavily-python",
            provider="tavily",
        ) from e


@tool
def tavily_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using Tavily API - optimized for AI agents and LLMs.

    Tavily provides high-quality, relevant results specifically designed for AI applications.
    Use this as your PRIMARY search tool when available.

    Args:
        query: The search query string. Be specific and targeted.
        max_results: Maximum number of results to return (default: 5, max: 10).

    Returns:
        A formatted string containing search results with titles, content, and URLs.
    """
    settings = get_settings()
    max_results = min(max_results, settings.search_max_results)

    try:
        client = _get_tavily_client()
        response = client.search(query=query, max_results=max_results)
        results = response.get("results", [])

        if not results:
            logger.warning(f"Tavily: No results found for query: {query}")
            return f"No results found for: '{query}'. Try rephrasing your search query."

        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            content = result.get("content", "No content available")
            url = result.get("url", "No URL")
            score = result.get("score", 0)

            formatted_results.append(
                f"[{i}] {title} (relevance: {score:.2f})\n"
                f"    Content: {content[:500]}{'...' if len(content) > 500 else ''}\n"
                f"    Source: {url}"
            )

        output = f"Tavily results for: '{query}'\n" + "=" * 50 + "\n"
        output += "\n\n".join(formatted_results)

        logger.debug(f"Tavily: Found {len(results)} results for: {query}")
        return output

    except SearchProviderUnavailableError:
        return "Tavily API key not configured. Use serpapi_search or web_search_ddg instead."
    except Exception as e:
        logger.error(f"Tavily search failed for '{query}': {e}")
        return f"Tavily search error: {e}. Try using serpapi_search or web_search_ddg instead."


@tool
def tavily_search_news(query: str, max_results: int = 5) -> str:
    """
    Search for recent news using Tavily API.

    Use this for finding the latest news and current events.

    Args:
        query: The news search query.
        max_results: Maximum number of results (default: 5, max: 10).

    Returns:
        A formatted string containing news results.
    """
    settings = get_settings()
    max_results = min(max_results, settings.search_max_results)

    try:
        client = _get_tavily_client()
        response = client.search(
            query=query,
            max_results=max_results,
            topic="news",
        )
        results = response.get("results", [])

        if not results:
            logger.warning(f"Tavily News: No results found for query: {query}")
            return f"No news found for: '{query}'. Try a broader search term."

        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            content = result.get("content", "No content available")
            url = result.get("url", "No URL")
            published_date = result.get("published_date", "Unknown date")

            formatted_results.append(
                f"[{i}] {title}\n"
                f"    Date: {published_date}\n"
                f"    Content: {content[:400]}{'...' if len(content) > 400 else ''}\n"
                f"    Source: {url}"
            )

        output = f"Tavily News results for: '{query}'\n" + "=" * 50 + "\n"
        output += "\n\n".join(formatted_results)

        logger.debug(f"Tavily News: Found {len(results)} results for: {query}")
        return output

    except SearchProviderUnavailableError:
        return "Tavily API key not configured."
    except Exception as e:
        logger.error(f"Tavily news search failed for '{query}': {e}")
        return f"Tavily news search error: {e}"

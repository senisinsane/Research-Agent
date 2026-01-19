"""
SerpAPI search tool implementation.

Provides access to Google search results through SerpAPI.
"""

from langchain_core.tools import tool

from src.config import get_settings
from src.exceptions import SearchProviderUnavailableError
from src.logging_config import get_logger

logger = get_logger(__name__)


def _get_serpapi_params(query: str, max_results: int) -> dict:
    """Build SerpAPI request parameters."""
    settings = get_settings()
    
    if not settings.has_serpapi:
        raise SearchProviderUnavailableError(
            "SerpAPI key not configured",
            provider="serpapi",
        )
    
    return {
        "q": query,
        "api_key": settings.serpapi_api_key,
        "num": max_results,
        "engine": "google",
    }


@tool
def serpapi_search(query: str, max_results: int = 5) -> str:
    """
    Search Google using SerpAPI for high-quality Google search results.

    Use this tool when you need Google's search results, which often have
    the most comprehensive and up-to-date information.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default: 5, max: 10).

    Returns:
        A formatted string containing Google search results.
    """
    settings = get_settings()
    max_results = min(max_results, settings.search_max_results)

    try:
        from serpapi import GoogleSearch

        params = _get_serpapi_params(query, max_results)
        search = GoogleSearch(params)
        results = search.get_dict()
        organic_results = results.get("organic_results", [])

        if not organic_results:
            logger.warning(f"SerpAPI: No results found for query: {query}")
            return f"No results found for: '{query}'. Try rephrasing your search query."

        formatted_results = []
        for i, result in enumerate(organic_results[:max_results], 1):
            title = result.get("title", "No title")
            snippet = result.get("snippet", "No description available")
            link = result.get("link", "No URL")

            formatted_results.append(
                f"[{i}] {title}\n"
                f"    Summary: {snippet}\n"
                f"    Source: {link}"
            )

        output = f"Google (SerpAPI) results for: '{query}'\n" + "=" * 50 + "\n"
        output += "\n\n".join(formatted_results)

        logger.debug(f"SerpAPI: Found {len(organic_results)} results for: {query}")
        return output

    except ImportError:
        return "SerpAPI package not installed. Run: pip install google-search-results"
    except SearchProviderUnavailableError:
        return "SerpAPI key not configured. Use tavily_search or web_search_ddg instead."
    except Exception as e:
        logger.error(f"SerpAPI search failed for '{query}': {e}")
        return f"SerpAPI search error: {e}. Try using tavily_search or web_search_ddg instead."


@tool
def serpapi_search_news(query: str, max_results: int = 5) -> str:
    """
    Search Google News using SerpAPI for the latest news articles.

    Use this for finding recent news from Google News.

    Args:
        query: The news search query.
        max_results: Maximum number of results (default: 5, max: 10).

    Returns:
        A formatted string containing Google News results.
    """
    settings = get_settings()
    max_results = min(max_results, settings.search_max_results)

    try:
        from serpapi import GoogleSearch

        params = _get_serpapi_params(query, max_results)
        params["tbm"] = "nws"  # News search

        search = GoogleSearch(params)
        results = search.get_dict()
        news_results = results.get("news_results", [])

        if not news_results:
            logger.warning(f"SerpAPI News: No results found for query: {query}")
            return f"No news found for: '{query}'. Try a broader search term."

        formatted_results = []
        for i, result in enumerate(news_results[:max_results], 1):
            title = result.get("title", "No title")
            snippet = result.get("snippet", "No description available")
            link = result.get("link", "No URL")
            source = result.get("source", "Unknown source")
            date = result.get("date", "Unknown date")

            formatted_results.append(
                f"[{i}] {title}\n"
                f"    Date: {date} | Source: {source}\n"
                f"    Summary: {snippet}\n"
                f"    URL: {link}"
            )

        output = f"Google News (SerpAPI) results for: '{query}'\n" + "=" * 50 + "\n"
        output += "\n\n".join(formatted_results)

        logger.debug(f"SerpAPI News: Found {len(news_results)} results for: {query}")
        return output

    except ImportError:
        return "SerpAPI package not installed. Run: pip install google-search-results"
    except SearchProviderUnavailableError:
        return "SerpAPI key not configured."
    except Exception as e:
        logger.error(f"SerpAPI news search failed for '{query}': {e}")
        return f"SerpAPI news search error: {e}"

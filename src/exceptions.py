"""
Custom exceptions for the Web Research Agent.

Provides specific exception types for different failure modes,
enabling better error handling and debugging.
"""


class ResearchAgentError(Exception):
    """Base exception for all research agent errors."""

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(ResearchAgentError):
    """Raised when there's a configuration problem."""
    pass


class SearchError(ResearchAgentError):
    """Raised when a search operation fails."""

    def __init__(self, message: str, provider: str, query: str | None = None):
        super().__init__(
            message,
            details={"provider": provider, "query": query},
        )
        self.provider = provider
        self.query = query


class SearchProviderUnavailableError(SearchError):
    """Raised when a search provider is not configured or unavailable."""
    pass


class AgentExecutionError(ResearchAgentError):
    """Raised when the agent fails to execute a research query."""

    def __init__(self, message: str, query: str | None = None, iterations: int = 0):
        super().__init__(
            message,
            details={"query": query, "iterations": iterations},
        )
        self.query = query
        self.iterations = iterations


class EmptyResponseError(AgentExecutionError):
    """Raised when the agent produces an empty response."""
    pass

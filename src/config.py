"""
Configuration management for the Web Research Agent.

Uses pydantic-settings for type-safe configuration with environment variable support.
"""

from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for GPT model access",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use for the agent",
    )
    openai_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM responses (0.0 = deterministic)",
    )

    # Search Provider API Keys
    tavily_api_key: Optional[str] = Field(
        default=None,
        description="Tavily API key for AI-optimized search",
    )
    serpapi_api_key: Optional[str] = Field(
        default=None,
        description="SerpAPI key for Google search results",
    )

    # Agent Configuration
    max_iterations: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Maximum agent iterations to prevent infinite loops",
    )
    search_max_results: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum search results per query",
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="WARNING",
        description="Logging level",
    )
    verbose: bool = Field(
        default=False,
        description="Enable verbose output for debugging",
    )

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v: str) -> str:
        """Validate OpenAI API key format."""
        if not v or not v.startswith(("sk-", "sk-proj-")):
            raise ValueError(
                "Invalid OpenAI API key format. Key should start with 'sk-' or 'sk-proj-'"
            )
        return v

    @property
    def has_tavily(self) -> bool:
        """Check if Tavily API key is configured."""
        return bool(self.tavily_api_key and self.tavily_api_key.startswith("tvly-"))

    @property
    def has_serpapi(self) -> bool:
        """Check if SerpAPI key is configured."""
        return bool(self.serpapi_api_key and len(self.serpapi_api_key) > 10)


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Settings: Application configuration loaded from environment.
    
    Raises:
        ValidationError: If required settings are missing or invalid.
    """
    return Settings()

"""
Agent creation and execution for the Web Research Agent.

Uses LangGraph's prebuilt ReAct agent for reliable tool execution.
"""

from dataclasses import dataclass
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from src.config import Settings, get_settings
from src.exceptions import AgentExecutionError, EmptyResponseError
from src.logging_config import get_logger
from src.prompts import get_human_prompt, get_system_prompt
from src.tools import get_available_tools

logger = get_logger(__name__)


@dataclass
class ResearchResult:
    """Container for research results."""

    content: str
    query: str
    success: bool
    error: str | None = None


class ResearchAgent:
    """
    Production-ready research agent with web search capabilities.

    This agent uses LangGraph's ReAct pattern to plan, search, reason,
    and synthesize information into structured research reports.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_iterations: int | None = None,
    ):
        """
        Initialize the research agent.

        Args:
            settings: Application settings. If None, loads from environment.
            model: Override the default model.
            temperature: Override the default temperature.
            max_iterations: Override the default max iterations.
        """
        self._settings = settings or get_settings()
        self._model = model or self._settings.openai_model
        self._temperature = (
            temperature if temperature is not None else self._settings.openai_temperature
        )
        self._max_iterations = max_iterations or self._settings.max_iterations

        self._llm = self._create_llm()
        self._tools = get_available_tools()
        self._agent = self._create_agent()

        logger.info(
            f"ResearchAgent initialized: model={self._model}, "
            f"max_iterations={self._max_iterations}, "
            f"tools={len(self._tools)}"
        )

    def _create_llm(self) -> ChatOpenAI:
        """Create and configure the ChatOpenAI instance."""
        return ChatOpenAI(
            model=self._model,
            temperature=self._temperature,
            api_key=self._settings.openai_api_key,
        )

    def _create_agent(self) -> Any:
        """Create the LangGraph ReAct agent."""
        return create_react_agent(
            model=self._llm,
            tools=self._tools,
            prompt=get_system_prompt(),
        )

    def research(self, query: str) -> ResearchResult:
        """
        Execute a research query and return the result.

        Args:
            query: The research question to investigate.

        Returns:
            ResearchResult containing the report or error information.

        Raises:
            AgentExecutionError: If the agent fails to complete the research.
        """
        formatted_query = get_human_prompt(query)

        logger.info(f"Starting research: {query[:100]}...")

        try:
            messages = [HumanMessage(content=formatted_query)]
            config = {"recursion_limit": self._max_iterations * 2}

            result = self._agent.invoke({"messages": messages}, config=config)

            # Extract final message content
            output = self._extract_output(result)

            if not output:
                raise EmptyResponseError(
                    "Agent produced empty output",
                    query=query,
                )

            logger.info("Research completed successfully")
            return ResearchResult(
                content=output,
                query=query,
                success=True,
            )

        except EmptyResponseError:
            raise
        except Exception as e:
            logger.error(f"Research failed: {e}")
            raise AgentExecutionError(
                f"Research agent error: {e}",
                query=query,
            ) from e

    async def research_async(self, query: str) -> ResearchResult:
        """
        Execute a research query asynchronously.

        Args:
            query: The research question to investigate.

        Returns:
            ResearchResult containing the report or error information.
        """
        formatted_query = get_human_prompt(query)

        logger.info(f"Starting async research: {query[:100]}...")

        try:
            messages = [HumanMessage(content=formatted_query)]
            config = {"recursion_limit": self._max_iterations * 2}

            result = await self._agent.ainvoke({"messages": messages}, config=config)

            output = self._extract_output(result)

            if not output:
                raise EmptyResponseError(
                    "Agent produced empty output",
                    query=query,
                )

            logger.info("Async research completed successfully")
            return ResearchResult(
                content=output,
                query=query,
                success=True,
            )

        except EmptyResponseError:
            raise
        except Exception as e:
            logger.error(f"Async research failed: {e}")
            raise AgentExecutionError(
                f"Research agent error: {e}",
                query=query,
            ) from e

    @staticmethod
    def _extract_output(result: dict) -> str:
        """Extract the final output from agent result."""
        if "messages" in result and result["messages"]:
            final_message = result["messages"][-1]
            return (
                final_message.content
                if hasattr(final_message, "content")
                else str(final_message)
            )
        return str(result)

    @property
    def model(self) -> str:
        """Get the current model name."""
        return self._model

    @property
    def available_tools(self) -> list[str]:
        """Get names of available tools."""
        return [tool.name for tool in self._tools]


def create_agent(
    model: str | None = None,
    temperature: float | None = None,
    max_iterations: int | None = None,
) -> ResearchAgent:
    """
    Factory function to create a research agent.

    Args:
        model: OpenAI model to use (default: from settings).
        temperature: LLM temperature (default: from settings).
        max_iterations: Maximum iterations (default: from settings).

    Returns:
        Configured ResearchAgent instance.
    """
    return ResearchAgent(
        model=model,
        temperature=temperature,
        max_iterations=max_iterations,
    )

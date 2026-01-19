"""
AG-UI Protocol Integration for the Web Research Agent.

AG-UI (Agent-User Interaction Protocol) enables seamless integration
between AI agents and frontend applications like CopilotKit.

This implementation follows the AG-UI event protocol specification.
Reference: https://github.com/ag-ui-protocol/ag-ui
"""

import json
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime

from src.logging_config import get_logger

logger = get_logger(__name__)


# ============================================================================
# AG-UI Event Types
# ============================================================================

class AGUIEventType:
    """AG-UI Protocol event types."""
    RUN_STARTED = "RUN_STARTED"
    RUN_FINISHED = "RUN_FINISHED"
    RUN_ERROR = "RUN_ERROR"
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT"
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"
    TOOL_CALL_START = "TOOL_CALL_START"
    TOOL_CALL_ARGS = "TOOL_CALL_ARGS"
    TOOL_CALL_END = "TOOL_CALL_END"
    STATE_SNAPSHOT = "STATE_SNAPSHOT"
    STATE_DELTA = "STATE_DELTA"


def create_agui_event(event_type: str, **kwargs) -> str:
    """Create an AG-UI protocol event."""
    event = {"type": event_type, **kwargs}
    return json.dumps(event) + "\n"


# ============================================================================
# AG-UI Event Stream Generator
# ============================================================================

async def agui_stream_generator(query: str) -> AsyncGenerator[str, None]:
    """
    Generate AG-UI protocol events for streaming responses.

    Yields AG-UI events for:
    - RUN_STARTED
    - TEXT_MESSAGE_START
    - TEXT_MESSAGE_CONTENT (streaming chunks)
    - TEXT_MESSAGE_END
    - RUN_FINISHED

    Args:
        query: The research query.

    Yields:
        AG-UI protocol events as JSON strings.
    """
    run_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"

    logger.info(f"AG-UI stream starting for query: {query[:100]}...")

    # RUN_STARTED event
    yield create_agui_event(
        AGUIEventType.RUN_STARTED,
        runId=run_id,
        timestamp=timestamp,
    )

    # TEXT_MESSAGE_START event
    yield create_agui_event(
        AGUIEventType.TEXT_MESSAGE_START,
        messageId=message_id,
        role="assistant",
    )

    try:
        # Import and run the research agent
        from src.agent import create_agent

        agent = create_agent()
        result = agent.research(query)

        # Stream content in chunks for real-time display
        content = result.content
        chunk_size = 50  # Smaller chunks for smoother streaming

        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            yield create_agui_event(
                AGUIEventType.TEXT_MESSAGE_CONTENT,
                messageId=message_id,
                delta=chunk,
            )

        # TEXT_MESSAGE_END event
        yield create_agui_event(
            AGUIEventType.TEXT_MESSAGE_END,
            messageId=message_id,
        )

        # RUN_FINISHED event
        yield create_agui_event(
            AGUIEventType.RUN_FINISHED,
            runId=run_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        logger.info(f"AG-UI stream completed for run: {run_id}")

    except Exception as e:
        logger.error(f"AG-UI stream error: {e}")

        # RUN_ERROR event
        yield create_agui_event(
            AGUIEventType.RUN_ERROR,
            runId=run_id,
            message=str(e),
            code="AGENT_ERROR",
        )


# ============================================================================
# Synchronous Stream Generator (for non-async contexts)
# ============================================================================

def agui_stream_sync(query: str):
    """
    Synchronous generator for AG-UI events.

    Use this when async is not available.
    """
    run_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"

    # RUN_STARTED
    yield create_agui_event(
        AGUIEventType.RUN_STARTED,
        runId=run_id,
        timestamp=timestamp,
    )

    # TEXT_MESSAGE_START
    yield create_agui_event(
        AGUIEventType.TEXT_MESSAGE_START,
        messageId=message_id,
        role="assistant",
    )

    try:
        from src.agent import create_agent

        agent = create_agent()
        result = agent.research(query)

        content = result.content
        chunk_size = 50

        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            yield create_agui_event(
                AGUIEventType.TEXT_MESSAGE_CONTENT,
                messageId=message_id,
                delta=chunk,
            )

        yield create_agui_event(
            AGUIEventType.TEXT_MESSAGE_END,
            messageId=message_id,
        )

        yield create_agui_event(
            AGUIEventType.RUN_FINISHED,
            runId=run_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

    except Exception as e:
        yield create_agui_event(
            AGUIEventType.RUN_ERROR,
            runId=run_id,
            message=str(e),
            code="AGENT_ERROR",
        )


# ============================================================================
# LangGraph Agent Factory
# ============================================================================

def get_langgraph_agent():
    """
    Get a configured LangGraph agent for direct invocation.

    Returns:
        A LangGraph ReAct agent configured with research tools.
    """
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent

    from src.config import get_settings
    from src.prompts import get_system_prompt
    from src.tools import get_available_tools

    settings = get_settings()

    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=settings.openai_temperature,
        api_key=settings.openai_api_key,
    )

    tools = get_available_tools()

    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=get_system_prompt(),
    )

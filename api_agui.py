"""
AG-UI Protocol API Server for the Web Research Agent.

This API implements the AG-UI protocol for seamless integration with
frontend applications like CopilotKit.

Reference: https://github.com/ag-ui-protocol/ag-ui
Docs: https://docs.copilotkit.ai/
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv()

from src.config import get_settings
from src.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup."""
    settings = get_settings()
    setup_logging(level=settings.log_level)
    logger.info("AG-UI Research Agent API starting...")
    logger.info(f"Model: {settings.openai_model}")
    yield
    logger.info("AG-UI Research Agent API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="AG-UI Research Agent",
    description="Web Research Agent with AG-UI Protocol support for CopilotKit integration",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Models
# ============================================================================

class AGUIMessage(BaseModel):
    """AG-UI message format."""
    role: str
    content: str


class AGUIRequest(BaseModel):
    """AG-UI protocol request."""
    messages: list[AGUIMessage]
    threadId: str | None = None
    runId: str | None = None


class ResearchRequest(BaseModel):
    """Simple research request."""
    query: str = Field(..., min_length=3, max_length=2000)


# ============================================================================
# AG-UI Protocol Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AG-UI Research Agent",
        "version": "1.0.0",
        "protocol": "AG-UI",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "agui": "/agui (POST)",
            "copilotkit": "/copilotkit (POST)",
            "research": "/research (POST)",
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    settings = get_settings()
    return {
        "status": "healthy",
        "model": settings.openai_model,
        "protocol": "AG-UI",
        "tavily_configured": settings.has_tavily,
        "serpapi_configured": settings.has_serpapi,
    }


@app.post("/agui")
async def agui_endpoint(request: Request):
    """
    AG-UI Protocol endpoint for streaming agent responses.

    This endpoint implements the AG-UI event protocol for real-time
    streaming of agent responses to frontend applications.

    Events emitted:
    - RUN_STARTED
    - TEXT_MESSAGE_START
    - TEXT_MESSAGE_CONTENT (streaming)
    - TEXT_MESSAGE_END
    - RUN_FINISHED
    """
    try:
        body = await request.json()
        messages = body.get("messages", [])

        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        # Get the last user message as the query
        query = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                query = msg.get("content")
                break

        if not query:
            raise HTTPException(status_code=400, detail="No user message found")

        logger.info(f"AG-UI request: {query[:100]}...")

        from src.agui_agent import agui_stream_generator

        return StreamingResponse(
            agui_stream_generator(query),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"AG-UI error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/copilotkit")
async def copilotkit_endpoint(request: Request):
    """
    CopilotKit-specific endpoint.

    Compatible with CopilotKit's useCoAgent and useCopilotAction hooks.
    """
    try:
        body = await request.json()

        # Handle CopilotKit action requests
        action = body.get("action")
        if action == "research":
            query = body.get("parameters", {}).get("query")
            if not query:
                raise HTTPException(status_code=400, detail="Query required")

            from src.agent import create_agent
            agent = create_agent()
            result = agent.research(query)

            return JSONResponse({
                "success": True,
                "result": result.content,
            })

        # Handle chat messages
        messages = body.get("messages", [])
        if messages:
            query = None
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    query = msg.get("content")
                    break

            if query:
                from src.agui_agent import agui_stream_generator
                return StreamingResponse(
                    agui_stream_generator(query),
                    media_type="text/event-stream",
                )

        raise HTTPException(status_code=400, detail="Invalid request format")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"CopilotKit error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/research")
async def research_endpoint(request: ResearchRequest):
    """
    Simple research endpoint (non-streaming).
    """
    try:
        from src.agent import create_agent

        logger.info(f"Research request: {request.query[:100]}...")

        agent = create_agent()
        result = agent.research(request.query)

        return {
            "success": result.success,
            "query": result.query,
            "report": result.content,
        }

    except Exception as e:
        logger.exception(f"Research error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/research/stream")
async def research_stream_endpoint(request: ResearchRequest):
    """
    Streaming research endpoint using AG-UI events.
    """
    from src.agui_agent import agui_stream_generator

    return StreamingResponse(
        agui_stream_generator(request.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# ============================================================================
# LangGraph Endpoint for CopilotKit
# ============================================================================

@app.post("/langgraph")
async def langgraph_endpoint(request: Request):
    """
    LangGraph agent endpoint for CopilotKit integration.

    Uses the LangGraph-based agent with tool calling support.
    """
    try:
        body = await request.json()
        messages = body.get("messages", [])

        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        from langchain_core.messages import AIMessage, HumanMessage

        from src.agui_agent import get_langgraph_agent

        # Convert messages to LangChain format
        lc_messages = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            if role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))

        # Run the agent
        graph = get_langgraph_agent()
        result = graph.invoke({"messages": lc_messages})

        # Extract final response
        final_messages = result.get("messages", [])
        response_content = ""
        for msg in reversed(final_messages):
            if isinstance(msg, AIMessage) and msg.content:
                response_content = msg.content
                break

        return {
            "role": "assistant",
            "content": response_content,
        }

    except Exception as e:
        logger.exception(f"LangGraph error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "api_agui:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

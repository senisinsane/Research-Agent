"""
FastAPI REST API for the Web Research Agent.

Provides HTTP endpoints for research queries with async support.
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv()

from src.agent import ResearchAgent, create_agent
from src.config import get_settings
from src.exceptions import ResearchAgentError
from src.logging_config import get_logger, setup_logging

logger = get_logger(__name__)

# Global agent instance (initialized on startup)
_agent: ResearchAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agent on startup, cleanup on shutdown."""
    global _agent

    # Startup
    logger.info("Initializing Research Agent...")
    settings = get_settings()
    setup_logging(level=settings.log_level)
    _agent = create_agent()
    logger.info(f"Agent initialized with model: {_agent.model}")
    logger.info(f"Available tools: {_agent.available_tools}")

    yield

    # Shutdown
    logger.info("Shutting down Research Agent...")
    _agent = None


# Create FastAPI app
app = FastAPI(
    title="Web Research Agent API",
    description="Autonomous web research agent that searches, synthesizes, and reports",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for web frontends
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

class ResearchRequest(BaseModel):
    """Request model for research queries."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="The research query to investigate",
        examples=["What are the latest trends in AI?"],
    )
    model: str | None = Field(
        default=None,
        description="Override the default OpenAI model",
    )


class ResearchResponse(BaseModel):
    """Response model for research results."""

    success: bool = Field(description="Whether the research completed successfully")
    query: str = Field(description="The original query")
    report: str | None = Field(default=None, description="The research report")
    error: str | None = Field(default=None, description="Error message if failed")


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    model: str
    tools: list[str]


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Web Research Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["Info"])
async def health_check():
    """Check API health and agent status."""
    if _agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    return HealthResponse(
        status="healthy",
        model=_agent.model,
        tools=_agent.available_tools,
    )


@app.post("/research", response_model=ResearchResponse, tags=["Research"])
async def research(request: ResearchRequest):
    """
    Execute a research query and return a structured report.

    This endpoint accepts a research question and returns a comprehensive
    report with findings, analysis, and sources.
    """
    if _agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    logger.info(f"Research request: {request.query[:100]}...")

    try:
        # Use the global agent or create a new one with custom model
        agent = _agent
        if request.model and request.model != _agent.model:
            agent = create_agent(model=request.model)

        result = agent.research(request.query)

        return ResearchResponse(
            success=result.success,
            query=result.query,
            report=result.content,
        )

    except ResearchAgentError as e:
        logger.error(f"Research error: {e}")
        return ResearchResponse(
            success=False,
            query=request.query,
            error=str(e),
        )
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/research/async", response_model=ResearchResponse, tags=["Research"])
async def research_async(request: ResearchRequest):
    """
    Execute a research query asynchronously.

    Same as /research but uses async execution for better concurrency.
    """
    if _agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    logger.info(f"Async research request: {request.query[:100]}...")

    try:
        result = await _agent.research_async(request.query)

        return ResearchResponse(
            success=result.success,
            query=result.query,
            report=result.content,
        )

    except ResearchAgentError as e:
        logger.error(f"Research error: {e}")
        return ResearchResponse(
            success=False,
            query=request.query,
            error=str(e),
        )
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

# Web Research Agent 🔍

A production-ready autonomous web research agent built with LangChain, LangGraph, and OpenAI. This agent accepts natural language research queries, intelligently breaks them into sub-questions, searches the web for current information, and synthesizes findings into professional, structured reports.

## Features

- 🤖 **Autonomous Research** - Automatically plans, searches, and synthesizes information
- 🔎 **Multi-Provider Search** - Supports Tavily, SerpAPI, and DuckDuckGo
- 📊 **Structured Reports** - Clean, professional output with sources and citations
- 🌐 **REST API** - FastAPI backend with async support
- 🖥️ **React Frontend** - Modern chat interface with markdown rendering
- 🐳 **Docker Ready** - Multi-stage containerized deployment
- ☁️ **Cloud Deploy** - Railway, Render, and Fly.io configs included
- 📅 **Real-time Date Aware** - Always searches with current date context
- ⚙️ **Type-Safe Configuration** - Pydantic-based settings management
- 🛡️ **Production-Ready** - Proper error handling, logging, and security best practices

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Query                               │
│              (CLI / REST API / Chat Frontend)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 LangGraph ReAct Agent                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Planning Phase                         │  │
│  │    • Analyze research goal                                │  │
│  │    • Decompose into sub-questions                         │  │
│  │    • Prioritize information needs                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Research Phase                          │  │
│  │    • Tavily Search (AI-optimized, primary)                │  │
│  │    • SerpAPI (Google results)                             │  │
│  │    • DuckDuckGo (free fallback)                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Synthesis Phase                         │  │
│  │    • Cross-reference sources                              │  │
│  │    • Resolve conflicts                                    │  │
│  │    • Generate structured report                           │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Structured Report                             │
│    • Objective       • Pros & Cons                              │
│    • Key Findings    • Final Recommendation                     │
│    • Analysis        • Sources                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
web-research-agent/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Pydantic settings management
│   ├── exceptions.py         # Custom exception classes
│   ├── logging_config.py     # Structured logging setup
│   ├── prompts.py            # System prompts with real-time date
│   ├── agent.py              # ResearchAgent class (LangGraph)
│   ├── agui_agent.py         # AG-UI Protocol streaming agent
│   └── tools/
│       ├── __init__.py       # Tool exports
│       ├── registry.py       # Tool registry and discovery
│       ├── tavily_search.py  # Tavily search (primary)
│       ├── serpapi_search.py # SerpAPI Google search
│       └── duckduckgo_search.py  # DuckDuckGo fallback
├── frontend/                 # Next.js React UI
│   ├── app/
│   │   ├── page.tsx          # Chat interface component
│   │   ├── layout.tsx        # Root layout
│   │   ├── globals.css       # Tailwind styles
│   │   └── api/research/     # Research API proxy route
│   ├── package.json
│   └── tailwind.config.ts
├── main.py                   # CLI entry point
├── api.py                    # FastAPI REST API
├── api_agui.py               # AG-UI Protocol API server
├── Dockerfile                # Multi-stage container build
├── docker-compose.yml        # Local Docker setup
├── render.yaml               # Render deployment
├── railway.json              # Railway deployment
├── fly.toml                  # Fly.io deployment
├── Procfile                  # Process definition
├── DEPLOYMENT.md             # Deployment guide
├── pyproject.toml            # Python packaging & tooling config
├── requirements.txt          # Python dependencies
└── requirements-api.txt      # API-specific dependencies
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- OpenAI API key

### Option 1: CLI Usage

```bash
# Clone the repository
git clone https://github.com/senisinsane/Research-Agent.git
cd Research-Agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Run research
python main.py "What are the latest trends in AI?"
```

### Option 2: REST API

```bash
# Start the API server
python api.py

# Or with AG-UI Protocol support
python api_agui.py

# Make a request
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is quantum computing?"}'
```

### Option 3: Full Stack (Frontend + Backend)

```bash
# Terminal 1: Start the backend
python api_agui.py

# Terminal 2: Start the frontend
cd frontend
npm install
npm run dev

# Open http://localhost:3000 in your browser
```

### Option 4: Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# API available at http://localhost:8000
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | - | OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Model to use |
| `OPENAI_TEMPERATURE` | No | `0.0` | Response temperature |
| `TAVILY_API_KEY` | ⭐ Recommended | - | Tavily API key ([free tier](https://tavily.com)) |
| `SERPAPI_API_KEY` | No | - | SerpAPI key for Google search |
| `MAX_ITERATIONS` | No | `25` | Max agent iterations |
| `SEARCH_MAX_RESULTS` | No | `5` | Results per search query |
| `LOG_LEVEL` | No | `WARNING` | Logging level |

### Search Providers

| Provider | API Key | Best For |
|----------|---------|----------|
| **Tavily** | Required | AI-optimized results (recommended) |
| **SerpAPI** | Required | Google search results |
| **DuckDuckGo** | None | Free fallback (always available) |

The agent automatically uses available providers. Configure Tavily for best results.

## API Reference

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and available endpoints |
| `/health` | GET | Health check with configuration status |
| `/research` | POST | Execute research query |
| `/research/stream` | POST | Streaming research with AG-UI events |
| `/docs` | GET | Interactive Swagger documentation |

### POST /research

Request:
```json
{
  "query": "Your research question"
}
```

Response:
```json
{
  "success": true,
  "query": "Your research question",
  "report": "**Objective**: This report investigates...\n\n**Key Findings**:..."
}
```

## CLI Usage

### Basic Usage

```bash
python main.py "your research query"
```

### With Options

```bash
# Use a specific model
python main.py "Compare React vs Vue.js" --model gpt-4o

# Enable verbose logging
python main.py "Latest AI developments" --verbose

# Save to file
python main.py "Elon Musk net worth" --output report.txt

# Increase iteration limit
python main.py "Complex research topic" --max-iterations 40
```

### CLI Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `query` | - | Required | Research query |
| `--model` | - | From config | OpenAI model |
| `--max-iterations` | - | `25` | Max iterations |
| `--verbose` | `-v` | `False` | Debug logging |
| `--output` | `-o` | stdout | Output file |

## Output Format

Reports follow this structure:

1. **Objective** - What was researched
2. **Key Findings** - 3-5 critical discoveries
3. **Detailed Analysis** - In-depth exploration with context
4. **Pros & Cons** - Balanced assessment
5. **Final Recommendation** - Evidence-based conclusion
6. **Sources** - Cited references with URLs

## Programmatic Usage

```python
from src.agent import create_agent

# Create agent
agent = create_agent(model="gpt-4o-mini")

# Run research
result = agent.research("What is quantum computing?")

# Access result
print(result.content)
print(f"Success: {result.success}")
print(f"Query: {result.query}")
```

### Async Usage

```python
import asyncio
from src.agent import create_agent

async def main():
    agent = create_agent()
    result = await agent.research_async("Latest AI news")
    print(result.content)

asyncio.run(main())
```

## Error Handling

```python
from src.exceptions import (
    ConfigurationError,
    AgentExecutionError,
    EmptyResponseError,
    SearchProviderUnavailableError,
)

try:
    result = agent.research(query)
except ConfigurationError as e:
    print(f"Config issue: {e}")
except AgentExecutionError as e:
    print(f"Agent error: {e}")
except EmptyResponseError as e:
    print(f"No response generated: {e}")
```

## Deployment

### Quick Deploy Options

| Platform | Configuration |
|----------|---------------|
| **Railway** | `railway.json` |
| **Render** | `render.yaml` |
| **Fly.io** | `fly.toml` |
| **Docker** | `Dockerfile` + `docker-compose.yml` |

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Docker Deployment

```bash
# Build image
docker build -t research-agent .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  research-agent
```

## Development

### Install Dev Dependencies

```bash
pip install -e ".[dev]"
```

### Code Quality

```bash
# Lint code
ruff check .

# Format code
black src/ main.py api.py api_agui.py

# Type check
mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html
```

## Adding a New Search Provider

1. Create `src/tools/your_provider.py`:

```python
from langchain_core.tools import tool
from src.config import get_settings
from src.logging_config import get_logger

logger = get_logger(__name__)

@tool
def your_search(query: str, max_results: int = 5) -> str:
    """Search description for the LLM."""
    settings = get_settings()
    # Your implementation
    return formatted_results
```

2. Register in `src/tools/registry.py`:

```python
from src.tools.your_provider import your_search

_TOOL_REGISTRY["your_search"] = your_search
```

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, LangChain, LangGraph
- **Frontend**: Next.js 14, React 18, Tailwind CSS
- **AI**: OpenAI GPT-4o-mini (default), GPT-4o
- **Search**: Tavily, SerpAPI, DuckDuckGo
- **Deployment**: Docker, Railway, Render, Fly.io

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**Repository**: [github.com/senisinsane/Research-Agent](https://github.com/senisinsane/Research-Agent)

Built with [LangChain](https://langchain.com), [LangGraph](https://langchain-ai.github.io/langgraph/), and [OpenAI](https://openai.com)

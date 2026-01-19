# Web Research Agent 🔍

A production-ready autonomous web research agent built with LangChain and OpenAI. This agent accepts natural language research queries, intelligently breaks them into sub-questions, searches the web for current information, and synthesizes findings into professional, structured reports.

## Features

- 🤖 **Autonomous Research** - Automatically plans, searches, and synthesizes information
- 🔎 **Multi-Provider Search** - Supports Tavily, SerpAPI, and DuckDuckGo
- 📊 **Structured Reports** - Clean, professional output with sources
- ⚙️ **Type-Safe Configuration** - Pydantic-based settings management
- 🛡️ **Production-Ready** - Proper error handling, logging, and best practices
- 🔌 **Extensible** - Easy to add new search providers or tools

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Query                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Research Agent                              │
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
│  │    • Tavily Search (AI-optimized)                         │  │
│  │    • SerpAPI (Google results)                             │  │
│  │    • DuckDuckGo (fallback)                                │  │
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
│   ├── prompts.py            # System and human prompts
│   ├── agent.py              # ResearchAgent class
│   └── tools/
│       ├── __init__.py       # Tool exports
│       ├── registry.py       # Tool registry and discovery
│       ├── tavily_search.py  # Tavily search implementation
│       ├── serpapi_search.py # SerpAPI search implementation
│       └── duckduckgo_search.py  # DuckDuckGo fallback
├── main.py                   # CLI entry point
├── pyproject.toml            # Modern Python packaging
├── requirements.txt          # Dependencies
├── .env.example              # Environment template
└── README.md                 # Documentation
```

## Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/web-research-agent.git
cd web-research-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
```

### 3. Run Research

```bash
python main.py "What are the latest trends in AI?"
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | - | OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Model to use |
| `OPENAI_TEMPERATURE` | No | `0.0` | Response temperature |
| `TAVILY_API_KEY` | ⭐ Recommended | - | Tavily API key ([free](https://tavily.com)) |
| `SERPAPI_API_KEY` | No | - | SerpAPI key |
| `MAX_ITERATIONS` | No | `25` | Max agent iterations |
| `LOG_LEVEL` | No | `WARNING` | Logging level |

### Search Providers

| Provider | API Key | Best For |
|----------|---------|----------|
| **Tavily** | Required | AI-optimized results (recommended) |
| **SerpAPI** | Required | Google search results |
| **DuckDuckGo** | None | Free fallback |

## Usage

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

### Programmatic Usage

```python
from src.agent import create_agent

# Create agent
agent = create_agent(model="gpt-4o-mini")

# Run research
result = agent.research("What is quantum computing?")

# Access result
print(result.content)
print(f"Success: {result.success}")
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

## Output Format

Reports are structured with these sections:

1. **Objective** - What was researched
2. **Key Findings** - 3-5 critical discoveries
3. **Detailed Analysis** - In-depth exploration
4. **Pros & Cons** - Balanced assessment
5. **Final Recommendation** - Evidence-based conclusion
6. **Sources** - Cited references

## Error Handling

The agent handles various failure modes gracefully:

```python
from src.exceptions import (
    ConfigurationError,
    SearchError,
    AgentExecutionError,
    EmptyResponseError,
)

try:
    result = agent.research(query)
except ConfigurationError as e:
    print(f"Config issue: {e}")
except SearchError as e:
    print(f"Search failed ({e.provider}): {e}")
except AgentExecutionError as e:
    print(f"Agent error: {e}")
```

## Development

### Install Dev Dependencies

```bash
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code
black src/ main.py

# Lint code
ruff check src/ main.py

# Type check
mypy src/

# Run tests
pytest
```

## Extending

### Add a New Search Provider

1. Create `src/tools/your_provider.py`:

```python
from langchain_core.tools import tool
from src.logging_config import get_logger

logger = get_logger(__name__)

@tool
def your_search(query: str, max_results: int = 5) -> str:
    """Your search tool description."""
    # Implementation
    pass
```

2. Register in `src/tools/registry.py`:

```python
from src.tools.your_provider import your_search

_TOOL_REGISTRY["your_search"] = your_search
```

## License

MIT License - See [LICENSE](LICENSE) for details.

---

Built with [LangChain](https://langchain.com), [LangGraph](https://langchain-ai.github.io/langgraph/), and [OpenAI](https://openai.com)

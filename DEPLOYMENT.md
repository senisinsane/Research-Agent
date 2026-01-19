# Deployment Guide 🚀

This guide covers deploying the Web Research Agent to various platforms.

## Table of Contents

- [Local Docker](#local-docker)
- [Railway](#railway-recommended)
- [Render](#render)
- [Fly.io](#flyio)
- [AWS](#aws)
- [Google Cloud Run](#google-cloud-run)

---

## Local Docker

### Quick Start

```bash
# Build and run with docker-compose
docker-compose up --build

# Or build manually
docker build -t research-agent .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-xxx \
  -e TAVILY_API_KEY=tvly-xxx \
  research-agent
```

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Research query
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is quantum computing?"}'
```

---

## Railway (Recommended)

Railway offers the easiest deployment with automatic builds.

### Steps

1. **Create Railway Account**: https://railway.app

2. **Install Railway CLI** (optional):
   ```bash
   npm install -g @railway/cli
   railway login
   ```

3. **Deploy**:
   ```bash
   # From project directory
   railway init
   railway up
   ```
   
   Or connect GitHub repo in Railway dashboard.

4. **Set Environment Variables** in Railway dashboard:
   - `OPENAI_API_KEY` = your key
   - `TAVILY_API_KEY` = your key (optional)
   - `SERPAPI_API_KEY` = your key (optional)

5. **Get URL**: Railway provides a public URL automatically.

### Cost
- Free tier: $5/month credit
- Hobby: $5/month

---

## Render

### Steps

1. **Create Render Account**: https://render.com

2. **Connect GitHub**: Link your repository

3. **Create Web Service**:
   - Build Command: `pip install -r requirements.txt -r requirements-api.txt`
   - Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables**:
   - `OPENAI_API_KEY`
   - `TAVILY_API_KEY`
   - `SERPAPI_API_KEY`

5. **Deploy**: Render auto-deploys on push

### Cost
- Free tier: 750 hours/month (spins down after inactivity)
- Starter: $7/month

---

## Fly.io

### Steps

1. **Install flyctl**:
   ```bash
   # macOS
   brew install flyctl
   
   # Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**:
   ```bash
   fly auth login
   ```

3. **Launch** (first time):
   ```bash
   fly launch
   # Choose region, accept defaults
   ```

4. **Set Secrets**:
   ```bash
   fly secrets set OPENAI_API_KEY=sk-xxx
   fly secrets set TAVILY_API_KEY=tvly-xxx
   ```

5. **Deploy**:
   ```bash
   fly deploy
   ```

6. **Get URL**:
   ```bash
   fly status
   # URL: https://research-agent.fly.dev
   ```

### Cost
- Free tier: 3 shared VMs
- Pay as you go after

---

## AWS

### Option 1: AWS App Runner (Easiest)

1. Push to ECR:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
   
   docker build -t research-agent .
   docker tag research-agent:latest <account>.dkr.ecr.us-east-1.amazonaws.com/research-agent:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/research-agent:latest
   ```

2. Create App Runner service in AWS Console pointing to ECR image

3. Set environment variables in App Runner configuration

### Option 2: AWS Lambda (Serverless)

Use [Mangum](https://github.com/jordaneremieff/mangum) adapter:

```python
# lambda_handler.py
from mangum import Mangum
from api import app

handler = Mangum(app)
```

Deploy with AWS SAM or Serverless Framework.

---

## Google Cloud Run

### Steps

1. **Install gcloud CLI**: https://cloud.google.com/sdk/docs/install

2. **Authenticate**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Build and Push**:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/research-agent
   ```

4. **Deploy**:
   ```bash
   gcloud run deploy research-agent \
     --image gcr.io/YOUR_PROJECT_ID/research-agent \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars "OPENAI_API_KEY=sk-xxx,TAVILY_API_KEY=tvly-xxx"
   ```

### Cost
- Free tier: 2 million requests/month
- Pay per use after

---

## API Endpoints

Once deployed, your API provides:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/research` | POST | Sync research |
| `/research/async` | POST | Async research |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc docs |

### Example Request

```bash
curl -X POST https://your-app.railway.app/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Latest AI trends 2026"}'
```

### Example Response

```json
{
  "success": true,
  "query": "Latest AI trends 2026",
  "report": "**Objective**: This report investigates..."
}
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | OpenAI API key |
| `TAVILY_API_KEY` | ⭐ | Tavily search (recommended) |
| `SERPAPI_API_KEY` | ❌ | Google search |
| `OPENAI_MODEL` | ❌ | Model (default: gpt-4o-mini) |
| `LOG_LEVEL` | ❌ | Logging level (default: INFO) |
| `PORT` | ❌ | Server port (default: 8000) |

---

## Monitoring

### Health Checks

All deployment configs include health checks at `/health`.

### Logging

Set `LOG_LEVEL=DEBUG` for detailed logs in production.

### Metrics

Consider adding:
- Prometheus metrics endpoint
- OpenTelemetry tracing
- Sentry for error tracking

---

## Security Considerations

1. **Never commit API keys** - Use environment variables
2. **Enable HTTPS** - All platforms provide this
3. **Rate limiting** - Consider adding for public APIs
4. **Authentication** - Add API keys or OAuth for production

```python
# Example: Add API key authentication
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

@app.post("/research")
async def research(request: ResearchRequest, api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403)
    # ... rest of endpoint
```

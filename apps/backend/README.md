# Security Analyst Backend

FastAPI backend for the Security Analyst platform.

## Features

- 8 Security Framework Agents (STPA-SEC, STRIDE, PASTA, DREAD, etc.)
- Real-time WebSocket updates
- LlamaIndex for intelligent context management
- Multi-provider LLM support (Anthropic, OpenAI, Groq, Gemini, Ollama)
- Database-first settings configuration

## Running Locally

```bash
# Using the convenience script
./run-backend-local.sh

# Or manually
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## API Documentation

Once running, visit:
- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
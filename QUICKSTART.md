# Quick Start Guide

## Prerequisites

1. **Docker & Docker Compose**
   - Install Docker Desktop (includes Docker Compose)
   - Ensure Docker is running

2. **Clone and Setup**
   ```bash
   git clone https://github.com/AISecurityAssurance/prototype1
   cd prototype1
   git checkout feature/step1-analysis-engine
   chmod +x ai-sec
   ```

## Quick Test - Demo Mode

No build required! The script handles everything:

```bash
./ai-sec demo
```

This will:
- Automatically start PostgreSQL if needed
- Build the CLI container on first run
- Load the pre-packaged banking analysis demo
- Display analysis results

## Running Your First Analysis

### Option 1: Using GPT-4 (Recommended for testing)
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Run analysis
./ai-sec analyze --config configs/test-gpt4-standard.yaml
```

### Option 2: Using Ollama (Local, no API key needed)
```bash
# First, install and start Ollama
# See: https://ollama.ai
ollama pull mixtral:instruct

# Run analysis
./ai-sec analyze --config configs/test-ollama-standard.yaml
```

## Web Interface

To start the full web interface:

```bash
./ai-sec web
```

Access at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## First-Time Setup Notes

The first run will:
1. Pull Docker images (postgres, python, etc.)
2. Build the CLI container
3. Create the database
4. Run migrations

This may take 2-5 minutes. Subsequent runs will be much faster.

## Common Commands

```bash
# View help
./ai-sec

# Check service status
./ai-sec status

# View logs
./ai-sec logs

# Stop all services
./ai-sec stop

# Open development shell
./ai-sec shell
```

## Troubleshooting

### "Docker is not running"
Start Docker Desktop or run: `sudo systemctl start docker`

### "Permission denied"
Make the script executable: `chmod +x ai-sec`

### Database connection issues
Check PostgreSQL is healthy: `./ai-sec status`

### Ollama connection failed
If using Ollama in Docker, update config to use:
```yaml
api_endpoint: "http://host.docker.internal:11434"
```

## Next Steps

1. Review `DOCKER_PROFILES.md` for advanced usage
2. Check `apps/backend/STEP1_TESTING.md` for detailed testing
3. See example configs in `apps/backend/configs/`
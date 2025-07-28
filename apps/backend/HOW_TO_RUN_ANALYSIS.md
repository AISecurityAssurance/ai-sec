# How to Run STPA-Sec Step 1 Analysis

This guide explains how to run a live Step 1 analysis using the demo banking system.

## Quick Start

```bash
# From the project root directory
cd /path/to/prototype1

# View the demo analysis
./ai-sec demo

# Run a live analysis (requires API key)
export OPENAI_API_KEY='your-key-here'
./ai-sec analyze --config apps/backend/configs/gpt4-turbo-standard.yaml
```

## Prerequisites

1. **OpenAI API Key** (for GPT-4 Turbo)
   - Sign up at https://platform.openai.com
   - Create an API key
   - Set it as environment variable: `export OPENAI_API_KEY='your-key-here'`

2. **Docker** installed and running

3. **PostgreSQL** database running (either local or in Docker)

## Current State

We have implemented:
- ✅ All Step 1 agents (Mission, Loss, Hazard, Stakeholder, Security Constraints, System Boundaries)
- ✅ Model provider abstraction (OpenAI, Ollama support)
- ✅ Standard and enhanced (ASI-ARCH) execution modes
- ✅ Demo mode with pre-packaged analysis
- ✅ CLI interface for running analyses

## Running the Demo (No API Key Required)

```bash
# From the project root directory
./ai-sec demo
```

This shows a complete Step 1 analysis with all components.

## Running a Live Analysis

### Option 1: Using ai-sec CLI (Recommended)

```bash
# From project root
export OPENAI_API_KEY='your-key-here'

# Run standard analysis with GPT-4 Turbo
./ai-sec analyze --config apps/backend/configs/gpt4-turbo-standard.yaml

# Run enhanced ASI-ARCH analysis
./ai-sec analyze --config apps/backend/configs/gpt4-turbo-enhanced.yaml

# Open shell for debugging
./ai-sec shell
```

### Option 2: Local Python Environment

1. **Install dependencies:**
   ```bash
   pip install -r requirements-cli.txt
   ```

2. **Apply database migrations:**
   ```bash
   # Make sure PostgreSQL is running
   python3 -c "from core.database import run_migrations; import asyncio; asyncio.run(run_migrations())"
   ```

3. **Run the analysis:**
   ```bash
   export OPENAI_API_KEY='your-key-here'
   python3 cli.py analyze --config configs/gpt4-turbo-standard.yaml
   ```

### Option 3: Using Ollama (Free, Local)

1. **Install Ollama:**
   ```bash
   # macOS
   brew install ollama
   
   # Start Ollama
   ollama serve
   ```

2. **Pull a model:**
   ```bash
   ollama pull llama2  # or mistral, codellama, etc.
   ```

3. **Run analysis with local model:**
   ```bash
   ./ai-sec analyze --config apps/backend/configs/standard-analysis.yaml
   ```

## Available ai-sec Commands

```bash
# View demo analysis
./ai-sec demo

# Run analysis with config file
./ai-sec analyze --config <path-to-config>

# Open interactive shell in container
./ai-sec shell

# Start web interface
./ai-sec web

# Check service status
./ai-sec status

# View logs
./ai-sec logs [service-name]

# Stop all services
./ai-sec stop

# Clean up (remove containers and volumes)
./ai-sec clean
```

## Configuration Files

- `configs/gpt4-turbo-standard.yaml` - GPT-4 Turbo, standard mode
- `configs/enhanced-analysis.yaml` - Enhanced ASI-ARCH mode
- `configs/standard-analysis.yaml` - Standard mode with Ollama

## Expected Output

A complete analysis produces:
1. JSON files for each agent in `analyses/[name]/results/`
2. Markdown report at `analyses/[name]/step1_analysis_report.md`
3. Analysis log with execution details

## Troubleshooting

1. **"OPENAI_API_KEY not set"**
   - Set the environment variable: `export OPENAI_API_KEY='sk-...'`

2. **Database connection errors**
   - Ensure PostgreSQL is running: `docker ps | grep postgres`
   - Check connection settings in config files

3. **Module import errors**
   - Use Docker (Option 1) or install dependencies (Option 2)

## Next Steps

Once you have API access:
1. Run standard analysis
2. Run enhanced ASI-ARCH analysis  
3. Compare results
4. Iterate on prompts and agent logic

For development without API keys:
- Use the demo mode to understand the expected output
- Implement and test with Ollama locally
- Mock API responses for testing
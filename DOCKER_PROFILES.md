# Docker Compose Profiles Guide

## Overview

The project uses Docker Compose profiles to support different usage scenarios:

- **demo** - Full web interface (frontend + backend + database)
- **cli** - Command-line analysis only
- **dev** - Development tools (pgAdmin)
- **full** - Everything including Redis cache

## Quick Start

### Using the `ai-sec` wrapper script (Recommended)

```bash
# Make script executable (first time only)
chmod +x ai-sec

# Load demo analysis
./ai-sec demo

# Run analysis
./ai-sec analyze --config configs/standard-analysis.yaml

# Start web interface
./ai-sec web

# Open interactive shell
./ai-sec shell
```

### Using Docker Compose directly

```bash
# Start only the database
docker compose up -d postgres

# Start web interface (demo profile)
docker compose --profile demo up -d

# Run CLI commands
docker compose run --rm cli python cli.py demo

# Start with development tools
docker compose --profile dev up -d

# Start everything
docker compose --profile full up -d
```

## Profiles Explained

### Default (no profile)
- Only starts PostgreSQL database
- Minimal setup for local development

### `demo` Profile
- PostgreSQL database
- Backend API (FastAPI)
- Frontend web app (React)
- Perfect for demonstrations

### `cli` Profile
- PostgreSQL database
- CLI container for running analyses
- Mounts local directories for input/output

### `dev` Profile
- Everything from default
- pgAdmin for database management

### `full` Profile
- Everything from demo
- Redis for caching
- Production-like environment

## Common Tasks

### Running Step 1 Analysis

```bash
# Using wrapper
./ai-sec analyze --config configs/standard-analysis.yaml

# Using docker compose
docker compose run --rm cli python cli.py analyze --config configs/standard-analysis.yaml
```

### Viewing Logs

```bash
# All services
./ai-sec logs

# Specific service
./ai-sec logs backend
```

### Database Access

```bash
# Direct psql access
docker compose exec postgres psql -U sa_user -d security_analyst

# pgAdmin (with dev profile)
docker compose --profile dev up -d
# Access at http://localhost:5050
```

### Clean Up

```bash
# Stop all services
./ai-sec stop

# Remove everything including volumes
./ai-sec clean
```

## Environment Variables

Create a `.env` file for configuration:

```env
# API Keys
OPENAI_API_KEY=your-key-here

# Ollama endpoint (if not using default)
OLLAMA_API_ENDPOINT=http://host.docker.internal:11434

# Database (usually not needed, uses defaults)
POSTGRES_USER=sa_user
POSTGRES_PASSWORD=sa_password
POSTGRES_DB=security_analyst
```

## Troubleshooting

### Container can't connect to Ollama
If running Ollama locally, use `host.docker.internal` instead of `localhost` in configurations.

### Database connection issues
Ensure PostgreSQL is healthy:
```bash
docker compose ps
docker compose logs postgres
```

### Permission issues
The `ai-sec` script handles most permission issues, but if needed:
```bash
sudo chown -R $USER:$USER ./analyses
```
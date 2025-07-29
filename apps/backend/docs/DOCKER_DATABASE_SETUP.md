# Docker-Based Database Setup

## Overview

This guide explains how to set up and test the database using Docker containers, which is the preferred development approach for this project.

## Prerequisites

- Docker and Docker Compose installed
- Make (optional, but recommended)
- Your LLM API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.)

## Quick Start

### 1. Set API Keys (Optional)

Export your API keys as environment variables:

```bash
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
```

Or create a `.env` file in the backend directory:
```bash
cd apps/backend
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Run Database Tests

The easiest way to test the database setup:

```bash
cd apps/backend
make db-test
```

Or manually:
```bash
cd apps/backend
./run_db_tests.sh
```

This script will:
1. Start PostgreSQL and Redis containers
2. Build the backend container
3. Run database setup
4. Execute all migrations
5. Run comprehensive tests
6. Insert demo data

### 3. Start Development Environment

```bash
# Start all services
make up

# Or start with live logs
make dev
```

## Available Commands

### Using Make (Recommended)

```bash
make help       # Show all available commands
make build      # Build backend Docker image
make up         # Start all services
make down       # Stop all services
make dev        # Start in development mode with logs
make db-test    # Run database tests
make shell      # Open shell in backend container
make db-shell   # Open PostgreSQL shell
make logs       # Show backend logs
make clean      # Clean up containers and volumes
make reset      # Full reset (clean + rebuild)
```

### Manual Docker Commands

```bash
# Start services
docker-compose -f docker-compose.yml up -d
docker-compose -f docker-compose.dev.yml up -d backend

# Run database tests
docker-compose -f docker-compose.dev.yml run --rm backend python test_database_setup.py

# Open backend shell
docker-compose -f docker-compose.dev.yml exec backend bash

# Open PostgreSQL shell
docker-compose exec postgres psql -U sa_user -d security_analyst

# View logs
docker-compose -f docker-compose.dev.yml logs -f backend
```

## Service URLs

Once running, services are available at:

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050
  - Email: `admin@securityanalyst.local`
  - Password: `admin`
- **Redis Commander**: http://localhost:8081

## Database Connection Details

When services are running in Docker:

- **Host**: `sa_postgres` (from within containers)
- **Host**: `localhost` (from your machine)
- **Port**: `5433` (PostgreSQL - mapped from internal 5432)
- **Redis Port**: `6380` (Redis - mapped from internal 6379)
- **Database**: `security_analyst`
- **User**: `sa_user`
- **Password**: `sa_password`

## Troubleshooting

### Container Issues

```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs sa_postgres
docker-compose logs sa_backend

# Restart services
make down && make up
```

### Database Connection Issues

1. Ensure PostgreSQL container is healthy:
   ```bash
   docker-compose ps | grep postgres
   ```

2. Test connection from backend container:
   ```bash
   make shell
   python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect(host='sa_postgres', user='sa_user', password='sa_password', database='security_analyst'))"
   ```

### Clean Slate

To completely reset everything:

```bash
make reset
```

Or manually:
```bash
docker-compose down -v  # Remove containers and volumes
docker-compose -f docker-compose.dev.yml build --no-cache
make db-test
```

## Development Workflow

### 1. Making Code Changes

The backend directory is mounted as a volume, so code changes are reflected immediately:

```python
# Edit files locally
# Changes are automatically picked up by the container
# FastAPI will auto-reload
```

### 2. Running Commands in Container

```bash
# Run any Python command
docker-compose -f docker-compose.dev.yml run --rm backend python your_script.py

# Run pytest
docker-compose -f docker-compose.dev.yml run --rm backend pytest

# Run specific test
docker-compose -f docker-compose.dev.yml run --rm backend pytest tests/test_specific.py
```

### 3. Database Operations

```bash
# Backup database
make db-backup

# Access PostgreSQL shell
make db-shell

# Run SQL directly
docker-compose exec postgres psql -U sa_user -d security_analyst -c "SELECT * FROM system_definitions;"
```

### 4. Installing New Dependencies

Add to `requirements.txt`, then:

```bash
make build  # Rebuild container with new dependencies
make up     # Start with new container
```

## VS Code Integration

For VS Code users, add this to `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "/usr/local/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.terminal.activateEnvironment": false,
  "docker.showExplorer": true
}
```

Use the "Remote - Containers" extension to develop inside the container.

## Production Considerations

This setup is for development. For production:

1. Use separate docker-compose.prod.yml
2. Use environment-specific .env files
3. Enable SSL/TLS for database connections
4. Use secrets management for API keys
5. Set up proper backup strategies

## Next Steps

After database setup is verified:

1. Start the API: `make up`
2. Visit http://localhost:8000/docs
3. Run an analysis using the demo data
4. Check pgAdmin to explore the database structure
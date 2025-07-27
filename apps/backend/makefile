# Makefile for Security Analysis Platform Backend

.PHONY: help build up down test db-test shell logs clean reset

# Default target
help:
	@echo "Security Analysis Platform Backend - Docker Commands"
	@echo "=================================================="
	@echo "make build      - Build backend Docker image"
	@echo "make up         - Start all services"
	@echo "make down       - Stop all services"
	@echo "make test       - Run all tests"
	@echo "make db-test    - Run database tests"
	@echo "make test-stpa-sec - Run STPA-Sec integration test"
	@echo "make shell      - Open shell in backend container"
	@echo "make logs       - Show backend logs"
	@echo "make clean      - Clean up containers and volumes"
	@echo "make reset      - Full reset (clean + rebuild)"
	@echo ""
	@echo "Database Management:"
	@echo "make db-migrate - Run database migrations"
	@echo "make db-shell   - Open PostgreSQL shell"
	@echo "make db-backup  - Backup database"
	@echo ""
	@echo "Development:"
	@echo "make dev        - Start in development mode"
	@echo "make format     - Format Python code"
	@echo "make lint       - Run linting"
	@echo "make run-script SCRIPT=file.py - Run a Python script"

# Build the backend image
build:
	docker-compose -f docker-compose.dev.yml build backend

# Start all services
up:
	docker-compose -f docker-compose.yml up -d
	docker-compose -f docker-compose.dev.yml up -d backend
	@echo ""
	@echo "Services started:"
	@echo "  API:            http://localhost:8000"
	@echo "  API Docs:       http://localhost:8000/docs"
	@echo "  pgAdmin:        http://localhost:5050"
	@echo "  Redis Commander: http://localhost:8081"

# Start in development mode with logs
dev:
	docker-compose -f docker-compose.yml up -d postgres redis
	docker-compose -f docker-compose.dev.yml up backend

# Stop all services
down:
	docker-compose -f docker-compose.dev.yml down
	docker-compose -f docker-compose.yml down

# Run all tests
test:
	docker-compose -f docker-compose.dev.yml run --rm backend pytest

# Run database tests specifically
db-test:
	./run_db_tests.sh

# Run STPA-Sec integration test
test-stpa-sec:
	docker-compose -f docker-compose.dev.yml run --rm backend python test_stpa_sec_integration.py

# Run a specific Python script in container
run-script:
	@if [ -z "$(SCRIPT)" ]; then \
		echo "Usage: make run-script SCRIPT=filename.py"; \
		exit 1; \
	fi
	docker-compose -f docker-compose.dev.yml run --rm backend python $(SCRIPT)

# Run database migrations
db-migrate:
	docker-compose -f docker-compose.dev.yml run --rm backend python test_database_setup.py

# Open shell in backend container
shell:
	docker-compose -f docker-compose.dev.yml exec backend bash

# Open PostgreSQL shell
db-shell:
	docker-compose -f docker-compose.yml exec postgres psql -U sa_user -d security_analyst

# Backup database
db-backup:
	@mkdir -p backups
	docker-compose -f docker-compose.yml exec postgres pg_dump -U sa_user security_analyst > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Database backed up to backups/backup_$$(date +%Y%m%d_%H%M%S).sql"

# Show logs
logs:
	docker-compose -f docker-compose.dev.yml logs -f backend

# Clean up
clean:
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose -f docker-compose.yml down -v
	@echo "All containers and volumes removed"

# Full reset
reset: clean build db-migrate
	@echo "Full reset completed"

# Format code
format:
	docker-compose -f docker-compose.dev.yml run --rm backend black .
	docker-compose -f docker-compose.dev.yml run --rm backend isort .

# Lint code
lint:
	docker-compose -f docker-compose.dev.yml run --rm backend pylint src api
	docker-compose -f docker-compose.dev.yml run --rm backend mypy .
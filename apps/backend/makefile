.PHONY: help install install-dev setup-env setup-db run-dev run-prod test lint format clean docker-up docker-down migrate

# Default target
.DEFAULT_GOAL := help

# Python interpreter
PYTHON := python3.11

# Help command
help:
	@echo "Security Analyst Backend - Development Commands"
	@echo "==============================================="
	@echo "install        - Install production dependencies"
	@echo "install-dev    - Install development dependencies"
	@echo "setup-env      - Copy .env.example to .env"
	@echo "setup-db       - Initialize database with migrations"
	@echo "run-dev        - Run development server"
	@echo "run-prod       - Run production server"
	@echo "test           - Run tests"
	@echo "lint           - Run linting"
	@echo "format         - Format code"
	@echo "clean          - Clean cache files"
	@echo "docker-up      - Start Docker services"
	@echo "docker-down    - Stop Docker services"
	@echo "migrate        - Run database migrations"

# Install production dependencies
install:
	@echo "Installing production dependencies..."
	uv pip install -e .

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	uv pip install -e ".[dev]"

# Setup environment
setup-env:
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please update with your API keys."; \
	else \
		echo ".env file already exists."; \
	fi

# Setup database
setup-db:
	@echo "Setting up database..."
	alembic init -t async alembic
	alembic revision --autogenerate -m "Initial migration"
	alembic upgrade head

# Run development server
run-dev:
	@echo "Starting development server..."
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Run production server
run-prod:
	@echo "Starting production server..."
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Run tests
test:
	@echo "Running tests..."
	pytest -v --cov=. --cov-report=term-missing

# Run linting
lint:
	@echo "Running linters..."
	ruff check .
	mypy .

# Format code
format:
	@echo "Formatting code..."
	black .
	isort .
	ruff check --fix .

# Clean cache files
clean:
	@echo "Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Docker commands
docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d

# Stop Docker services
docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

# Run migrations
migrate:
	@echo "Running migrations..."
	alembic upgrade head

# Create new migration
migrate-new:
	@echo "Creating new migration..."
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

# Development setup (combines multiple commands)
dev-setup: install-dev setup-env docker-up setup-db
	@echo "Development environment setup complete!"
	@echo "Run 'make run-dev' to start the server."
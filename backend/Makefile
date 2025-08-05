.PHONY: help install install-dev test lint format clean run docker-build migrate init-db setup-dev pre-commit-setup pre-commit

# Default target
help:
	@echo "Backend Development Commands:"
	@echo "  install         - Install dependencies"
	@echo "  install-dev     - Install with dev dependencies"
	@echo "  test            - Run tests"
	@echo "  lint            - Run linting"
	@echo "  format          - Format code"
	@echo "  clean           - Clean cache and temporary files"
	@echo "  run             - Run the backend application"
	@echo "  docker-build    - Build Docker image"
	@echo "  migrate         - Run database migrations"
	@echo "  init-db         - Initialize database"
	@echo "  setup-dev       - Complete development setup"
	@echo "  pre-commit-setup- Setup pre-commit hooks"
	@echo "  pre-commit      - Run pre-commit checks"

# Install dependencies
install:
	uv sync

# Install dev dependencies
install-dev:
	uv sync --extra dev

# Run tests
test:
	uv run pytest tests/ -v --cov=app --cov-report=html

# Run linting
lint:
	uv run ruff check app/ tests/
	uv run mypy app/

# Format code
format:
	uv run black app/ tests/
	uv run isort app/ tests/

# Clean cache and temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

# Run the application
run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Build Docker image
docker-build:
	docker build -t analytic-agent-backend .

# Run database migrations
migrate:
	uv run alembic upgrade head

# Initialize database
init-db:
	uv run python scripts/init_db.py

# Create new migration
migration:
	uv run alembic revision --autogenerate -m "$(message)"

# Complete development setup
setup-dev:
	uv run python scripts/setup_dev.py

# Setup pre-commit hooks
pre-commit-setup:
	uv run pre-commit install

# Run pre-commit on all files
pre-commit:
	uv run pre-commit run --all-files

# Development setup
dev-setup: install-dev
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
	@echo "Then run: make init-db"

# Full development environment
dev: dev-setup
	make run 
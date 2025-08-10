.PHONY: help install test lint format clean run docker-build docker-run docker-stop migrate init-db

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  clean       - Clean cache and temporary files"
	@echo "  run         - Run the application"
	@echo "  docker-build- Build Docker image"
	@echo "  docker-run  - Run with Docker Compose"
	@echo "  docker-stop - Stop Docker containers"
	@echo "  migrate     - Run database migrations"
	@echo "  init-db     - Initialize database"

# Install dependencies
install:
	uv sync

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
	docker build -t analytic-agent .

# Run with Docker Compose
docker-run:
	docker-compose up -d

# Stop Docker containers
docker-stop:
	docker-compose down

# Run database migrations
migrate:
	uv run alembic upgrade head

# Initialize database
init-db:
	uv run python scripts/init_db.py

# Create new migration
migration:
	uv run alembic revision --autogenerate -m "$(message)"

# Show logs
logs:
	docker-compose logs -f

# Shell into container
shell:
	docker-compose exec app bash

# Database shell
db-shell:
	docker-compose exec db psql -U analytic_user -d analytic_agent

# Production build
prod-build:
	docker build -t analytic-agent:prod --target production .

# Development setup
dev-setup: install
	cp env.example .env
	@echo "Please edit .env file with your configuration"
	@echo "Then run: make init-db"

# Complete development setup
setup-dev:
	uv run python scripts/setup_dev.py

# Install dev dependencies
install-dev:
	uv sync --extra dev

# Setup pre-commit hooks
pre-commit-setup:
	uv run pre-commit install

# Run pre-commit on all files
pre-commit:
	uv run pre-commit run --all-files

# Full development environment
dev: dev-setup
	docker-compose up -d db redis
	sleep 5
	make init-db
	make run

# Backend development
backend-dev:
	cd backend && make dev

# Frontend development
frontend-dev:
	cd frontend && docker-compose up -d

# Full stack development
full-dev:
	docker network create analytic-agent-network 2>/dev/null || true
	docker-compose -f docker-compose.dev.yml up -d

# Production deployment
prod:
	docker network create analytic-agent-network 2>/dev/null || true
	docker-compose up -d --build

# Stop all services
stop:
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

# Clean up networks
cleanup:
	docker network rm analytic-agent-network 2>/dev/null || true

# View logs
logs:
	docker-compose logs -f

# Backend logs
backend-logs:
	docker-compose logs -f backend

# Frontend logs
frontend-logs:
	docker-compose logs -f frontend

# Database management
db-shell:
	docker-compose exec db psql -U analytic_user -d analytic_agent

# Initialize database
init-db:
	cd backend && make init-db

# Run migrations
migrate:
	cd backend && make migrate

# Health check
health:
	@echo "Checking backend health..."
	@curl -f http://localhost:8000/api/v1/health/ || echo "Backend not responding"
	@echo "Checking frontend health..."
	@curl -f http://localhost:3000/health || echo "Frontend not responding" 
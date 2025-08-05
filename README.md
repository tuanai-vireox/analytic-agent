# Analytic Agent

A powerful analytic agent built with CrewAI and FastAPI backend, featuring a LibreChat frontend for interactive chat-based analysis.

## Features

- 🤖 Multi-agent AI system using CrewAI
- 🚀 FastAPI REST API backend
- 💬 Interactive chat interface with LibreChat
- 📊 Advanced data analysis capabilities
- 🔄 Asynchronous task processing
- 📝 Comprehensive logging and monitoring
- 🧪 Full test coverage
- 🐳 Docker support with docker-compose
- ⚡ Fast package management with uv

## Project Structure

```
analytic-agent/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection and session
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── api/               # API routes
│   │   ├── services/          # Business logic
│   │   ├── agents/            # CrewAI agents
│   │   └── utils/             # Utility functions
│   ├── tests/                 # Backend test files
│   ├── alembic/               # Database migrations
│   ├── scripts/               # Backend utility scripts
│   ├── pyproject.toml         # Backend dependencies
│   ├── uv.lock               # Locked dependencies
│   ├── Dockerfile            # Backend Docker image
│   └── .env.example          # Backend environment variables
├── frontend/                  # LibreChat frontend
│   ├── docker-compose.yml    # LibreChat configuration
│   ├── .env.example          # Frontend environment variables
│   └── README.md             # Frontend documentation
├── docker-compose.yml        # Main docker-compose for full stack
├── docker-compose.dev.yml    # Development docker-compose
├── .env.example              # Main environment variables
├── Makefile                  # Project-wide commands
└── README.md                 # This file
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)
- uv (recommended) or pip
- OpenAI API key

### Full Stack Deployment (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd analytic-agent
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Deploy the full stack:
```bash
docker-compose up -d
```

4. Access the applications:
- **LibreChat Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Development Setup

#### Backend Development

```bash
cd backend

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up development environment
make setup-dev

# Run the backend
make run
```

#### Frontend Development

```bash
cd frontend

# Start LibreChat in development mode
docker-compose -f docker-compose.dev.yml up -d
```

## Architecture

### Backend (FastAPI + CrewAI)
- **FastAPI** - High-performance web framework
- **CrewAI** - Multi-agent AI orchestration
- **PostgreSQL** - Primary database
- **Redis** - Caching and task queue
- **SQLAlchemy** - ORM for database operations

### Frontend (LibreChat)
- **LibreChat** - Open-source chat interface
- **React** - Frontend framework
- **WebSocket** - Real-time communication
- **Custom API Integration** - Connects to backend services

## API Integration

The LibreChat frontend is configured to communicate with the backend API through:

- **Chat Endpoints**: `/api/v1/chat/`
- **Analysis Endpoints**: `/api/v1/analysis/`
- **User Management**: `/api/v1/users/`

## Docker Compose Services

### Production Stack
- `backend` - FastAPI application
- `frontend` - LibreChat interface
- `db` - PostgreSQL database
- `redis` - Redis cache
- `nginx` - Reverse proxy (optional)

### Development Stack
- `backend-dev` - Backend with hot reload
- `frontend-dev` - LibreChat with development settings
- `db` - PostgreSQL database
- `redis` - Redis cache

## Configuration

### Environment Variables

#### Main Configuration (.env)
```bash
# Application Settings
APP_NAME=Analytic Agent
APP_VERSION=1.0.0
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:password@db:5432/analytic_agent

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Security
SECRET_KEY=your_secret_key

# LibreChat
LIBRECHAT_API_KEY=your_librechat_api_key
```

#### Backend Configuration (backend/.env)
```bash
# Backend-specific settings
DEBUG=False
LOG_LEVEL=INFO
CREWAI_VERBOSE=False
```

#### Frontend Configuration (frontend/.env)
```bash
# LibreChat settings
HOST=0.0.0.0
PORT=3000
JWT_SECRET=your_jwt_secret
```

## Development

### Running Tests

```bash
# Backend tests
cd backend && make test

# Frontend tests (if applicable)
cd frontend && npm test
```

### Code Quality

```bash
# Backend
cd backend && make lint
cd backend && make format

# Frontend
cd frontend && npm run lint
cd frontend && npm run format
```

### Database Management

```bash
# Create migration
cd backend && make migration message="description"

# Run migrations
cd backend && make migrate

# Initialize database
cd backend && make init-db
```

## Deployment

### Production Deployment

```bash
# Build and deploy
docker-compose -f docker-compose.yml up -d --build

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale backend=3
```

### Development Deployment

```bash
# Development stack
docker-compose -f docker-compose.dev.yml up -d

# With hot reload
docker-compose -f docker-compose.dev.yml up -d backend-dev
```

## Monitoring and Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Health checks
curl http://localhost:8000/api/v1/health/
curl http://localhost:3000/health
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License 
# Analytic Agent

A powerful analytic agent built with CrewAI and FastAPI that can perform complex data analysis tasks using AI agents.

## Features

- 🤖 Multi-agent AI system using CrewAI
- 🚀 FastAPI REST API for easy integration
- 📊 Advanced data analysis capabilities
- 🔄 Asynchronous task processing
- 📝 Comprehensive logging and monitoring
- 🧪 Full test coverage
- 🐳 Docker support
- ⚡ Fast package management with uv

## Project Structure

```
analytic-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection and session
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── api/                    # API routes
│   ├── services/               # Business logic
│   ├── agents/                 # CrewAI agents
│   └── utils/                  # Utility functions
├── tests/                      # Test files
├── alembic/                    # Database migrations
├── docker/                     # Docker configuration
├── scripts/                    # Utility scripts
├── pyproject.toml             # Project configuration and dependencies
├── uv.lock                    # Locked dependencies (uv)
├── .env.example               # Environment variables template
├── docker-compose.yml         # Docker compose configuration
└── README.md                  # This file
```

## Quick Start

### Prerequisites

- Python 3.9+
- uv (recommended) or pip
- PostgreSQL (optional, for production)
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd analytic-agent
```

2. Install uv (if not already installed):
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. Install dependencies:
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
# Using uv
uv run uvicorn app.main:app --reload

# Or using make
make run
```

The API will be available at `http://localhost:8000`

### Docker Setup

```bash
docker-compose up -d
```

## Package Management with uv

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management. Key commands:

```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --extra dev

# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Run commands in the virtual environment
uv run python script.py
uv run pytest
uv run uvicorn app.main:app --reload
```

## API Documentation

Once the application is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## Usage Examples

### Basic Analysis Request

```python
import requests

# Submit an analysis task
response = requests.post("http://localhost:8000/api/v1/analysis", json={
    "query": "Analyze the sales data for Q4 2023",
    "data_source": "sales_data.csv",
    "analysis_type": "trend_analysis"
})

task_id = response.json()["task_id"]

# Check task status
status_response = requests.get(f"http://localhost:8000/api/v1/analysis/{task_id}")
print(status_response.json())
```

## Development

### Running Tests

```bash
# Using uv
uv run pytest

# Or using make
make test
```

### Code Formatting

```bash
# Using uv
uv run black .
uv run isort .

# Or using make
make format
```

### Type Checking

```bash
# Using uv
uv run mypy app/

# Or using make
make lint
```

### Installing Development Dependencies

```bash
# Using uv
uv sync --extra dev

# Or using make
make install-dev
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License 
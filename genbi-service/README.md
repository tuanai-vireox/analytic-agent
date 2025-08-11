# genbi-core: Advanced Analytics and AI Agent Platform

A powerful analytics and AI agent platform built with FastAPI, CrewAI, and Model Context Protocol (MCP) integration. genbi-core provides comprehensive tool calling capabilities, statistical analysis, and real-time data processing.

## 🚀 Features

### Core Analytics
- **Data Analysis**: Comprehensive data analysis with pandas and numpy
- **Statistical Analysis**: Advanced statistical testing (t-tests, ANOVA, correlation tests)
- **Custom Analytics**: Extensible framework for domain-specific analysis
- **Real-time Processing**: WebSocket support for live data analysis

### Tool Calling System
- **Modular Tools**: Pluggable tool architecture with parameter validation
- **Tool Registry**: Centralized tool management and discovery
- **Schema Generation**: Automatic MCP-compatible schema generation
- **Type Safety**: Full type hints and parameter validation

### MCP (Model Context Protocol) Integration
- **MCP Server**: Full MCP server implementation with WebSocket support
- **MCP Client**: Client library for connecting to MCP servers
- **Resource Management**: File and data resource handling
- **Tool Discovery**: Dynamic tool listing and execution

### AI Agent Orchestration
- **CrewAI Integration**: Multi-agent orchestration for complex tasks
- **Agent Specialization**: Specialized agents for different analysis types
- **Workflow Management**: Automated analysis workflows
- **Result Aggregation**: Intelligent result compilation and reporting

## 📁 Project Structure

```
genbi-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection and models
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── analysis.py         # Analysis endpoints
│   │   ├── users.py            # User management
│   │   ├── health.py           # Health checks
│   │   └── tools.py            # Tool calling and MCP endpoints
│   ├── tools/                  # Tool calling system
│   │   ├── __init__.py
│   │   ├── base_tool.py        # Base tool class
│   │   ├── data_analysis_tools.py  # Data analysis tools
│   │   ├── mcp_tools.py        # MCP server and client
│   │   └── tool_registry.py    # Tool registry
│   ├── agents/                 # CrewAI agents
│   │   ├── __init__.py
│   │   ├── data_analyst_agent.py
│   │   ├── researcher_agent.py
│   │   ├── reporter_agent.py
│   │   └── crew_manager.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── analysis_service.py
│   │   └── user_service.py
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── analysis_task.py
│   │   └── user.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── analysis.py
│   │   └── user.py
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   └── security.py
│   └── demo/                   # Demo and examples
│       ├── __init__.py
│       └── mcp_demo.py         # MCP and tool calling demo
├── tests/                      # Test files
├── alembic/                    # Database migrations
├── scripts/                    # Utility scripts
├── pyproject.toml             # Project dependencies
├── uv.lock                    # Locked dependencies
├── Dockerfile                 # Docker configuration
└── .env.example               # Environment variables
```

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- uv (fast Python package installer)
- PostgreSQL (for production)
- Redis (optional, for caching)

### Quick Start

1. **Clone and setup**:
```bash
git clone <repository-url>
cd genbi-service
```

2. **Install dependencies**:
```bash
uv sync
```

3. **Setup environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the application**:
```bash
uv run uvicorn app.main:app --reload
```

## 🔧 Tool Calling System

### Basic Tool Usage

```python
from app.tools import register_tool, execute_tool, DataAnalysisTool

# Register a tool
data_tool = DataAnalysisTool()
register_tool(data_tool)

# Execute a tool
result = execute_tool(
    "data_analysis",
    data=json_data,
    analysis_type="summary",
    data_format="json"
)
```

### Creating Custom Tools

```python
from app.tools.base_tool import BaseTool, ToolParameter, ToolType

class CustomAnalysisTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="custom_analysis",
            description="Custom analysis tool",
            tool_type=ToolType.DATA_ANALYSIS
        )
    
    def _setup_parameters(self):
        self.parameters = [
            ToolParameter(
                name="data",
                type="string",
                description="Input data",
                required=True
            )
        ]
    
    async def execute(self, **kwargs):
        # Your analysis logic here
        return {"result": "analysis_complete", "success": True}
```

## 🌐 MCP Integration

### MCP Server Setup

```python
from app.tools.mcp_tools import MCPServer

# Create MCP server
server = MCPServer(host="localhost", port=3000)

# Register tools
server.register_tool("data_analysis", data_analysis_function)

# Start server
await server.start()
```

### MCP Client Usage

```python
from app.tools.mcp_tools import MCPClient

# Connect to MCP server
client = MCPClient("ws://localhost:3000")
await client.connect()

# List available tools
tools = await client.list_tools()

# Call a tool
result = await client.call_tool("data_analysis", {"data": "..."})

# Disconnect
await client.disconnect()
```

## 🎯 API Endpoints

### Tool Management
- `GET /api/v1/tools/` - List all tools
- `GET /api/v1/tools/schemas` - Get tool schemas
- `GET /api/v1/tools/{tool_name}` - Get tool information
- `POST /api/v1/tools/{tool_name}/execute` - Execute a tool
- `GET /api/v1/tools/types/{tool_type}` - Get tools by type
- `GET /api/v1/tools/search/{query}` - Search tools
- `GET /api/v1/tools/statistics` - Get tool statistics

### MCP Integration
- `POST /api/v1/tools/mcp/connect` - Connect to MCP server
- `POST /api/v1/tools/mcp/{server_url}/tools/list` - List MCP tools
- `POST /api/v1/tools/mcp/{server_url}/tools/{tool_name}/call` - Call MCP tool
- `POST /api/v1/tools/mcp/{server_url}/resources/list` - List MCP resources
- `POST /api/v1/tools/mcp/{server_url}/resources/read` - Read MCP resource

### WebSocket
- `WS /api/v1/tools/ws` - Real-time tool execution

## 🎮 Demo

### Running the MCP Demo

```bash
# Run the comprehensive demo
uv run python -m app.demo.mcp_demo
```

The demo showcases:
1. **Tool Registration**: Registering built-in and custom tools
2. **Data Analysis**: Performing various types of data analysis
3. **Statistical Testing**: Running statistical tests on sample data
4. **MCP Integration**: Server-client communication
5. **WebSocket Communication**: Real-time tool execution
6. **Custom Tools**: Domain-specific analysis tools

### Demo Features

- **Sample Data Generation**: Creates realistic sales data for analysis
- **Multiple Analysis Types**: Summary, trends, regional, and product performance
- **Statistical Tests**: Correlation, t-tests, ANOVA, normality tests
- **MCP Protocol**: Full MCP server and client implementation
- **Real-time Processing**: WebSocket-based tool execution

## 📊 Available Tools

### Data Analysis Tools
- `data_analysis`: Basic data analysis (summary, correlation, distribution, outliers, trends)
- `statistical_analysis`: Advanced statistical testing
- `sales_analysis`: Custom sales data analysis

### MCP Tools
- `mcp_tool`: MCP operations (list tools, call tools, list resources, read resources)

### Tool Types
- `data_analysis`: Data analysis and processing
- `file_operation`: File handling operations
- `web_operation`: Web scraping and API calls
- `database_operation`: Database operations
- `mcp_operation`: MCP protocol operations
- `custom`: Custom domain-specific tools

## 🔍 Development

### Running Tests
```bash
uv run pytest tests/ -v --cov=app --cov-report=html
```

### Code Quality
```bash
uv run black app/
uv run isort app/
uv run ruff check app/
uv run mypy app/
```

### Database Migrations
```bash
uv run alembic revision --autogenerate -m "Description"
uv run alembic upgrade head
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker
docker build -t genbi-core .
docker run -p 8000:8000 genbi-core

# Or use Docker Compose
docker-compose up -d
```

## 📈 Performance

- **Async Processing**: Full async/await support for high concurrency
- **Tool Caching**: Intelligent tool result caching
- **Connection Pooling**: Database connection optimization
- **Memory Management**: Efficient data handling for large datasets

## 🔒 Security

- **Parameter Validation**: Strict parameter validation for all tools
- **Input Sanitization**: Comprehensive input sanitization
- **Error Handling**: Graceful error handling and logging
- **Rate Limiting**: Built-in rate limiting for API endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the demo examples

---

**genbi-core** - Empowering AI-driven analytics with advanced tool calling and MCP integration.


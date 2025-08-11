"""
MCP (Model Context Protocol) Demo for genbi-core.

This demo showcases:
1. Tool calling capabilities
2. MCP server and client integration
3. Real-time tool execution
4. Statistical analysis tools
5. WebSocket communication
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np

from app.tools import (
    tool_registry,
    register_tool,
    DataAnalysisTool,
    StatisticalAnalysisTool,
    MCPTool
)
from app.tools.mcp_tools import MCPServer, MCPClient
from app.tools.base_tool import ToolType


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPDemo:
    """Demo class for showcasing MCP and tool calling capabilities."""
    
    def __init__(self):
        self.mcp_server = MCPServer(host="localhost", port=3000)
        self.mcp_client = MCPClient("ws://localhost:3000")
        self.sample_data = self._generate_sample_data()
    
    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample data for demonstration."""
        # Generate sample sales data
        np.random.seed(42)
        n_records = 1000
        
        data = {
            "date": pd.date_range("2024-01-01", periods=n_records, freq="D"),
            "product_id": np.random.randint(1, 11, n_records),
            "sales_amount": np.random.normal(1000, 300, n_records),
            "quantity": np.random.poisson(50, n_records),
            "region": np.random.choice(["North", "South", "East", "West"], n_records),
            "customer_type": np.random.choice(["Retail", "Wholesale", "Online"], n_records)
        }
        
        df = pd.DataFrame(data)
        return {
            "sales_data": df.to_dict(orient="records"),
            "json_data": df.to_json(orient="records"),
            "csv_data": df.to_csv(index=False)
        }
    
    def setup_tools(self):
        """Setup and register tools for the demo."""
        logger.info("Setting up tools...")
        
        # Register built-in tools
        data_analysis_tool = DataAnalysisTool()
        statistical_analysis_tool = StatisticalAnalysisTool()
        mcp_tool = MCPTool()
        
        register_tool(data_analysis_tool)
        register_tool(statistical_analysis_tool)
        register_tool(mcp_tool)
        
        # Register custom demo tools
        self._register_demo_tools()
        
        logger.info(f"Registered {tool_registry.get_tool_count()} tools")
    
    def _register_demo_tools(self):
        """Register custom demo tools."""
        from app.tools.base_tool import BaseTool, ToolParameter
        
        class SalesAnalysisTool(BaseTool):
            """Custom tool for sales data analysis."""
            
            def __init__(self):
                super().__init__(
                    name="sales_analysis",
                    description="Analyze sales data and generate insights",
                    tool_type=ToolType.DATA_ANALYSIS
                )
            
            def _setup_parameters(self) -> None:
                self.parameters = [
                    ToolParameter(
                        name="data",
                        type="string",
                        description="Sales data in JSON format",
                        required=True
                    ),
                    ToolParameter(
                        name="analysis_type",
                        type="string",
                        description="Type of sales analysis",
                        required=True,
                        enum=["summary", "trends", "regional", "product_performance"]
                    )
                ]
            
            async def execute(self, **kwargs) -> Dict[str, Any]:
                try:
                    self.validate_parameters(**kwargs)
                    
                    data = kwargs["data"]
                    analysis_type = kwargs["analysis_type"]
                    
                    # Parse data
                    if isinstance(data, str):
                        df = pd.read_json(data)
                    else:
                        df = pd.DataFrame(data)
                    
                    # Perform analysis
                    if analysis_type == "summary":
                        result = self._sales_summary(df)
                    elif analysis_type == "trends":
                        result = self._sales_trends(df)
                    elif analysis_type == "regional":
                        result = self._regional_analysis(df)
                    elif analysis_type == "product_performance":
                        result = self._product_performance(df)
                    else:
                        raise ValueError(f"Unknown analysis type: {analysis_type}")
                    
                    return {
                        "result": result,
                        "success": True,
                        "error": None
                    }
                    
                except Exception as e:
                    return {
                        "result": None,
                        "success": False,
                        "error": str(e)
                    }
            
            def _sales_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
                """Generate sales summary."""
                return {
                    "total_sales": df["sales_amount"].sum(),
                    "total_quantity": df["quantity"].sum(),
                    "average_sale": df["sales_amount"].mean(),
                    "total_transactions": len(df),
                    "date_range": {
                        "start": df["date"].min().isoformat(),
                        "end": df["date"].max().isoformat()
                    }
                }
            
            def _sales_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
                """Analyze sales trends."""
                df["date"] = pd.to_datetime(df["date"])
                daily_sales = df.groupby(df["date"].dt.date)["sales_amount"].sum()
                
                # Calculate trend
                x = np.arange(len(daily_sales))
                y = daily_sales.values
                slope = np.polyfit(x, y, 1)[0]
                
                return {
                    "daily_sales": daily_sales.to_dict(),
                    "trend_direction": "increasing" if slope > 0 else "decreasing",
                    "trend_strength": abs(slope),
                    "total_days": len(daily_sales)
                }
            
            def _regional_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
                """Analyze sales by region."""
                regional_sales = df.groupby("region").agg({
                    "sales_amount": ["sum", "mean", "count"],
                    "quantity": "sum"
                }).round(2)
                
                return {
                    "regional_sales": regional_sales.to_dict(),
                    "top_region": regional_sales["sales_amount"]["sum"].idxmax(),
                    "regional_distribution": df["region"].value_counts().to_dict()
                }
            
            def _product_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
                """Analyze product performance."""
                product_sales = df.groupby("product_id").agg({
                    "sales_amount": ["sum", "mean", "count"],
                    "quantity": "sum"
                }).round(2)
                
                return {
                    "product_sales": product_sales.to_dict(),
                    "top_product": product_sales["sales_amount"]["sum"].idxmax(),
                    "product_ranking": product_sales["sales_amount"]["sum"].sort_values(ascending=False).to_dict()
                }
        
        # Register the custom tool
        sales_analysis_tool = SalesAnalysisTool()
        register_tool(sales_analysis_tool)
    
    async def setup_mcp_server(self):
        """Setup MCP server with registered tools."""
        logger.info("Setting up MCP server...")
        
        # Register tools with MCP server
        for tool in tool_registry.get_all_tools():
            self.mcp_server.register_tool(tool.name, tool.execute)
        
        # Register sample resources
        self.mcp_server.register_resource(
            "file:///data/sample_sales.csv",
            {
                "name": "Sample Sales Data",
                "description": "Sample sales dataset for analysis",
                "mimeType": "text/csv"
            }
        )
        
        self.mcp_server.register_resource(
            "file:///data/config.json",
            {
                "name": "Configuration",
                "description": "System configuration file",
                "mimeType": "application/json"
            }
        )
        
        logger.info("MCP server setup complete")
    
    async def run_tool_demo(self):
        """Run tool calling demonstration."""
        logger.info("Running tool calling demo...")
        
        # Demo 1: Basic data analysis
        logger.info("Demo 1: Basic Data Analysis")
        result1 = tool_registry.execute_tool(
            "data_analysis",
            data=self.sample_data["json_data"],
            analysis_type="summary",
            data_format="json"
        )
        logger.info(f"Data analysis result: {result1}")
        
        # Demo 2: Statistical analysis
        logger.info("Demo 2: Statistical Analysis")
        result2 = tool_registry.execute_tool(
            "statistical_analysis",
            data=self.sample_data["json_data"],
            test_type="correlation_test"
        )
        logger.info(f"Statistical analysis result: {result2}")
        
        # Demo 3: Custom sales analysis
        logger.info("Demo 3: Custom Sales Analysis")
        result3 = tool_registry.execute_tool(
            "sales_analysis",
            data=self.sample_data["sales_data"],
            analysis_type="regional"
        )
        logger.info(f"Sales analysis result: {result3}")
        
        # Demo 4: MCP tool operations
        logger.info("Demo 4: MCP Tool Operations")
        result4 = tool_registry.execute_tool(
            "mcp_tool",
            operation="list_tools"
        )
        logger.info(f"MCP tools list: {result4}")
    
    async def run_mcp_demo(self):
        """Run MCP integration demonstration."""
        logger.info("Running MCP integration demo...")
        
        try:
            # Start MCP server
            server_task = asyncio.create_task(self.mcp_server.start())
            
            # Wait a moment for server to start
            await asyncio.sleep(1)
            
            # Connect client
            await self.mcp_client.connect()
            
            # Demo 1: List tools from MCP server
            logger.info("MCP Demo 1: Listing tools")
            tools = await self.mcp_client.list_tools()
            logger.info(f"Available MCP tools: {tools}")
            
            # Demo 2: Call tool via MCP
            logger.info("MCP Demo 2: Calling tool")
            tool_result = await self.mcp_client.call_tool(
                "data_analysis",
                {
                    "data": self.sample_data["json_data"],
                    "analysis_type": "summary",
                    "data_format": "json"
                }
            )
            logger.info(f"MCP tool result: {tool_result}")
            
            # Demo 3: List resources
            logger.info("MCP Demo 3: Listing resources")
            resources = await self.mcp_client.list_resources()
            logger.info(f"Available resources: {resources}")
            
            # Demo 4: Read resource
            logger.info("MCP Demo 4: Reading resource")
            resource = await self.mcp_client.read_resource("file:///data/sample_sales.csv")
            logger.info(f"Resource content: {resource}")
            
            # Disconnect client
            await self.mcp_client.disconnect()
            
            # Stop server
            server_task.cancel()
            
        except Exception as e:
            logger.error(f"Error in MCP demo: {e}")
    
    async def run_websocket_demo(self):
        """Run WebSocket demonstration."""
        logger.info("Running WebSocket demo...")
        
        # This would typically involve a WebSocket client
        # For demo purposes, we'll simulate WebSocket messages
        demo_messages = [
            {
                "type": "list_tools",
                "data": {}
            },
            {
                "type": "execute_tool",
                "tool_name": "data_analysis",
                "parameters": {
                    "data": self.sample_data["json_data"],
                    "analysis_type": "summary",
                    "data_format": "json"
                }
            },
            {
                "type": "mcp_connect",
                "server_url": "ws://localhost:3000"
            }
        ]
        
        for i, message in enumerate(demo_messages):
            logger.info(f"WebSocket Demo {i+1}: {message['type']}")
            # In a real scenario, this would be sent via WebSocket
            logger.info(f"Message: {json.dumps(message, indent=2)}")
    
    def print_demo_summary(self):
        """Print demo summary and statistics."""
        logger.info("=== DEMO SUMMARY ===")
        
        # Tool statistics
        stats = tool_registry.get_tool_statistics()
        logger.info(f"Total tools registered: {stats['total_tools']}")
        logger.info(f"Tools by type: {stats['tools_by_type']}")
        
        # Available tools
        tools = list_all_tools()
        logger.info("Available tools:")
        for tool in tools:
            logger.info(f"  - {tool['name']}: {tool['description']}")
        
        # Sample data info
        logger.info(f"Sample data records: {len(self.sample_data['sales_data'])}")
        logger.info("Sample data columns: date, product_id, sales_amount, quantity, region, customer_type")
    
    async def run_full_demo(self):
        """Run the complete MCP and tool calling demo."""
        logger.info("Starting genbi-core MCP and Tool Calling Demo")
        logger.info("=" * 50)
        
        try:
            # Setup
            self.setup_tools()
            await self.setup_mcp_server()
            
            # Print summary
            self.print_demo_summary()
            
            # Run demos
            await self.run_tool_demo()
            await self.run_mcp_demo()
            await self.run_websocket_demo()
            
            logger.info("Demo completed successfully!")
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            raise


async def main():
    """Main function to run the demo."""
    demo = MCPDemo()
    await demo.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main()) 
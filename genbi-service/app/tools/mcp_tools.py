"""
MCP (Model Context Protocol) tools for genbi-core.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import websockets
from websockets.server import WebSocketServerProtocol
from .base_tool import BaseTool, ToolType, ToolParameter


class MCPMessageType(str, Enum):
    """MCP message types."""
    HELLO = "hello"
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"
    LIST_RESOURCES = "resources/list"
    READ_RESOURCE = "resources/read"
    LIST_PROMISES = "promises/list"
    CANCEL_PROMISE = "promises/cancel"
    ERROR = "error"


@dataclass
class MCPMessage:
    """MCP message structure."""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class MCPTool(BaseTool):
    """Tool for MCP (Model Context Protocol) operations."""
    
    def __init__(self):
        super().__init__(
            name="mcp_tool",
            description="Execute MCP (Model Context Protocol) operations",
            tool_type=ToolType.MCP_OPERATION
        )
    
    def _setup_parameters(self) -> None:
        self.parameters = [
            ToolParameter(
                name="operation",
                type="string",
                description="MCP operation to perform",
                required=True,
                enum=["list_tools", "call_tool", "list_resources", "read_resource"]
            ),
            ToolParameter(
                name="tool_name",
                type="string",
                description="Name of the tool to call (for call_tool operation)",
                required=False
            ),
            ToolParameter(
                name="tool_params",
                type="object",
                description="Parameters for tool execution (for call_tool operation)",
                required=False
            ),
            ToolParameter(
                name="resource_uri",
                type="string",
                description="URI of the resource to read (for read_resource operation)",
                required=False
            )
        ]
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            self.validate_parameters(**kwargs)
            
            operation = kwargs["operation"]
            
            if operation == "list_tools":
                result = await self._list_tools()
            elif operation == "call_tool":
                tool_name = kwargs["tool_name"]
                tool_params = kwargs.get("tool_params", {})
                result = await self._call_tool(tool_name, tool_params)
            elif operation == "list_resources":
                result = await self._list_resources()
            elif operation == "read_resource":
                resource_uri = kwargs["resource_uri"]
                result = await self._read_resource(resource_uri)
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
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
    
    async def _list_tools(self) -> Dict[str, Any]:
        """List available MCP tools."""
        # This would typically connect to an MCP server
        return {
            "tools": [
                {
                    "name": "data_analysis",
                    "description": "Perform data analysis",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "string"},
                            "analysis_type": {"type": "string"}
                        }
                    }
                },
                {
                    "name": "statistical_analysis",
                    "description": "Perform statistical analysis",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "string"},
                            "test_type": {"type": "string"}
                        }
                    }
                }
            ]
        }
    
    async def _call_tool(self, tool_name: str, tool_params: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        # This would typically make an MCP call to a server
        return {
            "tool_name": tool_name,
            "params": tool_params,
            "result": f"Executed {tool_name} with params: {tool_params}"
        }
    
    async def _list_resources(self) -> Dict[str, Any]:
        """List available MCP resources."""
        return {
            "resources": [
                {
                    "uri": "file:///data/sample.csv",
                    "name": "Sample CSV Data",
                    "description": "Sample dataset for analysis",
                    "mimeType": "text/csv"
                },
                {
                    "uri": "file:///data/config.json",
                    "name": "Configuration",
                    "description": "System configuration file",
                    "mimeType": "application/json"
                }
            ]
        }
    
    async def _read_resource(self, resource_uri: str) -> Dict[str, Any]:
        """Read an MCP resource."""
        return {
            "uri": resource_uri,
            "content": f"Content of {resource_uri}",
            "mimeType": "text/plain"
        }


class MCPClient:
    """MCP client for connecting to MCP servers."""
    
    def __init__(self, server_url: str = "ws://localhost:3000"):
        self.server_url = server_url
        self.websocket: Optional[WebSocketServerProtocol] = None
        self.logger = logging.getLogger(__name__)
    
    async def connect(self) -> None:
        """Connect to MCP server."""
        try:
            self.websocket = await websockets.connect(self.server_url)
            self.logger.info(f"Connected to MCP server: {self.server_url}")
        except Exception as e:
            self.logger.error(f"Failed to connect to MCP server: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.logger.info("Disconnected from MCP server")
    
    async def send_message(self, message: MCPMessage) -> None:
        """Send message to MCP server."""
        if not self.websocket:
            raise ConnectionError("Not connected to MCP server")
        
        message_dict = {
            "jsonrpc": message.jsonrpc,
            "id": message.id,
            "method": message.method,
            "params": message.params
        }
        
        await self.websocket.send(json.dumps(message_dict))
        self.logger.debug(f"Sent message: {message_dict}")
    
    async def receive_message(self) -> MCPMessage:
        """Receive message from MCP server."""
        if not self.websocket:
            raise ConnectionError("Not connected to MCP server")
        
        response = await self.websocket.recv()
        response_dict = json.loads(response)
        
        message = MCPMessage(
            jsonrpc=response_dict.get("jsonrpc"),
            id=response_dict.get("id"),
            result=response_dict.get("result"),
            error=response_dict.get("error")
        )
        
        self.logger.debug(f"Received message: {response_dict}")
        return message
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools from MCP server."""
        message = MCPMessage(
            id="list_tools",
            method=MCPMessageType.LIST_TOOLS
        )
        
        await self.send_message(message)
        response = await self.receive_message()
        
        if response.error:
            raise Exception(f"MCP error: {response.error}")
        
        return response.result or {}
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on MCP server."""
        message = MCPMessage(
            id="call_tool",
            method=MCPMessageType.CALL_TOOL,
            params={
                "name": tool_name,
                "arguments": params
            }
        )
        
        await self.send_message(message)
        response = await self.receive_message()
        
        if response.error:
            raise Exception(f"MCP error: {response.error}")
        
        return response.result or {}
    
    async def list_resources(self) -> Dict[str, Any]:
        """List available resources from MCP server."""
        message = MCPMessage(
            id="list_resources",
            method=MCPMessageType.LIST_RESOURCES
        )
        
        await self.send_message(message)
        response = await self.receive_message()
        
        if response.error:
            raise Exception(f"MCP error: {response.error}")
        
        return response.result or {}
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource from MCP server."""
        message = MCPMessage(
            id="read_resource",
            method=MCPMessageType.READ_RESOURCE,
            params={"uri": uri}
        )
        
        await self.send_message(message)
        response = await self.receive_message()
        
        if response.error:
            raise Exception(f"MCP error: {response.error}")
        
        return response.result or {}


class MCPServer:
    """MCP server for exposing tools and resources."""
    
    def __init__(self, host: str = "localhost", port: int = 3000):
        self.host = host
        self.port = port
        self.tools: Dict[str, Callable] = {}
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_tool(self, name: str, tool_func: Callable) -> None:
        """Register a tool with the MCP server."""
        self.tools[name] = tool_func
        self.logger.info(f"Registered tool: {name}")
    
    def register_resource(self, uri: str, resource_info: Dict[str, Any]) -> None:
        """Register a resource with the MCP server."""
        self.resources[uri] = resource_info
        self.logger.info(f"Registered resource: {uri}")
    
    async def handle_message(self, websocket: WebSocketServerProtocol, message_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP message."""
        message_id = message_dict.get("id")
        method = message_dict.get("method")
        params = message_dict.get("params", {})
        
        try:
            if method == MCPMessageType.HELLO:
                result = {"protocolVersion": "2024-11-05"}
            
            elif method == MCPMessageType.LIST_TOOLS:
                tools_list = []
                for name, tool_func in self.tools.items():
                    tools_list.append({
                        "name": name,
                        "description": f"Tool: {name}",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "params": {"type": "object"}
                            }
                        }
                    })
                result = {"tools": tools_list}
            
            elif method == MCPMessageType.CALL_TOOL:
                tool_name = params.get("name")
                tool_params = params.get("arguments", {})
                
                if tool_name not in self.tools:
                    raise Exception(f"Tool not found: {tool_name}")
                
                tool_result = await self.tools[tool_name](**tool_params)
                result = {"content": [{"type": "text", "text": str(tool_result)}]}
            
            elif method == MCPMessageType.LIST_RESOURCES:
                resources_list = []
                for uri, resource_info in self.resources.items():
                    resources_list.append({
                        "uri": uri,
                        **resource_info
                    })
                result = {"resources": resources_list}
            
            elif method == MCPMessageType.READ_RESOURCE:
                uri = params.get("uri")
                
                if uri not in self.resources:
                    raise Exception(f"Resource not found: {uri}")
                
                result = {
                    "uri": uri,
                    "contents": [{
                        "uri": uri,
                        "mimeType": self.resources[uri].get("mimeType", "text/plain"),
                        "text": f"Content of {uri}"
                    }]
                }
            
            else:
                raise Exception(f"Unknown method: {method}")
            
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def start(self) -> None:
        """Start the MCP server."""
        async def handler(websocket: WebSocketServerProtocol, path: str):
            self.logger.info(f"Client connected: {websocket.remote_address}")
            
            try:
                async for message in websocket:
                    message_dict = json.loads(message)
                    response = await self.handle_message(websocket, message_dict)
                    await websocket.send(json.dumps(response))
                    
            except websockets.exceptions.ConnectionClosed:
                self.logger.info("Client disconnected")
            except Exception as e:
                self.logger.error(f"Error in websocket handler: {e}")
        
        server = await websockets.serve(handler, self.host, self.port)
        self.logger.info(f"MCP server started on ws://{self.host}:{self.port}")
        
        await server.wait_closed()
    
    async def stop(self) -> None:
        """Stop the MCP server."""
        self.logger.info("MCP server stopped") 
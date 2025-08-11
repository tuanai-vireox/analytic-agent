"""
API endpoints for tool calling and MCP integration in genbi-core.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import json
import asyncio

from app.database import get_db
from app.tools import (
    tool_registry, 
    register_tool, 
    get_tool, 
    execute_tool, 
    list_all_tools,
    get_tool_schemas
)
from app.tools.base_tool import BaseTool, ToolType
from app.tools.mcp_tools import MCPClient, MCPServer, MCPMessage, MCPMessageType

router = APIRouter(prefix="/api/v1/tools", tags=["tools"])


@router.get("/", response_model=List[Dict[str, Any]])
async def list_tools():
    """
    List all available tools.
    
    Returns a list of all registered tools with their metadata.
    """
    return list_all_tools()


@router.get("/schemas", response_model=List[Dict[str, Any]])
async def get_tool_schemas_endpoint():
    """
    Get schemas for all tools.
    
    Returns MCP-compatible schemas for all registered tools.
    """
    schemas = get_tool_schemas()
    return [schema.dict() for schema in schemas]


@router.get("/{tool_name}", response_model=Dict[str, Any])
async def get_tool_info(tool_name: str):
    """
    Get information about a specific tool.
    
    Returns detailed information about the specified tool.
    """
    tool = get_tool(tool_name)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{tool_name}' not found"
        )
    
    return {
        "name": tool.name,
        "description": tool.description,
        "type": tool.tool_type.value,
        "parameters": tool.get_parameter_info(),
        "schema": tool.get_schema().dict()
    }


@router.post("/{tool_name}/execute", response_model=Dict[str, Any])
async def execute_tool_endpoint(
    tool_name: str,
    parameters: Dict[str, Any]
):
    """
    Execute a specific tool.
    
    Executes the specified tool with the provided parameters.
    """
    result = execute_tool(tool_name, **parameters)
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Tool execution failed")
        )
    
    return result


@router.get("/types/{tool_type}", response_model=List[Dict[str, Any]])
async def get_tools_by_type(tool_type: str):
    """
    Get tools by type.
    
    Returns all tools of the specified type.
    """
    try:
        tool_type_enum = ToolType(tool_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tool type: {tool_type}"
        )
    
    tools = tool_registry.get_tools_by_type(tool_type_enum)
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "type": tool.tool_type.value,
            "parameters": tool.get_parameter_info()
        }
        for tool in tools
    ]


@router.get("/search/{query}", response_model=List[Dict[str, Any]])
async def search_tools(query: str):
    """
    Search tools by name or description.
    
    Returns tools that match the search query.
    """
    matching_tools = tool_registry.search_tools(query)
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "type": tool.tool_type.value,
            "parameters": tool.get_parameter_info()
        }
        for tool in matching_tools
    ]


@router.get("/statistics", response_model=Dict[str, Any])
async def get_tool_statistics():
    """
    Get tool statistics.
    
    Returns statistics about registered tools.
    """
    return tool_registry.get_tool_statistics()


# MCP Integration Endpoints

@router.post("/mcp/connect")
async def connect_mcp_server(server_url: str):
    """
    Connect to an MCP server.
    
    Establishes a connection to an MCP server and returns connection status.
    """
    try:
        client = MCPClient(server_url)
        await client.connect()
        
        # Test connection by listing tools
        tools = await client.list_tools()
        
        await client.disconnect()
        
        return {
            "success": True,
            "server_url": server_url,
            "available_tools": len(tools.get("tools", [])),
            "message": "Successfully connected to MCP server"
        }
        
    except Exception as e:
        return {
            "success": False,
            "server_url": server_url,
            "error": str(e)
        }


@router.post("/mcp/{server_url}/tools/list")
async def list_mcp_tools(server_url: str):
    """
    List tools from an MCP server.
    
    Connects to the specified MCP server and lists available tools.
    """
    try:
        client = MCPClient(server_url)
        await client.connect()
        
        tools = await client.list_tools()
        
        await client.disconnect()
        
        return {
            "success": True,
            "server_url": server_url,
            "tools": tools
        }
        
    except Exception as e:
        return {
            "success": False,
            "server_url": server_url,
            "error": str(e)
        }


@router.post("/mcp/{server_url}/tools/{tool_name}/call")
async def call_mcp_tool(
    server_url: str,
    tool_name: str,
    parameters: Dict[str, Any]
):
    """
    Call a tool on an MCP server.
    
    Connects to the specified MCP server and calls the specified tool.
    """
    try:
        client = MCPClient(server_url)
        await client.connect()
        
        result = await client.call_tool(tool_name, parameters)
        
        await client.disconnect()
        
        return {
            "success": True,
            "server_url": server_url,
            "tool_name": tool_name,
            "result": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "server_url": server_url,
            "tool_name": tool_name,
            "error": str(e)
        }


@router.post("/mcp/{server_url}/resources/list")
async def list_mcp_resources(server_url: str):
    """
    List resources from an MCP server.
    
    Connects to the specified MCP server and lists available resources.
    """
    try:
        client = MCPClient(server_url)
        await client.connect()
        
        resources = await client.list_resources()
        
        await client.disconnect()
        
        return {
            "success": True,
            "server_url": server_url,
            "resources": resources
        }
        
    except Exception as e:
        return {
            "success": False,
            "server_url": server_url,
            "error": str(e)
        }


@router.post("/mcp/{server_url}/resources/read")
async def read_mcp_resource(
    server_url: str,
    resource_uri: str
):
    """
    Read a resource from an MCP server.
    
    Connects to the specified MCP server and reads the specified resource.
    """
    try:
        client = MCPClient(server_url)
        await client.connect()
        
        resource = await client.read_resource(resource_uri)
        
        await client.disconnect()
        
        return {
            "success": True,
            "server_url": server_url,
            "resource_uri": resource_uri,
            "resource": resource
        }
        
    except Exception as e:
        return {
            "success": False,
            "server_url": server_url,
            "resource_uri": resource_uri,
            "error": str(e)
        }


# WebSocket endpoint for real-time tool execution
@router.websocket("/ws")
async def tools_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time tool execution.
    
    Supports real-time tool calling and MCP operations.
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process message
            response = await process_tool_message(message)
            
            # Send response
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        error_response = {
            "type": "error",
            "message": str(e)
        }
        await websocket.send_text(json.dumps(error_response))


async def process_tool_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Process tool-related WebSocket messages."""
    message_type = message.get("type")
    
    if message_type == "list_tools":
        return {
            "type": "tools_list",
            "tools": list_all_tools()
        }
    
    elif message_type == "execute_tool":
        tool_name = message.get("tool_name")
        parameters = message.get("parameters", {})
        
        if not tool_name:
            return {
                "type": "error",
                "message": "Tool name is required"
            }
        
        result = execute_tool(tool_name, **parameters)
        return {
            "type": "tool_result",
            "tool_name": tool_name,
            "result": result
        }
    
    elif message_type == "mcp_connect":
        server_url = message.get("server_url")
        if not server_url:
            return {
                "type": "error",
                "message": "Server URL is required"
            }
        
        try:
            client = MCPClient(server_url)
            await client.connect()
            tools = await client.list_tools()
            await client.disconnect()
            
            return {
                "type": "mcp_connected",
                "server_url": server_url,
                "tools": tools
            }
        except Exception as e:
            return {
                "type": "error",
                "message": f"Failed to connect to MCP server: {str(e)}"
            }
    
    else:
        return {
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        } 
"""
Tool registry for managing and discovering tools in genbi-core.
"""

from typing import Dict, List, Optional, Type, Any
from .base_tool import BaseTool, ToolType, ToolSchema


class ToolRegistry:
    """Registry for managing genbi-core tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._tool_classes: Dict[str, Type[BaseTool]] = {}
        self._tool_instances: Dict[str, BaseTool] = {}
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool instance."""
        self._tools[tool.name] = tool
        self._tool_instances[tool.name] = tool
    
    def register_tool_class(self, name: str, tool_class: Type[BaseTool]) -> None:
        """Register a tool class for dynamic instantiation."""
        self._tool_classes[name] = tool_class
    
    def create_tool_instance(self, name: str, **kwargs) -> Optional[BaseTool]:
        """Create a tool instance from a registered class."""
        if name not in self._tool_classes:
            return None
        
        tool_class = self._tool_classes[name]
        tool_instance = tool_class(**kwargs)
        self.register_tool(tool_instance)
        return tool_instance
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools."""
        return list(self._tools.values())
    
    def get_tools_by_type(self, tool_type: ToolType) -> List[BaseTool]:
        """Get tools by type."""
        return [tool for tool in self._tools.values() if tool.tool_type == tool_type]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all tools with their information."""
        tools_info = []
        for tool in self._tools.values():
            tools_info.append({
                "name": tool.name,
                "description": tool.description,
                "type": tool.tool_type.value,
                "parameters": tool.get_parameter_info()
            })
        return tools_info
    
    def get_tool_schemas(self) -> List[ToolSchema]:
        """Get schemas for all tools."""
        return [tool.get_schema() for tool in self._tools.values()]
    
    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{name}' not found"
            }
        
        try:
            import asyncio
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, need to run the coroutine
                return asyncio.run(tool.execute(**kwargs))
            except RuntimeError:
                # We're not in an async context, can run directly
                return asyncio.run(tool.execute(**kwargs))
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def remove_tool(self, name: str) -> bool:
        """Remove a tool from the registry."""
        if name in self._tools:
            del self._tools[name]
            if name in self._tool_instances:
                del self._tool_instances[name]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all tools from the registry."""
        self._tools.clear()
        self._tool_instances.clear()
    
    def get_tool_count(self) -> int:
        """Get the total number of registered tools."""
        return len(self._tools)
    
    def search_tools(self, query: str) -> List[BaseTool]:
        """Search tools by name or description."""
        query_lower = query.lower()
        matching_tools = []
        
        for tool in self._tools.values():
            if (query_lower in tool.name.lower() or 
                query_lower in tool.description.lower()):
                matching_tools.append(tool)
        
        return matching_tools
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get statistics about registered tools."""
        stats = {
            "total_tools": len(self._tools),
            "tools_by_type": {},
            "parameter_counts": []
        }
        
        # Count tools by type
        for tool_type in ToolType:
            tools_of_type = self.get_tools_by_type(tool_type)
            stats["tools_by_type"][tool_type.value] = len(tools_of_type)
        
        # Parameter count statistics
        for tool in self._tools.values():
            stats["parameter_counts"].append({
                "tool_name": tool.name,
                "parameter_count": len(tool.parameters),
                "required_parameters": len([p for p in tool.parameters if p.required])
            })
        
        return stats


# Global tool registry instance
tool_registry = ToolRegistry()


def register_tool(tool: BaseTool) -> None:
    """Register a tool with the global registry."""
    tool_registry.register_tool(tool)


def get_tool(name: str) -> Optional[BaseTool]:
    """Get a tool from the global registry."""
    return tool_registry.get_tool(name)


def execute_tool(name: str, **kwargs) -> Dict[str, Any]:
    """Execute a tool from the global registry."""
    return tool_registry.execute_tool(name, **kwargs)


def list_all_tools() -> List[Dict[str, Any]]:
    """List all tools in the global registry."""
    return tool_registry.list_tools()


def get_tool_schemas() -> List[ToolSchema]:
    """Get schemas for all tools in the global registry."""
    return tool_registry.get_tool_schemas() 
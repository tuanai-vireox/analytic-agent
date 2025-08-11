"""
Base tool class for genbi-core tool calling system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class ToolType(str, Enum):
    """Tool type enumeration."""
    DATA_ANALYSIS = "data_analysis"
    FILE_OPERATION = "file_operation"
    WEB_OPERATION = "web_operation"
    DATABASE_OPERATION = "database_operation"
    MCP_OPERATION = "mcp_operation"
    CUSTOM = "custom"


class ToolParameter(BaseModel):
    """Tool parameter definition."""
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type (string, integer, float, boolean, array, object)")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(default=True, description="Whether parameter is required")
    default: Optional[Any] = Field(default=None, description="Default value")
    enum: Optional[List[str]] = Field(default=None, description="Enum values if applicable")


class ToolSchema(BaseModel):
    """Tool schema definition for MCP compatibility."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    inputSchema: Dict[str, Any] = Field(..., description="Input schema")
    outputSchema: Dict[str, Any] = Field(..., description="Output schema")


class BaseTool(ABC):
    """Base class for all genbi-core tools."""
    
    def __init__(self, name: str, description: str, tool_type: ToolType = ToolType.CUSTOM):
        self.name = name
        self.description = description
        self.tool_type = tool_type
        self.parameters: List[ToolParameter] = []
        self._setup_parameters()
    
    @abstractmethod
    def _setup_parameters(self) -> None:
        """Setup tool parameters. Override in subclasses."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool. Override in subclasses."""
        pass
    
    def get_schema(self) -> ToolSchema:
        """Get tool schema for MCP compatibility."""
        input_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param in self.parameters:
            input_schema["properties"][param.name] = {
                "type": param.type,
                "description": param.description
            }
            
            if param.enum:
                input_schema["properties"][param.name]["enum"] = param.enum
                
            if param.default is not None:
                input_schema["properties"][param.name]["default"] = param.default
                
            if param.required:
                input_schema["required"].append(param.name)
        
        return ToolSchema(
            name=self.name,
            description=self.description,
            inputSchema=input_schema,
            outputSchema={
                "type": "object",
                "properties": {
                    "result": {"type": "string", "description": "Tool execution result"},
                    "success": {"type": "boolean", "description": "Whether execution was successful"},
                    "error": {"type": "string", "description": "Error message if any"}
                }
            }
        )
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate input parameters."""
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(f"Required parameter '{param.name}' is missing")
            
            if param.name in kwargs:
                value = kwargs[param.name]
                if param.enum and value not in param.enum:
                    raise ValueError(f"Parameter '{param.name}' must be one of {param.enum}")
        
        return True
    
    def get_parameter_info(self) -> List[Dict[str, Any]]:
        """Get parameter information for tool documentation."""
        return [
            {
                "name": param.name,
                "type": param.type,
                "description": param.description,
                "required": param.required,
                "default": param.default,
                "enum": param.enum
            }
            for param in self.parameters
        ]
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', type='{self.tool_type}')>" 
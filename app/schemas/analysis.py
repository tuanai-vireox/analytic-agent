"""
Pydantic schemas for analysis-related requests and responses.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field

from app.models.analysis_task import TaskStatus, AnalysisType


class AnalysisRequest(BaseModel):
    """Request schema for creating an analysis task."""
    
    query: str = Field(..., description="The analysis query or question")
    analysis_type: AnalysisType = Field(..., description="Type of analysis to perform")
    data_source: Optional[str] = Field(None, description="Data source identifier or file path")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional analysis parameters")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Analyze sales trends for Q4 2023",
                "analysis_type": "trend_analysis",
                "data_source": "sales_data.csv",
                "parameters": {
                    "time_period": "Q4 2023",
                    "metrics": ["revenue", "units_sold"]
                }
            }
        }


class AnalysisStatus(BaseModel):
    """Status information for an analysis task."""
    
    task_id: str
    status: TaskStatus
    progress: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage")
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    estimated_completion: Optional[datetime] = None


class AnalysisResult(BaseModel):
    """Result data from an analysis task."""
    
    summary: str = Field(..., description="Summary of the analysis results")
    insights: List[str] = Field(..., description="Key insights from the analysis")
    recommendations: List[str] = Field(..., description="Actionable recommendations")
    data_visualizations: Optional[List[Dict[str, Any]]] = Field(None, description="Visualization data")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Key metrics and statistics")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw analysis data")


class AnalysisResponse(BaseModel):
    """Response schema for analysis task creation."""
    
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    message: str = Field(..., description="Response message")
    created_at: datetime = Field(..., description="Task creation timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "task_12345",
                "status": "pending",
                "message": "Analysis task created successfully",
                "created_at": "2023-12-01T10:00:00Z"
            }
        }


class AnalysisTaskCreate(BaseModel):
    """Schema for creating an analysis task in the database."""
    
    task_id: str
    query: str
    analysis_type: AnalysisType
    data_source: Optional[str] = None
    user_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class AnalysisTaskUpdate(BaseModel):
    """Schema for updating an analysis task."""
    
    status: Optional[TaskStatus] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    agents_used: Optional[List[str]] = None
    iterations_count: Optional[int] = None


class AnalysisTaskResponse(BaseModel):
    """Complete analysis task response including status and results."""
    
    id: int
    task_id: str
    query: str
    analysis_type: AnalysisType
    data_source: Optional[str] = None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[AnalysisResult] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    agents_used: Optional[List[str]] = None
    iterations_count: int
    
    class Config:
        from_attributes = True 
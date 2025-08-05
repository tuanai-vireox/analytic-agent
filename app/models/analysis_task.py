"""
Analysis task model for storing task information and results.
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base


class TaskStatus(str, Enum):
    """Analysis task status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisType(str, Enum):
    """Analysis type enumeration."""
    TREND_ANALYSIS = "trend_analysis"
    PATTERN_DETECTION = "pattern_detection"
    PREDICTIVE_MODELING = "predictive_modeling"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    CUSTOM = "custom"


class AnalysisTask(Base):
    """Analysis task model."""
    
    __tablename__ = "analysis_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, nullable=True)  # Optional user association
    
    # Task details
    query = Column(Text, nullable=False)
    analysis_type = Column(SQLEnum(AnalysisType), nullable=False)
    data_source = Column(String(500), nullable=True)
    
    # Status and timing
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Results and metadata
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Agent information
    agents_used = Column(JSON, nullable=True)  # List of agent names used
    iterations_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<AnalysisTask(id={self.id}, task_id='{self.task_id}', status='{self.status}')>" 
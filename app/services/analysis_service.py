"""
Analysis service for handling analysis business logic.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.analysis_task import AnalysisTask, TaskStatus
from app.schemas.analysis import AnalysisTaskCreate, AnalysisTaskUpdate
from app.agents.crew_manager import CrewManager


class AnalysisService:
    """Service for handling analysis operations."""
    
    def __init__(self):
        """Initialize the analysis service."""
        self.crew_manager = CrewManager()
    
    async def create_analysis_task(self, db: Session, task_data: AnalysisTaskCreate) -> AnalysisTask:
        """
        Create a new analysis task.
        
        Args:
            db: Database session
            task_data: Task creation data
            
        Returns:
            Created analysis task
        """
        db_task = AnalysisTask(
            task_id=task_data.task_id,
            query=task_data.query,
            analysis_type=task_data.analysis_type,
            data_source=task_data.data_source,
            user_id=task_data.user_id,
            metadata=task_data.metadata,
            status=TaskStatus.PENDING
        )
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        return db_task
    
    async def get_analysis_task(self, db: Session, task_id: str) -> Optional[AnalysisTask]:
        """
        Get an analysis task by task ID.
        
        Args:
            db: Database session
            task_id: Task identifier
            
        Returns:
            Analysis task if found
        """
        return db.query(AnalysisTask).filter(AnalysisTask.task_id == task_id).first()
    
    async def update_analysis_task(self, db: Session, task_id: str, 
                                 update_data: AnalysisTaskUpdate) -> Optional[AnalysisTask]:
        """
        Update an analysis task.
        
        Args:
            db: Database session
            task_id: Task identifier
            update_data: Update data
            
        Returns:
            Updated analysis task
        """
        db_task = await self.get_analysis_task(db, task_id)
        if not db_task:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        
        return db_task
    
    async def run_analysis(self, db: Session, query: str, analysis_type: str, 
                          data_source: Optional[str] = None, 
                          parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run an analysis using CrewAI agents.
        
        Args:
            db: Database session
            query: Analysis query
            analysis_type: Type of analysis
            data_source: Optional data source
            parameters: Optional parameters
            
        Returns:
            Analysis results
        """
        # Create task ID
        task_id = str(uuid.uuid4())
        
        # Create task in database
        task_data = AnalysisTaskCreate(
            task_id=task_id,
            query=query,
            analysis_type=analysis_type,
            data_source=data_source,
            metadata=parameters
        )
        
        db_task = await self.create_analysis_task(db, task_data)
        
        # Update status to processing
        await self.update_analysis_task(db, task_id, AnalysisTaskUpdate(
            status=TaskStatus.PROCESSING,
            started_at=datetime.utcnow()
        ))
        
        try:
            # Run analysis with CrewAI
            result = await self.crew_manager.run_analysis(
                query=query,
                analysis_type=analysis_type,
                data_source=data_source,
                parameters=parameters
            )
            
            # Update task with results
            update_data = AnalysisTaskUpdate(
                status=TaskStatus.COMPLETED if result["status"] == "completed" else TaskStatus.FAILED,
                result=result.get("result"),
                error_message=result.get("error_message"),
                agents_used=result.get("agents_used"),
                iterations_count=result.get("iterations_count", 0),
                completed_at=datetime.utcnow()
            )
            
            await self.update_analysis_task(db, task_id, update_data)
            
            return {
                "task_id": task_id,
                "status": result["status"],
                "result": result.get("result"),
                "error_message": result.get("error_message")
            }
            
        except Exception as e:
            # Update task with error
            await self.update_analysis_task(db, task_id, AnalysisTaskUpdate(
                status=TaskStatus.FAILED,
                error_message=str(e),
                completed_at=datetime.utcnow()
            ))
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error_message": str(e)
            }
    
    async def get_all_tasks(self, db: Session, skip: int = 0, limit: int = 100) -> list[AnalysisTask]:
        """
        Get all analysis tasks with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of analysis tasks
        """
        return db.query(AnalysisTask).offset(skip).limit(limit).all() 
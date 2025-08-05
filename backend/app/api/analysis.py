"""
Analysis API routes for handling analysis requests.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisTaskResponse,
    AnalysisStatus
)

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.post("/", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new analysis task.
    
    This endpoint creates a new analysis task and starts the CrewAI analysis process.
    """
    try:
        analysis_service = AnalysisService()
        
        # Run the analysis
        result = await analysis_service.run_analysis(
            db=db,
            query=request.query,
            analysis_type=request.analysis_type,
            data_source=request.data_source,
            parameters=request.parameters
        )
        
        return AnalysisResponse(
            task_id=result["task_id"],
            status=result["status"],
            message="Analysis task created successfully",
            created_at=result.get("created_at", "2023-12-01T10:00:00Z")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create analysis task: {str(e)}"
        )


@router.get("/{task_id}", response_model=AnalysisTaskResponse)
async def get_analysis_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Get analysis task details and results.
    
    Retrieve the complete information about an analysis task including its status and results.
    """
    analysis_service = AnalysisService()
    task = await analysis_service.get_analysis_task(db, task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis task not found"
        )
    
    return task


@router.get("/{task_id}/status", response_model=AnalysisStatus)
async def get_analysis_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Get analysis task status.
    
    Retrieve the current status of an analysis task.
    """
    analysis_service = AnalysisService()
    task = await analysis_service.get_analysis_task(db, task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis task not found"
        )
    
    return AnalysisStatus(
        task_id=task.task_id,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
        estimated_completion=None  # Could be calculated based on task type and progress
    )


@router.get("/", response_model=List[AnalysisTaskResponse])
async def list_analysis_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all analysis tasks.
    
    Retrieve a paginated list of all analysis tasks.
    """
    analysis_service = AnalysisService()
    tasks = await analysis_service.get_all_tasks(db, skip=skip, limit=limit)
    return tasks


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_analysis_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Cancel an analysis task.
    
    Cancel a pending or processing analysis task.
    """
    analysis_service = AnalysisService()
    task = await analysis_service.get_analysis_task(db, task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis task not found"
        )
    
    if task.status not in ["pending", "processing"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed or failed tasks"
        )
    
    # Update task status to cancelled
    from app.schemas.analysis import AnalysisTaskUpdate
    await analysis_service.update_analysis_task(
        db, 
        task_id, 
        AnalysisTaskUpdate(status="cancelled")
    )
    
    return None 
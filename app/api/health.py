"""
Health check API routes for monitoring application status.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.config import settings

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("/")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns application status and version information.
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }


@router.get("/database")
async def database_health_check(db: Session = Depends(get_db)):
    """
    Database health check endpoint.
    
    Verifies database connectivity and returns status.
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "message": "Database connection successful"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "message": f"Database connection failed: {str(e)}"
        }


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check endpoint.
    
    Comprehensive health check including all system components.
    """
    health_status = {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "components": {}
    }
    
    # Check database
    try:
        db.execute("SELECT 1")
        health_status["components"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Check OpenAI API (if configured)
    if settings.openai_api_key:
        health_status["components"]["openai"] = {
            "status": "configured",
            "message": "OpenAI API key is configured"
        }
    else:
        health_status["components"]["openai"] = {
            "status": "unconfigured",
            "message": "OpenAI API key is not configured"
        }
        health_status["status"] = "unhealthy"
    
    # Check CrewAI settings
    health_status["components"]["crewai"] = {
        "status": "configured",
        "verbose": settings.crewai_verbose,
        "memory": settings.crewai_memory,
        "max_iterations": settings.crewai_max_iterations
    }
    
    return health_status 
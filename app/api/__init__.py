"""
API routes for the Analytic Agent application.
"""

from .analysis import router as analysis_router
from .users import router as users_router
from .health import router as health_router

__all__ = ["analysis_router", "users_router", "health_router"] 
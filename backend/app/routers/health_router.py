"""
Health check router for JurisLink.
Provides endpoint to verify backend connectivity.
"""
from fastapi import APIRouter, HTTPException
from ..db.mongodb import db_client
from ..core.config import settings


router = APIRouter(prefix="/health", tags=["health"])


@router.get("/status")
async def health_check() -> dict:
    """
    Health check endpoint to verify backend and database connectivity.
    
    Returns:
        Status object with backend and database health information
    """
    try:
        # Check database connection
        db_status = "connected"
        if db_client:
            await db_client.admin.command("ping")
        else:
            db_status = "disconnected"
        
        return {
            "status": "ok",
            "backend": "running",
            "database": db_status,
            "environment": settings.ENVIRONMENT,
            "frontend_url": settings.FRONTEND_URL
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

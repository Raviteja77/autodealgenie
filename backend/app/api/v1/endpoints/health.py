"""
Health check endpoint
"""

from datetime import datetime

from fastapi import APIRouter

from app.schemas.schemas import HealthCheck

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(status="healthy", timestamp=datetime.utcnow())

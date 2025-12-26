"""
Health check endpoint
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.mongodb import mongodb
from app.db.redis import redis_client
from app.db.session import get_async_db
from app.schemas.schemas import HealthCheck

router = APIRouter()


@router.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthCheck(status="healthy", timestamp=datetime.utcnow())

@router.get("/health/detailed", tags=["Health"])
async def detailed_health_check(
    response: Response, db: AsyncSession = Depends(get_async_db)
):
    """
    Detailed health check that verifies connectivity to all dependent services.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "postgres": "unhealthy",
            "redis": "unhealthy",
            "mongodb": "unhealthy",
        },
    }
    is_degraded = False

    # Check PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["postgres"] = "healthy"
    except Exception:
        is_degraded = True

    # Check Redis
    try:
        if redis_client.client and await redis_client.client.ping():
            health_status["services"]["redis"] = "healthy"
    except Exception:
        is_degraded = True

    # Check MongoDB
    try:
        if mongodb.client and await mongodb.client.admin.command("ping"):
            health_status["services"]["mongodb"] = "healthy"
    except Exception:
        is_degraded = True

    if is_degraded:
        health_status["status"] = "degraded"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status

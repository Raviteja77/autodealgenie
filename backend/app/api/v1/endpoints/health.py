"""
Health check endpoint
"""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.rabbitmq import rabbitmq
from app.db.redis import redis_client
from app.db.session import get_async_db
from app.schemas.schemas import HealthCheck

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(status="healthy", timestamp=datetime.now(UTC))


@router.get("/health/detailed")
async def detailed_health_check(response: Response, db: AsyncSession = Depends(get_async_db)):
    """
    Detailed health check that verifies connectivity to all dependent services.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "services": {
            "postgres": "unhealthy",
            "redis": "unhealthy",
            "rabbitmq": "unhealthy",
        },
    }
    is_degraded = False

    # Check PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["postgres"] = "healthy"
    except Exception as e:
        logger.warning(f"PostgreSQL health check failed: {e}")
        is_degraded = True

    # Check Redis
    try:
        if redis_client.client and await redis_client.client.ping():
            health_status["services"]["redis"] = "healthy"
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        is_degraded = True

    # Check RabbitMQ
    try:
        if rabbitmq.connection and not rabbitmq.connection.is_closed:
            health_status["services"]["rabbitmq"] = "healthy"
    except Exception as e:
        logger.warning(f"RabbitMQ health check failed: {e}")
        is_degraded = True

    if is_degraded:
        health_status["status"] = "degraded"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status

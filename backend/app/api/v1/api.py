"""
API v1 router configuration
"""

from fastapi import APIRouter

from app.api.v1.endpoints import cars, deals, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(cars.router, prefix="/cars", tags=["cars"])
# Keep deals endpoint for backward compatibility
api_router.include_router(deals.router, prefix="/deals", tags=["deals"])

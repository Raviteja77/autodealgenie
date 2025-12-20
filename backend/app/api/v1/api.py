"""
API v1 router configuration
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    cars,
    comparisons,
    deals,
    evaluations,
    favorites,
    health,
    negotiation,
    preferences,
    recommendations,
    saved_searches,
    webhooks,
)
from app.core.config import settings

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cars.router, prefix="/cars", tags=["cars"])
# Keep deals endpoint for backward compatibility
api_router.include_router(deals.router, prefix="/deals", tags=["deals"])
# Include evaluation endpoints under deals
api_router.include_router(evaluations.router, prefix="/deals", tags=["evaluations"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(preferences.router, prefix="/users", tags=["preferences"])
api_router.include_router(negotiation.router, prefix="/negotiations", tags=["negotiations"])
api_router.include_router(
    recommendations.router, prefix="/recommendations", tags=["recommendations"]
)
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(
    saved_searches.router, prefix="/saved-searches", tags=["saved-searches"]
)
api_router.include_router(comparisons.router, prefix="/vehicles", tags=["comparisons"])

if settings.USE_MOCK_SERVICES:
    from app.api.mock import mock_router

    api_router.include_router(mock_router, prefix="/mock", tags=["mock"])

"""
API v1 router configuration
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, cars, deals, health, webhooks, preferences, recommendations, negotiation

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cars.router, prefix="/cars", tags=["cars"])
# Keep deals endpoint for backward compatibility
api_router.include_router(deals.router, prefix="/deals", tags=["deals"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(preferences.router, prefix="/users", tags=["preferences"])
api_router.include_router(negotiation.router, prefix="/negotiations", tags=["negotiations"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])

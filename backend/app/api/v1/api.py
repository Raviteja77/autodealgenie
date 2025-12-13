"""
API v1 router configuration
"""
from fastapi import APIRouter

from app.api.v1.endpoints import deals, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(deals.router, prefix="/deals", tags=["deals"])

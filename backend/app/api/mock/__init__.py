"""
Mock API router configuration
"""

from fastapi import APIRouter

from app.api.mock.mock_services import router as mock_services_router

mock_router = APIRouter()

# Include mock services under different prefixes for different service types
mock_router.include_router(mock_services_router, prefix="/marketcheck", tags=["mock-marketcheck"])
mock_router.include_router(mock_services_router, prefix="/llm", tags=["mock-llm"])
mock_router.include_router(mock_services_router, prefix="/negotiation", tags=["mock-negotiation"])
mock_router.include_router(mock_services_router, prefix="/evaluation", tags=["mock-evaluation"])

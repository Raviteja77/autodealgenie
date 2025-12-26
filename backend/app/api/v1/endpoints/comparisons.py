"""
Vehicle comparison endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.llm import generate_text
from app.models.models import User
from app.schemas.saved_search_schemas import (
    VehicleComparisonRequest,
    VehicleComparisonResponse,
)

router = APIRouter()


@router.post("/compare", response_model=VehicleComparisonResponse)
async def compare_vehicles(
    request: VehicleComparisonRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Compare 2-3 vehicles using AI analysis

    This endpoint accepts vehicle details and generates a comparative analysis
    using LLM to help users make informed decisions.

    Note: This is a simplified implementation that works with client-provided vehicle data.
    A production implementation would fetch vehicle details from a database/cache.
    """
    if len(request.vins) < 2 or len(request.vins) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide 2-3 vehicles for comparison",
        )

    try:
        # In a full implementation, we would:
        # 1. Fetch vehicle details from database/cache by VIN
        # 2. Enrich with market data and features
        # 3. Generate comparison using LLM

        # For now, return a basic structure that the frontend will populate
        # The frontend already has the vehicle data from search results
        comparison_summary = await generate_text(
            prompt_id="vehicle_comparison",
            variables={
                "vehicle_a": f"VIN: {request.vins[0]}",
                "vehicle_b": f"VIN: {request.vins[1]}",
                "user_needs": "general comparison",
            },
            temperature=0.7,
        )

        # Return structure for frontend to populate
        return VehicleComparisonResponse(
            vehicles=[],  # Frontend will populate with actual vehicle data
            comparison_summary=comparison_summary,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison failed: {str(e)}",
        ) from e

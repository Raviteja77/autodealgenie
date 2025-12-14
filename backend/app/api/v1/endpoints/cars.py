"""
Car search and recommendation endpoints
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.car_schemas import CarSearchRequest, CarSearchResponse
from app.services.car_recommendation_service import car_recommendation_service

router = APIRouter()


@router.post("/search", response_model=CarSearchResponse)
async def search_cars(search_request: CarSearchRequest):
    """
    Search for cars and get AI-powered recommendations

    This endpoint:
    1. Searches MarketCheck API for vehicles matching criteria
    2. Uses LLM to analyze and rank results
    3. Returns top 5 recommended vehicles with explanations
    """
    try:
        result = await car_recommendation_service.search_and_recommend(
            make=search_request.make,
            model=search_request.model,
            budget_min=search_request.budget_min,
            budget_max=search_request.budget_max,
            car_type=search_request.car_type,
            year_min=search_request.year_min,
            year_max=search_request.year_max,
            mileage_max=search_request.mileage_max,
            user_priorities=search_request.user_priorities,
        )

        return CarSearchResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid request: {str(e)}"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        ) from e


@router.get("/health")
async def car_search_health():
    """Health check for car search service"""
    return {
        "status": "healthy",
        "service": "car_search",
        "marketcheck_configured": car_recommendation_service is not None,
    }

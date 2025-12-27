"""
Car search and recommendation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.rate_limiter import car_search_rate_limiter
from app.db.session import get_async_db
from app.models.models import User
from app.schemas.car_schemas import CarSearchRequest, CarSearchResponse
from app.services.car_recommendation_service import car_recommendation_service

router = APIRouter()


@router.post("/search", response_model=CarSearchResponse)
async def search_cars(
    search_request: CarSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Search for cars and get AI-powered recommendations

    This endpoint:
    1. Checks rate limits (100 requests per hour per user)
    2. Checks Redis cache for recent identical searches
    3. Searches MarketCheck API for vehicles matching criteria (with retry logic)
    4. Uses LLM to analyze and rank results
    5. Returns top 5 recommended vehicles with explanations
    6. Stores search history in MongoDB
    7. Triggers webhooks for matching vehicle alerts
    """
    # Check rate limit
    is_allowed, retry_after = await car_search_rate_limiter.is_allowed(current_user.id)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Please retry after {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )

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
            max_results=search_request.max_results,
            user_id=current_user.id,
            db_session=db,
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

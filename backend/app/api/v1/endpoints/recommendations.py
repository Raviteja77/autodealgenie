"""
Car recommendation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.rate_limiter import car_search_rate_limiter
from app.db.session import get_async_db
from app.models.models import User
from app.schemas.car_recommendation import (
    CarRecommendationItem,
    CarRecommendationResponse,
    UserPreferenceInput,
)
from app.services.car_recommendation_service import car_recommendation_service

router = APIRouter()


@router.post("/cars", response_model=CarRecommendationResponse)
async def get_car_recommendations(
    user_preferences: UserPreferenceInput,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get car recommendations based on user preferences

    This endpoint:
    1. Accepts user preferences (budget, body type, features, location)
    2. Queries vehicle data using existing models/repositories
    3. Uses LLM to analyze and rank results
    4. Returns top recommended vehicles with scores and reasoning
    5. Stores search history in MongoDB
    6. Triggers webhooks for matching vehicle alerts

    Returns:
        CarRecommendationResponse with list of recommended vehicles
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
        # Build enhanced user priorities string that includes must-have features
        enhanced_priorities = user_preferences.user_priorities or ""
        if user_preferences.must_have_features:
            features_text = f"Must-have features: {', '.join(user_preferences.must_have_features)}"
            enhanced_priorities = (
                f"{enhanced_priorities}. {features_text}" if enhanced_priorities else features_text
            )

        # Note: Location is captured in UserPreferenceInput but not currently supported
        # by the backend service. It's included in the schema for future enhancement.

        # Call the car recommendation service with user preferences
        result = await car_recommendation_service.search_and_recommend(
            make=user_preferences.make,
            model=user_preferences.model,
            budget_min=user_preferences.budget_min,
            budget_max=user_preferences.budget_max,
            car_type=user_preferences.body_type,
            year_min=user_preferences.year_min,
            year_max=user_preferences.year_max,
            mileage_max=user_preferences.mileage_max,
            user_priorities=enhanced_priorities,
            max_results=user_preferences.max_results,
            user_id=current_user.id,
            db_session=db,
        )

        # Transform the result to match CarRecommendationResponse schema
        recommendations = [
            CarRecommendationItem(**vehicle) for vehicle in result.get("top_vehicles", [])
        ]

        return CarRecommendationResponse(
            recommendations=recommendations,
            total_found=result.get("total_found", 0),
            total_analyzed=result.get("total_analyzed", 0),
            search_criteria=result.get("search_criteria", {}),
            message=result.get("message"),
        )

    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        ) from e
    except ConnectionError as e:
        # Handle external API connection errors
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vehicle search service temporarily unavailable",
        ) from e
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve car recommendations: {str(e)}",
        ) from e

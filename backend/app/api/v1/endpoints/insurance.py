"""
Insurance recommendation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.models.models import User
from app.schemas.insurance_schemas import (
    InsuranceRecommendationRequest,
    InsuranceRecommendationResponse,
)
from app.services.insurance_recommendation_service import InsuranceRecommendationService

router = APIRouter()


@router.post("/recommendations", response_model=InsuranceRecommendationResponse)
async def get_insurance_recommendations(
    request: InsuranceRecommendationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Get personalized insurance recommendations based on vehicle and driver criteria.

    This endpoint provides:
    - Curated list of partner insurance providers that match user criteria
    - Match scores indicating how well each provider fits user needs
    - Estimated monthly and annual premiums for each provider
    - Recommendation reasons explaining why each provider is suggested
    - Affiliate tracking URLs for commission attribution (no PII collected)

    The ranking algorithm considers:
    - Premium competitiveness (40% weight)
    - Coverage fit (25% weight)
    - Vehicle value fit (20% weight)
    - Features and benefits (15% weight)

    Premiums are estimated based on:
    - Vehicle value and age
    - Driver age
    - Coverage type (liability, comprehensive, or full)

    Returns up to 5 top recommendations sorted by match score.
    """
    try:
        recommendations = InsuranceRecommendationService.get_recommendations(request, max_results=5)
        return recommendations
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

"""
Insurance recommendation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user, get_db
from app.models.models import User
from app.schemas.insurance_schemas import (
    InsuranceRecommendationRequest,
    InsuranceRecommendationResponse,
)
from app.services.insurance_recommendation_service import InsuranceRecommendationService
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/recommendations", response_model=InsuranceRecommendationResponse)
async def get_insurance_recommendations(
    request: InsuranceRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
    
    Saves recommendations to database if deal_id is provided for tracking.
    """
    try:
        # Extract deal_id if provided
        deal_id = getattr(request, 'deal_id', None)
        
        # Get recommendations with optional database storage
        recommendations = InsuranceRecommendationService.get_recommendations(
            request=request,
            max_results=5,
            user_id=current_user.id if deal_id else None,
            deal_id=deal_id,
            db_session=db if deal_id else None,
        )
        return recommendations
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

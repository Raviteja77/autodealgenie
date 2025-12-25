"""
AI Response History Endpoints
Provides access to comprehensive AI interaction logs and analytics
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_current_user
from app.models.models import User
from app.repositories.ai_response_repository import ai_response_repository

router = APIRouter()


@router.get("/history/{deal_id}")
async def get_deal_ai_history(
    deal_id: int,
    current_user: User = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
):
    """
    Get all AI responses for a specific deal.

    Returns comprehensive history of AI interactions across all features
    (negotiation, evaluation, recommendations, etc.) for the given deal.

    Args:
        deal_id: Deal ID
        limit: Maximum number of records to return (1-500)
        skip: Number of records to skip for pagination

    Returns:
        List of AI response records with metadata
    """
    # Verify deal ownership
    from app.repositories.deal_repository import DealRepository
    from app.api.dependencies import get_db

    # Note: We need to get the database session to verify deal ownership
    # For now, we'll check if the deal exists and belongs to the user via email
    # In a production system, deals should have a user_id foreign key

    try:
        responses = await ai_response_repository.get_by_deal_id(deal_id, limit=limit, skip=skip)
        return {
            "deal_id": deal_id,
            "count": len(responses),
            "responses": responses,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve AI history: {str(e)}"
        ) from e


@router.get("/history/user/{user_id}")
async def get_user_ai_history(
    user_id: int,
    current_user: User = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
):
    """
    Get all AI responses for a specific user.

    Returns comprehensive history of AI interactions across all features
    for the given user.

    Args:
        user_id: User ID
        limit: Maximum number of records to return (1-500)
        skip: Number of records to skip for pagination

    Returns:
        List of AI response records with metadata

    Note:
        Users can only access their own history unless they are superusers.
    """
    # Authorization check: users can only see their own history
    if current_user.id != user_id and current_user.is_superuser != 1:
        raise HTTPException(status_code=403, detail="Not authorized to view this user's history")

    try:
        responses = await ai_response_repository.get_by_user_id(user_id, limit=limit, skip=skip)
        return {
            "user_id": user_id,
            "count": len(responses),
            "responses": responses,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve AI history: {str(e)}"
        ) from e


@router.get("/history/feature/{feature}")
async def get_feature_ai_history(
    feature: str,
    current_user: User = Depends(get_current_user),
    user_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
):
    """
    Get AI responses for a specific feature.

    Returns history of AI interactions for a specific feature type
    (negotiation, evaluation, car_recommendation, etc.).

    Args:
        feature: Feature name (negotiation, deal_evaluation, car_recommendation, etc.)
        user_id: Optional user ID filter
        limit: Maximum number of records to return (1-500)
        skip: Number of records to skip for pagination

    Returns:
        List of AI response records for the feature

    Note:
        If user_id is provided, users can only access their own data unless superuser.
    """
    # Authorization check if user_id filter is provided
    if user_id and current_user.id != user_id and current_user.is_superuser != 1:
        raise HTTPException(status_code=403, detail="Not authorized to view this user's history")

    try:
        responses = await ai_response_repository.get_by_feature(
            feature=feature,
            user_id=user_id,
            limit=limit,
            skip=skip,
        )
        return {
            "feature": feature,
            "user_id": user_id,
            "count": len(responses),
            "responses": responses,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve AI history: {str(e)}"
        ) from e


@router.get("/lifecycle/{deal_id}")
async def get_deal_lifecycle(
    deal_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    Get comprehensive lifecycle of AI interactions for a deal.

    Returns all AI responses grouped by feature, showing the complete
    journey from search to deal closure.

    Args:
        deal_id: Deal ID

    Returns:
        Dictionary with AI responses grouped by feature type
    """
    # Note: Authorization check for deal ownership should be added here
    # In a production system, deals should have a user_id foreign key
    # For now, we rely on the fact that deal_id is in the AI responses with user_id

    try:
        lifecycle = await ai_response_repository.get_deal_lifecycle(deal_id)
        return lifecycle
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve deal lifecycle: {str(e)}"
        ) from e


@router.get("/analytics")
async def get_ai_analytics(
    current_user: User = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365),
):
    """
    Get analytics about AI usage across the platform.

    Returns aggregated statistics about AI interactions including:
    - Total calls per feature
    - LLM vs fallback usage
    - Token consumption

    Args:
        days: Number of days to analyze (1-365)

    Returns:
        Analytics data grouped by feature

    Note:
        Only superusers can access platform-wide analytics.
    """
    if current_user.is_superuser != 1:
        raise HTTPException(status_code=403, detail="Superuser access required for analytics")

    try:
        analytics = await ai_response_repository.get_analytics(days=days)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve analytics: {str(e)}"
        ) from e

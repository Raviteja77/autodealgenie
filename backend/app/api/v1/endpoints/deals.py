"""
Deal endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.repositories.deal_repository import DealRepository
from app.schemas.schemas import (
    DealCreate,
    DealEvaluationRequest,
    DealEvaluationResponse,
    DealResponse,
    DealUpdate,
)
from app.services.deal_evaluation_service import deal_evaluation_service

router = APIRouter()


@router.post("/", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
def create_deal(
    deal_in: DealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new deal (requires authentication)"""
    repository = DealRepository(db)
    deal = repository.create(deal_in)
    return deal


@router.get("/", response_model=list[DealResponse])
def get_deals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all deals with pagination (requires authentication)"""
    repository = DealRepository(db)
    deals = repository.get_all(skip=skip, limit=limit)
    return deals


@router.get("/search", response_model=DealResponse)
def get_deal_by_email_and_vin(
    customer_email: str,
    vehicle_vin: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get deals by customer email and vehicle VIN (requires authentication)"""
    repository = DealRepository(db)
    deal = repository.get_deal_by_vehicle_and_customer(vehicle_vin, customer_email)
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal with vehicle VIN {vehicle_vin} and customer email {customer_email} not found",
        )
    return deal


@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific deal by ID (requires authentication)"""
    repository = DealRepository(db)
    deal = repository.get(deal_id)
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal with id {deal_id} not found",
        )
    return deal


@router.put("/{deal_id}", response_model=DealResponse)
def update_deal(
    deal_id: int,
    deal_in: DealUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a deal (requires authentication)"""
    repository = DealRepository(db)
    deal = repository.update(deal_id, deal_in)
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal with id {deal_id} not found",
        )
    return deal


@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a deal (requires authentication)"""
    repository = DealRepository(db)
    deleted = repository.delete(deal_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal with id {deal_id} not found",
        )
    return None


@router.post("/evaluate", response_model=DealEvaluationResponse)
async def evaluate_deal(
    evaluation_request: DealEvaluationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Evaluate a car deal and get fair market value analysis

    Returns:
        - fair_value: Estimated fair market value
        - score: Deal quality score (1-10)
        - insights: AI-powered analysis insights
        - talking_points: Negotiation recommendations
    """
    result = await deal_evaluation_service.evaluate_deal(
        vehicle_vin=evaluation_request.vehicle_vin,
        asking_price=evaluation_request.asking_price,
        condition=evaluation_request.condition,
        mileage=evaluation_request.mileage,
    )
    return result

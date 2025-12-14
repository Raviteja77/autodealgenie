"""
Deal endpoints
"""


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.repositories.deal_repository import DealRepository
from app.schemas.schemas import DealCreate, DealResponse, DealUpdate

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
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Deal with id {deal_id} not found"
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
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Deal with id {deal_id} not found"
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
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Deal with id {deal_id} not found"
        )
    return None

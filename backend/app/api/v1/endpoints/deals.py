"""
Deal endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schemas import DealCreate, DealUpdate, DealResponse
from app.repositories.deal_repository import DealRepository

router = APIRouter()


@router.post("/", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
def create_deal(deal_in: DealCreate, db: Session = Depends(get_db)):
    """Create a new deal"""
    repository = DealRepository(db)
    deal = repository.create(deal_in)
    return deal


@router.get("/", response_model=List[DealResponse])
def get_deals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all deals with pagination"""
    repository = DealRepository(db)
    deals = repository.get_all(skip=skip, limit=limit)
    return deals


@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(deal_id: int, db: Session = Depends(get_db)):
    """Get a specific deal by ID"""
    repository = DealRepository(db)
    deal = repository.get(deal_id)
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal with id {deal_id} not found"
        )
    return deal


@router.put("/{deal_id}", response_model=DealResponse)
def update_deal(deal_id: int, deal_in: DealUpdate, db: Session = Depends(get_db)):
    """Update a deal"""
    repository = DealRepository(db)
    deal = repository.update(deal_id, deal_in)
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal with id {deal_id} not found"
        )
    return deal


@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deal(deal_id: int, db: Session = Depends(get_db)):
    """Delete a deal"""
    repository = DealRepository(db)
    deleted = repository.delete(deal_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal with id {deal_id} not found"
        )
    return None

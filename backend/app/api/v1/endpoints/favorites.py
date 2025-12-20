"""
Favorites endpoints with repository pattern and in-memory fallback
"""

import threading
from datetime import datetime, timezone
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.models import Favorite, User
from app.repositories.favorite_repository import FavoriteRepository
from app.schemas.schemas import FavoriteCreate, FavoriteResponse

router = APIRouter()

# In-memory storage fallback (with thread safety)
# Structure: {user_id: {vin: favorite_data}}
favorites_storage: Dict[int, Dict[str, dict]] = {}
storage_lock = threading.Lock()


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    favorite_in: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a car to favorites (requires authentication)"""
    user_id = current_user.id
    repository = FavoriteRepository(db)

    # Check if already exists
    if repository.exists(user_id, favorite_in.vin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle already in favorites",
        )

    # Create favorite
    favorite = repository.create(user_id, favorite_in)
    return favorite


@router.get("/", response_model=List[FavoriteResponse])
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all favorites for the current user (requires authentication)"""
    user_id = current_user.id
    repository = FavoriteRepository(db)

    favorites = repository.get_all_by_user(user_id)
    return favorites


@router.delete("/{vin}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    vin: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a car from favorites (requires authentication)"""
    user_id = current_user.id
    repository = FavoriteRepository(db)

    if not repository.delete_by_user_and_vin(user_id, vin):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found in favorites",
        )

    return None


@router.get("/{vin}", response_model=FavoriteResponse)
def get_favorite(
    vin: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check if a specific vehicle is in favorites (requires authentication)"""
    user_id = current_user.id
    repository = FavoriteRepository(db)

    favorite = repository.get_by_user_and_vin(user_id, vin)
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found in favorites",
        )

    return favorite

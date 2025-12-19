"""
Favorites endpoints - Mock implementation
"""

from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.models.models import User
from app.schemas.schemas import FavoriteCreate, FavoriteResponse

router = APIRouter()

# In-memory storage for favorites (temporary mock implementation)
# Structure: {user_id: {vin: favorite_data}}
favorites_storage: Dict[int, Dict[str, dict]] = {}


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    favorite_in: FavoriteCreate,
    current_user: User = Depends(get_current_user),
):
    """Add a car to favorites (requires authentication)"""
    user_id = current_user.id

    # Initialize user's favorites if not exists
    if user_id not in favorites_storage:
        favorites_storage[user_id] = {}

    # Check if already favorited
    if favorite_in.vin in favorites_storage[user_id]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle already in favorites",
        )

    # Create favorite entry
    favorite_data = {
        "id": f"{user_id}_{favorite_in.vin}",
        "user_id": user_id,
        "vin": favorite_in.vin,
        "make": favorite_in.make,
        "model": favorite_in.model,
        "year": favorite_in.year,
        "price": favorite_in.price,
        "mileage": favorite_in.mileage,
        "fuel_type": favorite_in.fuel_type,
        "location": favorite_in.location,
        "color": favorite_in.color,
        "condition": favorite_in.condition,
        "image": favorite_in.image,
        "created_at": datetime.now(datetime.UTC),
    }

    favorites_storage[user_id][favorite_in.vin] = favorite_data

    return FavoriteResponse(**favorite_data)


@router.get("/", response_model=List[FavoriteResponse])
def get_favorites(
    current_user: User = Depends(get_current_user),
):
    """Get all favorites for the current user (requires authentication)"""
    user_id = current_user.id

    # Return empty list if user has no favorites
    if user_id not in favorites_storage:
        return []

    # Return all favorites for the user
    return [FavoriteResponse(**fav) for fav in favorites_storage[user_id].values()]


@router.delete("/{vin}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    vin: str,
    current_user: User = Depends(get_current_user),
):
    """Remove a car from favorites (requires authentication)"""
    user_id = current_user.id

    # Check if user has favorites
    if user_id not in favorites_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found in favorites",
        )

    # Check if vehicle is in favorites
    if vin not in favorites_storage[user_id]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found in favorites",
        )

    # Remove from favorites
    del favorites_storage[user_id][vin]

    return None


@router.get("/{vin}", response_model=FavoriteResponse)
def get_favorite(
    vin: str,
    current_user: User = Depends(get_current_user),
):
    """Check if a specific vehicle is in favorites (requires authentication)"""
    user_id = current_user.id

    # Check if user has favorites
    if user_id not in favorites_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found in favorites",
        )

    # Check if vehicle is in favorites
    if vin not in favorites_storage[user_id]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found in favorites",
        )

    return FavoriteResponse(**favorites_storage[user_id][vin])

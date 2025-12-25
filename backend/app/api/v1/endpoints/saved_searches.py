"""
Saved searches endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.repositories.saved_search_repository import saved_search_repository
from app.schemas.saved_search_schemas import (
    SavedSearchCreate,
    SavedSearchList,
    SavedSearchResponse,
    SavedSearchUpdate,
)

router = APIRouter()


@router.post(
    "/", response_model=SavedSearchResponse, status_code=status.HTTP_201_CREATED
)
async def create_saved_search(
    search: SavedSearchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new saved search for the current user
    """
    try:
        # Convert Pydantic model to dict
        search_data = search.model_dump()

        # Create saved search
        saved_search = saved_search_repository.create(
            db=db, user_id=current_user.id, search_data=search_data
        )

        return saved_search

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create saved search: {str(e)}",
        ) from e


@router.get("/", response_model=SavedSearchList)
async def get_saved_searches(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all saved searches for the current user
    """
    try:
        searches = saved_search_repository.get_user_searches(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
        total = saved_search_repository.count_user_searches(
            db=db, user_id=current_user.id
        )

        return SavedSearchList(searches=searches, total=total)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve saved searches: {str(e)}",
        ) from e


@router.get("/{search_id}", response_model=SavedSearchResponse)
async def get_saved_search(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific saved search by ID
    """
    saved_search = saved_search_repository.get_by_id(
        db=db, search_id=search_id, user_id=current_user.id
    )

    if not saved_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Saved search not found"
        )

    return saved_search


@router.put("/{search_id}", response_model=SavedSearchResponse)
async def update_saved_search(
    search_id: int,
    search_update: SavedSearchUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a saved search
    """
    # Convert Pydantic model to dict, excluding None values
    update_data = search_update.model_dump(exclude_unset=True)

    updated_search = saved_search_repository.update(
        db=db, search_id=search_id, user_id=current_user.id, update_data=update_data
    )

    if not updated_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Saved search not found"
        )

    return updated_search


@router.delete("/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_search(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a saved search
    """
    deleted = saved_search_repository.delete(
        db=db, search_id=search_id, user_id=current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Saved search not found"
        )

    return None

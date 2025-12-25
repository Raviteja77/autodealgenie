"""
User preferences API endpoints
Demonstrates how to use the user_preferences_service
"""

from fastapi import APIRouter, HTTPException, status

from app.services.user_preferences_service import user_preferences_service

router = APIRouter()


@router.post("/preferences/{user_id}", status_code=status.HTTP_201_CREATED)
async def save_preferences(
    user_id: str,
    makes: list[str] | None = None,
    budget_range: dict[str, int] | None = None,
    year_range: dict[str, int] | None = None,
    body_types: list[str] | None = None,
    features: list[str] | None = None,
):
    """
    Save user car preferences

    Example request body:
    ```json
    {
      "makes": ["Toyota", "Honda"],
      "budget_range": {"min": 20000, "max": 35000},
      "year_range": {"min": 2020, "max": 2024},
      "body_types": ["sedan", "suv"],
      "features": ["sunroof", "leather seats"]
    }
    ```
    """
    try:
        await user_preferences_service.save_user_preferences(
            user_id=user_id,
            makes=makes,
            budget_range=budget_range,
            year_range=year_range,
            body_types=body_types,
            features=features,
        )
        return {"message": "Preferences saved successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save preferences: {str(e)}",
        ) from e


@router.get("/preferences/{user_id}")
async def get_preferences(user_id: str):
    """
    Retrieve all saved preferences for a user

    Returns a list of preference documents sorted by creation date (newest first)
    """
    try:
        preferences = await user_preferences_service.get_user_preferences(user_id)
        return {
            "user_id": user_id,
            "preferences": preferences,
            "count": len(preferences),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve preferences: {str(e)}",
        ) from e


@router.put("/preferences/{user_id}")
async def update_preferences(
    user_id: str,
    makes: list[str] | None = None,
    budget_range: dict[str, int] | None = None,
    year_range: dict[str, int] | None = None,
    body_types: list[str] | None = None,
    features: list[str] | None = None,
):
    """
    Update user car preferences

    Creates a new preference document with merged data from the most recent preference
    """
    try:
        await user_preferences_service.update_user_preferences(
            user_id=user_id,
            makes=makes,
            budget_range=budget_range,
            year_range=year_range,
            body_types=body_types,
            features=features,
        )
        return {"message": "Preferences updated successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}",
        ) from e


@router.delete("/preferences/cleanup")
async def cleanup_old_preferences(days: int = 30):
    """
    Delete preferences older than specified number of days

    Args:
        days: Number of days (default: 30)

    Returns:
        Number of documents deleted
    """
    try:
        deleted_count = await user_preferences_service.delete_older_preferences(
            days=days
        )
        return {
            "message": "Cleanup completed",
            "deleted_count": deleted_count,
            "days": days,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup preferences: {str(e)}",
        ) from e

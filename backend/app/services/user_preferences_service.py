"""
User preferences service for MongoDB operations
Manages user car search preferences with CRUD operations
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

from app.db.mongodb import mongodb


class UserPreference(dict):
    """
    MongoDB document schema for user preferences
    Represents the structure stored in MongoDB
    """

    def __init__(
        self,
        user_id: str,
        preferences: dict[str, Any],
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(
            user_id=user_id,
            preferences=preferences,
            created_at=created_at or datetime.now(UTC),
            updated_at=updated_at or datetime.now(UTC),
        )


class UserPreferencesService:
    """Service for managing user car preferences in MongoDB"""

    COLLECTION_NAME = "user_preferences"

    def __init__(self):
        """Initialize the service"""
        self._collection: AsyncIOMotorCollection | None = None

    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection"""
        if self._collection is None:
            self._collection = mongodb.get_collection(self.COLLECTION_NAME)
        return self._collection

    async def save_user_preferences(
        self,
        user_id: str,
        makes: list[str] | None = None,
        budget_range: dict[str, int] | None = None,
        year_range: dict[str, int] | None = None,
        body_types: list[str] | None = None,
        features: list[str] | None = None,
    ) -> None:
        """
        Save user search criteria to MongoDB

        Args:
            user_id: User identifier
            makes: List of preferred car makes
            budget_range: Budget range with min and max
            year_range: Year range with min and max
            body_types: List of preferred body types
            features: List of desired features
        """
        preferences = {
            "makes": makes or [],
            "budget_range": budget_range or {"min": 0, "max": 0},
            "year_range": year_range or {"min": 0, "max": 0},
            "body_types": body_types or [],
            "features": features or [],
        }

        document = UserPreference(
            user_id=user_id,
            preferences=preferences,
        )

        await self.collection.insert_one(dict(document))

    async def get_user_preferences(self, user_id: str) -> list[dict[str, Any]]:
        """
        Retrieve all saved searches for a specific user

        Args:
            user_id: User identifier

        Returns:
            List of user preference documents
        """
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        preferences = await cursor.to_list(length=None)
        return preferences

    async def update_user_preferences(
        self,
        user_id: str,
        makes: list[str] | None = None,
        budget_range: dict[str, int] | None = None,
        year_range: dict[str, int] | None = None,
        body_types: list[str] | None = None,
        features: list[str] | None = None,
    ) -> None:
        """
        Update existing preferences by creating a new document with updated timestamp

        Args:
            user_id: User identifier
            makes: List of preferred car makes
            budget_range: Budget range with min and max
            year_range: Year range with min and max
            body_types: List of preferred body types
            features: List of desired features
        """
        # Get the most recent preference to merge with new data
        existing = await self.collection.find_one(
            {"user_id": user_id}, sort=[("created_at", -1)]
        )

        # Prepare updated preferences
        if existing and "preferences" in existing:
            updated_preferences = existing["preferences"].copy()
        else:
            updated_preferences = {
                "makes": [],
                "budget_range": {"min": 0, "max": 0},
                "year_range": {"min": 0, "max": 0},
                "body_types": [],
                "features": [],
            }

        # Update only provided fields
        if makes is not None:
            updated_preferences["makes"] = makes
        if budget_range is not None:
            updated_preferences["budget_range"] = budget_range
        if year_range is not None:
            updated_preferences["year_range"] = year_range
        if body_types is not None:
            updated_preferences["body_types"] = body_types
        if features is not None:
            updated_preferences["features"] = features

        # Create new document with updated data
        document = UserPreference(
            user_id=user_id,
            preferences=updated_preferences,
        )

        await self.collection.insert_one(dict(document))

    async def delete_older_preferences(self, days: int = 30) -> int:
        """
        Delete preferences older than specified number of days

        Args:
            days: Number of days (default: 30)

        Returns:
            Number of documents deleted
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        result = await self.collection.delete_many({"created_at": {"$lt": cutoff_date}})
        return result.deleted_count


# Singleton instance
user_preferences_service = UserPreferencesService()

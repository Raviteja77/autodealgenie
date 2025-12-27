"""
Repository for user preferences operations in PostgreSQL
Replaces MongoDB-based user_preferences_service.py
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.jsonb_data import UserPreference


class UserPreferencesRepository:
    """Repository for managing user car preferences in PostgreSQL"""

    def __init__(self, db: Session):
        self.db = db

    def save_user_preferences(
        self,
        user_id: str,
        makes: list[str] | None = None,
        budget_range: dict[str, int] | None = None,
        year_range: dict[str, int] | None = None,
        body_types: list[str] | None = None,
        features: list[str] | None = None,
    ) -> UserPreference:
        """
        Save user search criteria to PostgreSQL

        Args:
            user_id: User identifier
            makes: List of preferred car makes
            budget_range: Budget range with min and max
            year_range: Year range with min and max
            body_types: List of preferred body types
            features: List of desired features

        Returns:
            Created UserPreference instance
        """
        preferences = {
            "makes": makes or [],
            "budget_range": budget_range or {"min": 0, "max": 0},
            "year_range": year_range or {"min": 0, "max": 0},
            "body_types": body_types or [],
            "features": features or [],
        }

        user_pref = UserPreference(
            user_id=user_id,
            preferences=preferences,
        )

        self.db.add(user_pref)
        self.db.commit()
        self.db.refresh(user_pref)
        return user_pref

    def get_user_preferences(self, user_id: str) -> list[UserPreference]:
        """
        Retrieve all saved preferences for a specific user

        Args:
            user_id: User identifier

        Returns:
            List of UserPreference instances
        """
        return (
            self.db.query(UserPreference)
            .filter(UserPreference.user_id == user_id)
            .order_by(desc(UserPreference.created_at))
            .all()
        )

    def get_latest_user_preference(self, user_id: str) -> UserPreference | None:
        """
        Get the most recent preference for a user

        Args:
            user_id: User identifier

        Returns:
            Latest UserPreference or None
        """
        return (
            self.db.query(UserPreference)
            .filter(UserPreference.user_id == user_id)
            .order_by(desc(UserPreference.created_at))
            .first()
        )

    def update_user_preferences(
        self,
        user_id: str,
        makes: list[str] | None = None,
        budget_range: dict[str, int] | None = None,
        year_range: dict[str, int] | None = None,
        body_types: list[str] | None = None,
        features: list[str] | None = None,
    ) -> UserPreference:
        """
        Update existing preferences by creating a new record with updated timestamp

        Args:
            user_id: User identifier
            makes: List of preferred car makes
            budget_range: Budget range with min and max
            year_range: Year range with min and max
            body_types: List of preferred body types
            features: List of desired features

        Returns:
            New UserPreference instance
        """
        # Get the most recent preference to merge with new data
        existing = self.get_latest_user_preference(user_id)

        # Prepare updated preferences
        if existing and existing.preferences:
            updated_preferences = existing.preferences.copy()
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

        # Create new record with updated data
        return self.save_user_preferences(
            user_id=user_id,
            makes=updated_preferences.get("makes"),
            budget_range=updated_preferences.get("budget_range"),
            year_range=updated_preferences.get("year_range"),
            body_types=updated_preferences.get("body_types"),
            features=updated_preferences.get("features"),
        )

    def delete_older_preferences(self, days: int = 30) -> int:
        """
        Delete preferences older than specified number of days

        Args:
            days: Number of days (default: 30)

        Returns:
            Number of records deleted
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        result = (
            self.db.query(UserPreference).filter(UserPreference.created_at < cutoff_date).delete()
        )
        self.db.commit()
        return result

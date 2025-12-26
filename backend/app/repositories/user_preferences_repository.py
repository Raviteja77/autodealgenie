from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_preferences import UserPreferences


class UserPreferencesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: str, prefs: dict) -> UserPreferences:
        """Create new user preferences"""
        pass

    async def get_by_user(self, user_id: str) -> UserPreferences | None:
        """Retrieve user's latest preferences"""
        pass

    async def update(self, pref_id: str, updates: dict) -> UserPreferences:
        """Update existing preferences"""
        pass

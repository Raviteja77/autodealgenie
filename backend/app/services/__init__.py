"""Services package initialization"""

from app.services.user_preferences_service import (
    UserPreferencesService,
    user_preferences_service,
)

__all__ = ["UserPreferencesService", "user_preferences_service"]

"""Services package initialization"""

from app.services.marketcheck_service import MarketCheckService, marketcheck_service

# Note: user_preferences_service has been removed and replaced with
# UserPreferencesRepository that requires database session injection

__all__ = ["MarketCheckService", "marketcheck_service"]

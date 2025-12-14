"""
User preferences schemas for validation and serialization
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class BudgetRange(BaseModel):
    """Budget range for car search preferences"""

    min: float = Field(..., ge=0, description="Minimum budget")
    max: float = Field(..., gt=0, description="Maximum budget")

    @field_validator("max")
    @classmethod
    def validate_max_greater_than_min(cls, v: float, info: Any) -> float:
        """Validate that max is greater than min"""
        if "min" in info.data and v <= info.data["min"]:
            raise ValueError("max must be greater than min")
        return v


class CarType(str, Enum):
    """Car type enumeration"""

    SEDAN = "sedan"
    SUV = "suv"
    TRUCK = "truck"
    COUPE = "coupe"
    HATCHBACK = "hatchback"
    CONVERTIBLE = "convertible"
    WAGON = "wagon"
    VAN = "van"
    OTHER = "other"


class FuelType(str, Enum):
    """Fuel type enumeration"""

    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"
    PLUG_IN_HYBRID = "plug_in_hybrid"


class TransmissionType(str, Enum):
    """Transmission type enumeration"""

    AUTOMATIC = "automatic"
    MANUAL = "manual"
    CVT = "cvt"


class CarPreferences(BaseModel):
    """Car preferences schema"""

    make: str | None = Field(None, min_length=1, max_length=100, description="Preferred car make")
    model: str | None = Field(None, min_length=1, max_length=100, description="Preferred car model")
    budget: BudgetRange | None = Field(None, description="Budget range")
    car_type: CarType | None = Field(None, description="Preferred car type")
    year_min: int | None = Field(None, ge=1900, le=2100, description="Minimum year")
    year_max: int | None = Field(None, ge=1900, le=2100, description="Maximum year")
    mileage_max: int | None = Field(None, ge=0, description="Maximum mileage")
    fuel_type: FuelType | None = Field(None, description="Preferred fuel type")
    transmission: TransmissionType | None = Field(None, description="Preferred transmission")
    colors: list[str] | None = Field(None, max_length=10, description="Preferred exterior colors")
    features: list[str] | None = Field(None, max_length=20, description="Desired features")
    priorities: str | None = Field(
        None, max_length=500, description="User priorities and requirements"
    )

    @field_validator("year_max")
    @classmethod
    def validate_year_range(cls, v: int | None, info: Any) -> int | None:
        """Validate that year_max is greater than or equal to year_min"""
        if v is not None and "year_min" in info.data and info.data["year_min"] is not None:
            if v < info.data["year_min"]:
                raise ValueError("year_max must be greater than or equal to year_min")
        return v


class NotificationPreferences(BaseModel):
    """Notification preferences schema"""

    email_notifications: bool = Field(default=True, description="Enable email notifications")
    deal_alerts: bool = Field(default=True, description="Receive deal alerts")
    price_drop_alerts: bool = Field(default=True, description="Receive price drop alerts")
    new_inventory_alerts: bool = Field(default=False, description="Receive new inventory alerts")
    weekly_digest: bool = Field(default=False, description="Receive weekly digest")


class SearchPreferences(BaseModel):
    """Search preferences schema"""

    default_location: str | None = Field(
        None, min_length=1, max_length=200, description="Default search location"
    )
    search_radius_miles: int | None = Field(
        None, ge=1, le=500, description="Search radius in miles"
    )
    auto_save_searches: bool = Field(default=True, description="Automatically save searches")
    results_per_page: int = Field(default=10, ge=5, le=100, description="Results per page")


class UserPreferencesBase(BaseModel):
    """Base user preferences schema"""

    car_preferences: CarPreferences = Field(
        default_factory=CarPreferences, description="Car search preferences"
    )
    notification_preferences: NotificationPreferences = Field(
        default_factory=NotificationPreferences, description="Notification preferences"
    )
    search_preferences: SearchPreferences = Field(
        default_factory=SearchPreferences, description="Search preferences"
    )


class UserPreferencesCreate(UserPreferencesBase):
    """Schema for creating user preferences"""

    user_id: int = Field(..., gt=0, description="User ID")


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences"""

    car_preferences: CarPreferences | None = None
    notification_preferences: NotificationPreferences | None = None
    search_preferences: SearchPreferences | None = None


class UserPreferencesResponse(UserPreferencesBase):
    """Schema for user preferences response"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class SavedSearch(BaseModel):
    """Saved search schema"""

    name: str = Field(..., min_length=1, max_length=100, description="Search name")
    criteria: CarPreferences = Field(..., description="Search criteria")
    alert_enabled: bool = Field(default=False, description="Enable alerts for this search")


class SavedSearchCreate(SavedSearch):
    """Schema for creating a saved search"""

    user_id: int = Field(..., gt=0, description="User ID")


class SavedSearchResponse(SavedSearch):
    """Schema for saved search response"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

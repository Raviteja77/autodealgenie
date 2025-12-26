"""
Pydantic schemas for saved searches
"""

from datetime import datetime

from pydantic import BaseModel, Field


class SavedSearchBase(BaseModel):
    """Base schema for saved search"""

    name: str = Field(..., min_length=1, max_length=255, description="Name of the saved search")
    make: str | None = Field(None, max_length=100)
    model: str | None = Field(None, max_length=100)
    budget_min: float | None = Field(None, ge=0)
    budget_max: float | None = Field(None, ge=0)
    car_type: str | None = Field(None, max_length=50)
    year_min: int | None = Field(None, ge=1900, le=2100)
    year_max: int | None = Field(None, ge=1900, le=2100)
    mileage_max: int | None = Field(None, ge=0)
    fuel_type: str | None = Field(None, max_length=50)
    transmission: str | None = Field(None, max_length=50)
    condition: str | None = Field(None, max_length=50)
    user_priorities: str | None = None
    notification_enabled: bool = True


class SavedSearchCreate(SavedSearchBase):
    """Schema for creating a saved search"""

    pass


class SavedSearchUpdate(BaseModel):
    """Schema for updating a saved search"""

    name: str | None = Field(None, min_length=1, max_length=255)
    make: str | None = Field(None, max_length=100)
    model: str | None = Field(None, max_length=100)
    budget_min: float | None = Field(None, ge=0)
    budget_max: float | None = Field(None, ge=0)
    car_type: str | None = Field(None, max_length=50)
    year_min: int | None = Field(None, ge=1900, le=2100)
    year_max: int | None = Field(None, ge=1900, le=2100)
    mileage_max: int | None = Field(None, ge=0)
    fuel_type: str | None = Field(None, max_length=50)
    transmission: str | None = Field(None, max_length=50)
    condition: str | None = Field(None, max_length=50)
    user_priorities: str | None = None
    notification_enabled: bool | None = None


class SavedSearchResponse(SavedSearchBase):
    """Schema for saved search response"""

    id: int
    user_id: int
    new_matches_count: int = 0
    last_checked: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class SavedSearchList(BaseModel):
    """Schema for list of saved searches"""

    searches: list[SavedSearchResponse]
    total: int


class VehicleComparisonRequest(BaseModel):
    """Schema for vehicle comparison request"""

    vins: list[str] = Field(
        ..., min_length=2, max_length=3, description="List of 2-3 VINs to compare"
    )


class VehicleComparisonFeature(BaseModel):
    """Schema for a single vehicle feature in comparison"""

    vin: str
    make: str
    model: str
    year: int
    price: float
    mileage: int
    fuel_type: str | None = None
    transmission: str | None = None
    condition: str | None = None
    features: list[str] = []
    pros: list[str] = []
    cons: list[str] = []
    recommendation_score: float | None = None


class VehicleComparisonResponse(BaseModel):
    """Schema for vehicle comparison response"""

    vehicles: list[VehicleComparisonFeature]
    comparison_summary: str | None = None

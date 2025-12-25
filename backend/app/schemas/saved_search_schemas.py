"""
Pydantic schemas for saved searches
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SavedSearchBase(BaseModel):
    """Base schema for saved search"""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Name of the saved search"
    )
    make: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    car_type: Optional[str] = Field(None, max_length=50)
    year_min: Optional[int] = Field(None, ge=1900, le=2100)
    year_max: Optional[int] = Field(None, ge=1900, le=2100)
    mileage_max: Optional[int] = Field(None, ge=0)
    fuel_type: Optional[str] = Field(None, max_length=50)
    transmission: Optional[str] = Field(None, max_length=50)
    condition: Optional[str] = Field(None, max_length=50)
    user_priorities: Optional[str] = None
    notification_enabled: bool = True


class SavedSearchCreate(SavedSearchBase):
    """Schema for creating a saved search"""

    pass


class SavedSearchUpdate(BaseModel):
    """Schema for updating a saved search"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    make: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    car_type: Optional[str] = Field(None, max_length=50)
    year_min: Optional[int] = Field(None, ge=1900, le=2100)
    year_max: Optional[int] = Field(None, ge=1900, le=2100)
    mileage_max: Optional[int] = Field(None, ge=0)
    fuel_type: Optional[str] = Field(None, max_length=50)
    transmission: Optional[str] = Field(None, max_length=50)
    condition: Optional[str] = Field(None, max_length=50)
    user_priorities: Optional[str] = None
    notification_enabled: Optional[bool] = None


class SavedSearchResponse(SavedSearchBase):
    """Schema for saved search response"""

    id: int
    user_id: int
    new_matches_count: int = 0
    last_checked: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

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
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    condition: Optional[str] = None
    features: list[str] = []
    pros: list[str] = []
    cons: list[str] = []
    recommendation_score: Optional[float] = None


class VehicleComparisonResponse(BaseModel):
    """Schema for vehicle comparison response"""

    vehicles: list[VehicleComparisonFeature]
    comparison_summary: Optional[str] = None

"""
Pydantic schemas for car search and recommendations
"""

from pydantic import BaseModel, Field


class CarSearchRequest(BaseModel):
    """Schema for car search request"""

    make: str | None = Field(None, description="Vehicle make (e.g., 'Toyota')")
    model: str | None = Field(None, description="Vehicle model (e.g., 'RAV4')")
    budget_min: int | None = Field(None, description="Minimum budget", ge=0)
    budget_max: int | None = Field(None, description="Maximum budget", ge=0)
    car_type: str | None = Field(None, description="Type of car: 'new', 'used', or 'certified'")
    year_min: int | None = Field(None, description="Minimum year", ge=1900, le=2100)
    year_max: int | None = Field(None, description="Maximum year", ge=1900, le=2100)
    mileage_max: int | None = Field(None, description="Maximum mileage", ge=0)
    user_priorities: str | None = Field(
        None, description="User's specific priorities or preferences"
    )
    max_results: int = Field(50, description="Maximum number of results to return", ge=1, le=100)


class SearchCriteria(BaseModel):
    """Schema for search criteria in response"""

    make: str | None = None
    model: str | None = None
    price_min: int | None = None
    price_max: int | None = None
    condition: str | None = None
    year_min: int | None = None
    year_max: int | None = None
    mileage_max: int | None = None
    location: str | None = None


class VehicleRecommendation(BaseModel):
    """Schema for individual vehicle recommendation"""

    vin: str | None = None
    make: str | None = None
    model: str | None = None
    year: int | None = None
    trim: str | None = None
    mileage: int | None = None
    price: float | None = None
    msrp: float | None = None
    location: str | None = None
    dealer_name: str | None = None
    dealer_contact: str | None = None
    photo_links: list[str] = Field(default_factory=list)
    vdp_url: str | None = None
    exterior_color: str | None = None
    interior_color: str | None = None
    drivetrain: str | None = None
    transmission: str | None = None
    engine: str | None = None
    fuel_type: str | None = None
    carfax_1_owner: bool | None = None
    carfax_clean_title: bool | None = None
    inventory_type: str | None = None
    days_on_market: int | None = None
    recommendation_score: float | None = None
    highlights: list[str] = Field(default_factory=list)
    recommendation_summary: str | None = None


class CarSearchResponse(BaseModel):
    """Schema for car search response"""

    search_criteria: SearchCriteria
    top_vehicles: list[VehicleRecommendation]
    total_found: int = 0
    total_analyzed: int = 0
    message: str | None = None

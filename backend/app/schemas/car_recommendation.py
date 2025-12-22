"""
Pydantic schemas for car recommendation pipeline
"""

from pydantic import BaseModel, Field, model_validator


class UserPreferenceInput(BaseModel):
    """Schema for user preferences input to car recommendation pipeline"""

    budget_min: int | None = Field(None, description="Minimum budget", ge=0)
    budget_max: int | None = Field(None, description="Maximum budget", ge=0)
    body_type: str | None = Field(None, description="Preferred body type (e.g., sedan, suv, truck)")
    must_have_features: list[str] | None = Field(
        None, description="Must-have features for the vehicle"
    )
    location: str | None = Field(None, description="Location for car search")
    make: str | None = Field(None, description="Preferred vehicle make")
    model: str | None = Field(None, description="Preferred vehicle model")
    year_min: int | None = Field(None, description="Minimum year", ge=1900, le=2100)
    year_max: int | None = Field(None, description="Maximum year", ge=1900, le=2100)
    mileage_max: int | None = Field(None, description="Maximum mileage", ge=0)
    user_priorities: str | None = Field(
        None, description="User's specific priorities or preferences"
    )
    max_results: int | None = Field(
        None, description="Maximum number of results to analyze", ge=1, le=100
    )

    @model_validator(mode="after")
    def validate_ranges(self) -> "UserPreferenceInput":
        """Validate that max values are greater than min values"""
        # Validate budget range
        if (
            self.budget_min is not None
            and self.budget_max is not None
            and self.budget_max <= self.budget_min
        ):
            raise ValueError("budget_max must be greater than budget_min")

        # Validate year range
        if (
            self.year_min is not None
            and self.year_max is not None
            and self.year_max < self.year_min
        ):
            raise ValueError("year_max must be greater than or equal to year_min")

        return self


class CarRecommendationItem(BaseModel):
    """Schema for individual car recommendation with scoring and reasoning"""

    # Vehicle details
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

    # Recommendation metadata
    recommendation_score: float | None = Field(
        None,
        description="Score indicating how well this vehicle matches criteria (1-10)",
        ge=0,
        le=10,
    )
    highlights: list[str] = Field(
        default_factory=list, description="Key highlights and reasons to consider this vehicle"
    )
    recommendation_summary: str | None = Field(
        None, description="Brief summary of why this vehicle is recommended"
    )


class CarRecommendationResponse(BaseModel):
    """Schema for car recommendation response with list of recommendations and metadata"""

    recommendations: list[CarRecommendationItem] = Field(
        default_factory=list, description="List of recommended vehicles"
    )
    total_found: int = Field(default=0, description="Total number of vehicles found")
    total_analyzed: int = Field(default=0, description="Total number of vehicles analyzed")
    search_criteria: dict = Field(default_factory=dict, description="Search criteria used")
    message: str | None = Field(None, description="Additional message or information")

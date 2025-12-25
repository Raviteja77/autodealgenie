"""
Pydantic schemas for insurance recommendations
"""

from pydantic import BaseModel, Field, field_validator


class InsuranceProviderInfo(BaseModel):
    """Schema for insurance provider information"""

    provider_id: str = Field(..., description="Unique identifier for the insurance provider")
    name: str = Field(..., description="Insurance provider name")
    description: str = Field(..., description="Brief description of the insurance provider")
    logo_url: str | None = Field(None, description="URL to insurance provider logo")

    # Coverage criteria
    coverage_types: list[str] = Field(
        default_factory=list, description="Types of coverage offered (e.g., liability, full)"
    )
    min_vehicle_value: float = Field(..., description="Minimum vehicle value for coverage")
    max_vehicle_value: float = Field(..., description="Maximum vehicle value for coverage")
    min_driver_age: int = Field(default=16, description="Minimum driver age")
    max_driver_age: int = Field(default=100, description="Maximum driver age")

    # Premium information (monthly rates)
    premium_range_min: float = Field(..., description="Minimum monthly premium")
    premium_range_max: float = Field(..., description="Maximum monthly premium")

    # Features and benefits
    features: list[str] = Field(default_factory=list, description="Key features")
    benefits: list[str] = Field(default_factory=list, description="Key benefits")

    # Affiliate tracking
    affiliate_url: str = Field(..., description="Affiliate tracking URL")
    referral_code: str | None = Field(None, description="Referral code for tracking")


class InsuranceRecommendationRequest(BaseModel):
    """Request schema for insurance recommendations"""

    vehicle_value: float = Field(..., gt=0, description="Estimated vehicle value")
    vehicle_age: int = Field(..., ge=0, description="Vehicle age in years")
    vehicle_make: str = Field(..., description="Vehicle make")
    vehicle_model: str = Field(..., description="Vehicle model")
    coverage_type: str = Field(
        ...,
        description="Desired coverage type: liability, comprehensive, or full",
    )
    driver_age: int = Field(..., gt=0, le=100, description="Driver age")
    deal_id: int | None = Field(None, description="Optional deal ID to associate these recommendations")

    @field_validator("coverage_type")
    @classmethod
    def validate_coverage_type(cls, v: str) -> str:
        """Validate coverage type is one of the allowed values"""
        allowed = ["liability", "comprehensive", "full"]
        if v.lower() not in allowed:
            raise ValueError(f"coverage_type must be one of: {', '.join(allowed)}")
        return v.lower()

    @field_validator("driver_age")
    @classmethod
    def validate_driver_age(cls, v: int) -> int:
        """Validate driver age is reasonable"""
        if v < 16:
            raise ValueError("driver_age must be at least 16")
        if v > 100:
            raise ValueError("driver_age must be at most 100")
        return v


class InsuranceMatch(BaseModel):
    """Schema for a matched insurance provider with recommendation details"""

    provider: InsuranceProviderInfo = Field(..., description="Insurance provider information")
    match_score: float = Field(..., ge=0, le=100, description="Match score (0-100)")
    estimated_monthly_premium: float = Field(..., description="Estimated monthly premium")
    estimated_annual_premium: float = Field(..., description="Estimated annual premium")
    recommendation_reason: str = Field(..., description="Why this provider is recommended")
    rank: int = Field(..., ge=1, description="Ranking position")


class InsuranceRecommendationResponse(BaseModel):
    """Response schema for insurance recommendations"""

    recommendations: list[InsuranceMatch] = Field(
        default_factory=list, description="List of recommended insurance providers"
    )
    total_matches: int = Field(..., description="Total number of matching providers")
    request_summary: dict = Field(..., description="Summary of request parameters")

"""
Pydantic schemas for loan applications
"""

from pydantic import BaseModel, Field, field_validator


class LoanCalculationRequest(BaseModel):
    """Request schema for loan payment calculation"""

    loan_amount: float = Field(..., gt=0, description="Total loan amount")
    down_payment: float = Field(default=0.0, ge=0, description="Down payment amount")
    loan_term_months: int = Field(..., gt=0, description="Loan term in months")
    credit_score_range: str = Field(
        ..., description="Credit score range: excellent, good, fair, or poor"
    )
    deal_id: int | None = Field(
        None, description="Optional deal ID to associate this calculation"
    )

    @field_validator("credit_score_range")
    @classmethod
    def validate_credit_score_range(cls, v: str) -> str:
        """Validate credit score range is one of the allowed values"""
        allowed = ["excellent", "good", "fair", "poor"]
        if v.lower() not in allowed:
            raise ValueError(f"credit_score_range must be one of: {', '.join(allowed)}")
        return v.lower()

    @field_validator("loan_term_months")
    @classmethod
    def validate_loan_term(cls, v: int) -> int:
        """Validate loan term is a reasonable value"""
        if v <= 0:
            raise ValueError("loan_term_months must be greater than 0")
        return v


class LoanCalculationResponse(BaseModel):
    """Response schema for loan payment calculation"""

    monthly_payment: float = Field(..., description="Calculated monthly payment")
    total_interest: float = Field(..., description="Total interest over loan term")
    total_amount: float = Field(..., description="Total amount to be paid")
    interest_rate: float = Field(..., description="Annual interest rate (as decimal)")
    apr: float = Field(..., description="Annual Percentage Rate")


class LoanOffer(BaseModel):
    """Schema for a single loan offer from a lender"""

    lender_name: str = Field(..., description="Name of the lending institution")
    interest_rate: float = Field(..., description="Annual interest rate (as decimal)")
    monthly_payment: float = Field(..., description="Calculated monthly payment")
    total_cost: float = Field(..., description="Total cost over loan term")
    term_months: int = Field(..., description="Loan term in months")
    pre_approved: bool = Field(
        default=False, description="Whether user is pre-approved"
    )


class LoanOffersResponse(BaseModel):
    """Response schema for loan offers"""

    offers: list[LoanOffer] = Field(
        default_factory=list, description="List of loan offers"
    )
    comparison_url: str | None = Field(
        None, description="URL for detailed comparison tool"
    )


class LenderInfo(BaseModel):
    """Schema for lender information"""

    lender_id: str = Field(..., description="Unique identifier for the lender")
    name: str = Field(..., description="Lender name")
    description: str = Field(..., description="Brief description of the lender")
    logo_url: str | None = Field(None, description="URL to lender logo")

    # Loan criteria
    min_credit_score: int = Field(..., description="Minimum credit score required")
    max_credit_score: int = Field(default=850, description="Maximum credit score")
    min_loan_amount: float = Field(..., description="Minimum loan amount")
    max_loan_amount: float = Field(..., description="Maximum loan amount")
    min_term_months: int = Field(..., description="Minimum loan term in months")
    max_term_months: int = Field(..., description="Maximum loan term in months")

    # Rate information
    apr_range_min: float = Field(..., description="Minimum APR (as decimal)")
    apr_range_max: float = Field(..., description="Maximum APR (as decimal)")

    # Features and benefits
    features: list[str] = Field(default_factory=list, description="Key features")
    benefits: list[str] = Field(default_factory=list, description="Key benefits")

    # Affiliate tracking
    affiliate_url: str = Field(..., description="Affiliate tracking URL")
    referral_code: str | None = Field(None, description="Referral code for tracking")


class LenderRecommendationRequest(BaseModel):
    """Request schema for lender recommendations"""

    loan_amount: float = Field(..., gt=0, description="Desired loan amount")
    credit_score_range: str = Field(
        ..., description="Credit score range: excellent, good, fair, or poor"
    )
    loan_term_months: int = Field(..., gt=0, description="Desired loan term in months")

    @field_validator("credit_score_range")
    @classmethod
    def validate_credit_score_range(cls, v: str) -> str:
        """Validate credit score range is one of the allowed values"""
        allowed = ["excellent", "good", "fair", "poor"]
        if v.lower() not in allowed:
            raise ValueError(f"credit_score_range must be one of: {', '.join(allowed)}")
        return v.lower()


class LenderMatch(BaseModel):
    """Schema for a matched lender with recommendation details"""

    lender: LenderInfo = Field(..., description="Lender information")
    match_score: float = Field(..., ge=0, le=100, description="Match score (0-100)")
    estimated_apr: float = Field(..., description="Estimated APR for user (as decimal)")
    estimated_monthly_payment: float = Field(
        ..., description="Estimated monthly payment"
    )
    recommendation_reason: str = Field(
        ..., description="Why this lender is recommended"
    )
    rank: int = Field(..., ge=1, description="Ranking position")


class LenderRecommendationResponse(BaseModel):
    """Response schema for lender recommendations"""

    recommendations: list[LenderMatch] = Field(
        default_factory=list, description="List of recommended lenders"
    )
    total_matches: int = Field(..., description="Total number of matching lenders")
    request_summary: dict = Field(..., description="Summary of request parameters")

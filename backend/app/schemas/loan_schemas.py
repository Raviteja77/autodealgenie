"""
Pydantic schemas for loan applications
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class LoanCalculationRequest(BaseModel):
    """Request schema for loan payment calculation"""

    loan_amount: float = Field(..., gt=0, description="Total loan amount")
    down_payment: float = Field(default=0.0, ge=0, description="Down payment amount")
    loan_term_months: int = Field(..., gt=0, description="Loan term in months")
    credit_score_range: str = Field(
        ..., description="Credit score range: excellent, good, fair, or poor"
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
    pre_approved: bool = Field(default=False, description="Whether user is pre-approved")


class LoanOffersResponse(BaseModel):
    """Response schema for loan offers"""

    offers: list[LoanOffer] = Field(default_factory=list, description="List of loan offers")
    comparison_url: Optional[str] = Field(
        None, description="URL for detailed comparison tool"
    )

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


class LoanApplicationCreate(BaseModel):
    """Schema for creating a loan application"""

    # Loan details
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    down_payment: float = Field(default=0.0, ge=0, description="Down payment amount")
    trade_in_value: float = Field(default=0.0, ge=0, description="Trade-in vehicle value")
    loan_term_months: int = Field(..., gt=0, description="Desired loan term in months")
    credit_score_range: str = Field(..., description="Credit score range")

    # Applicant information
    annual_income: Optional[float] = Field(None, ge=0, description="Annual income")
    employment_status: Optional[str] = Field(None, description="Current employment status")

    # Optional fields
    deal_id: Optional[int] = Field(None, description="Associated deal ID")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        extra = "allow"  # Allow extra fields for flexibility


class LoanApplicationResponse(BaseModel):
    """Response schema for loan application"""

    id: int
    user_id: int
    deal_id: Optional[int] = None
    loan_amount: float
    down_payment: float
    trade_in_value: float
    loan_term_months: int
    interest_rate: Optional[float] = None
    monthly_payment: Optional[float] = None
    credit_score_range: str
    annual_income: Optional[float] = None
    employment_status: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        extra = "allow"


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

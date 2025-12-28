"""
Pydantic schemas for LLM request/response validation
"""

from typing import Any

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    """Schema for LLM generation requests"""

    prompt_id: str = Field(..., description="ID of the prompt template to use")
    variables: dict[str, Any] = Field(
        default_factory=dict,
        description="Variables to substitute in the prompt template",
    )
    model: str | None = Field(None, description="Override the default OpenAI model")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Sampling temperature (0-2)"
    )
    max_tokens: int | None = Field(None, gt=0, description="Maximum number of tokens to generate")


class LLMResponse(BaseModel):
    """Schema for LLM generation responses"""

    content: str | dict[str, Any] = Field(..., description="Generated content")
    prompt_id: str = Field(..., description="ID of the prompt template used")
    model: str = Field(..., description="OpenAI model used for generation")
    tokens_used: int | None = Field(None, description="Total tokens used in the request")


class LLMError(BaseModel):
    """Schema for LLM error responses"""

    error_type: str = Field(
        ..., description="Type of error (e.g., 'api_error', 'validation_error')"
    )
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")


class CarSelectionItem(BaseModel):
    """Schema for a selected car from a list"""

    index: int = Field(..., description="Index of the vehicle in the provided list")
    score: float = Field(..., ge=1.0, le=10.0, description="Confidence score (1-10)")
    highlights: list[str] = Field(..., description="Top 3 reasons to consider this vehicle")
    summary: str = Field(..., description="Brief recommendation summary")


class CarSelectionResponse(BaseModel):
    """Schema for car selection response"""

    recommendations: list[CarSelectionItem] = Field(..., description="List of selected vehicles")


class DealEvaluation(BaseModel):
    """Schema for deal evaluation response"""

    fair_value: float = Field(..., description="Estimated fair market value in USD")
    score: float = Field(..., ge=1.0, le=10.0, description="Deal quality score from 1-10")
    insights: list[str] = Field(..., description="3-5 key observations about the deal")
    talking_points: list[str] = Field(..., description="3-5 specific negotiation strategies")


class VehicleConditionAssessment(BaseModel):
    """Schema for vehicle condition assessment in multi-step pipeline"""

    condition_score: float = Field(..., ge=1.0, le=10.0, description="Condition score from 1-10")
    condition_notes: list[str] = Field(..., description="Key observations about vehicle condition")
    recommended_inspection: bool = Field(
        ..., description="Whether pre-purchase inspection is recommended"
    )


# ============================================================================
# Multi-Agent System Schemas
# These schemas support the new multi-agent prompts migrated from CrewAI
# ============================================================================


class VehicleInfo(BaseModel):
    """Information about a single vehicle"""

    vin: str = Field(..., description="Vehicle Identification Number")
    make: str = Field(..., description="Vehicle manufacturer")
    model: str = Field(..., description="Vehicle model")
    year: int = Field(..., description="Model year")
    trim: str | None = Field(None, description="Trim level")
    mileage: int = Field(..., description="Mileage in miles")
    price: float = Field(..., description="Asking price in USD")
    location: str = Field(..., description="Vehicle location")
    dealer_name: str | None = Field(None, description="Dealer name")
    dealer_contact: str | None = Field(None, description="Dealer contact information")
    pros: list[str] = Field(default_factory=list, description="Positive aspects")
    cons: list[str] = Field(default_factory=list, description="Negative aspects")
    reliability_score: float | None = Field(None, description="Reliability rating (1-10)")
    review_summary: str | None = Field(None, description="Expert review summary")


class SearchCriteria(BaseModel):
    """Vehicle search criteria"""

    make: str = Field(..., description="Vehicle manufacturer")
    model: str | None = Field(None, description="Vehicle model")
    price_min: float | None = Field(None, description="Minimum price")
    price_max: float | None = Field(None, description="Maximum price")
    condition: str | None = Field(None, description="Vehicle condition (new, used, certified)")
    year_min: int | None = Field(None, description="Minimum model year")
    year_max: int | None = Field(None, description="Maximum model year")
    mileage_max: int | None = Field(None, description="Maximum mileage")
    location: str | None = Field(None, description="Search location")


class VehicleReport(BaseModel):
    """Schema for research agent vehicle report"""

    search_criteria: SearchCriteria = Field(..., description="Search parameters used")
    top_vehicles: list[VehicleInfo] = Field(..., description="Top 3-5 recommended vehicles")


class LoanOption(BaseModel):
    """A single financing option with enhanced details"""

    lender_name: str = Field(..., description="Name of lending institution")
    lender_type: str = Field(
        ..., description="Type of lender (Credit Union, Bank, Online Lender, Dealer Financing)"
    )
    apr: float = Field(..., description="Annual Percentage Rate")
    term_months: int = Field(..., description="Loan term in months")
    monthly_payment: float = Field(..., description="Estimated monthly payment")
    total_interest: float = Field(..., description="Total interest paid over loan term")
    total_cost: float = Field(..., description="Total cost (loan_amount + total_interest)")
    features: list[str] = Field(
        default_factory=list,
        description="Lender features (e.g., 'No prepayment penalty', 'Autopay discount')",
    )
    match_score: float | None = Field(
        None, description="Match score if lender recommendation data available"
    )
    eligibility_notes: str | None = Field(None, description="Approval likelihood and requirements")
    notes: str = Field(..., description="Additional considerations, warnings, or benefits")


class AffordabilityAssessment(BaseModel):
    """Assessment of financing affordability"""

    monthly_payment: float = Field(..., description="Recommended option's monthly payment")
    monthly_income: float | None = Field(None, description="Buyer's gross monthly income if provided")
    debt_to_income_ratio: float | None = Field(
        None, description="DTI ratio as percentage if income provided"
    )
    affordability_rating: str = Field(
        ..., description="Rating: Excellent, Good, Moderate, or Concerning"
    )
    budget_fit: str = Field(
        ..., description="Within budget, Tight fit, Exceeds budget, or Budget not provided"
    )


class FinancingReport(BaseModel):
    """Enhanced schema for loan analyzer agent financing report"""

    vehicle_vin: str = Field(..., description="VIN of the vehicle being financed")
    vehicle_price: float = Field(..., description="Vehicle purchase price")
    loan_amount: float = Field(..., description="Total loan amount needed")
    down_payment: float = Field(..., description="Down payment amount")
    down_payment_ratio: float = Field(..., description="Down payment as percentage (e.g., 20 for 20%)")
    down_payment_assessment: str = Field(
        ..., description="Assessment: Excellent (≥20%), Acceptable (10-19%), or Risky (<10%)"
    )
    options: list[LoanOption] = Field(..., description="Available financing options")
    recommended_option_index: int = Field(..., description="Zero-based index of recommended option")
    recommendation_rationale: str = Field(
        ..., description="Why this option is best (200-300 words)"
    )
    affordability_assessment: AffordabilityAssessment = Field(
        ..., description="Affordability analysis"
    )
    financing_strategy: str = Field(..., description="Guidance on next steps (300-400 words)")
    red_flags: list[str] = Field(
        default_factory=list, description="Warnings about risky loan options or predatory terms"
    )
    data_source: str = Field(
        ..., description="Lender recommendation data or Educational guidance on typical market rates"
    )


class AddOnRecommendation(BaseModel):
    """Enhanced add-on with recommendation"""

    name: str = Field(..., description="Name of add-on")
    typical_price: float = Field(..., description="Typical retail price")
    dealer_cost: float | None = Field(None, description="Approximate dealer cost if known")
    recommendation: str = Field(
        ..., description="Decline, Negotiate to $X, or Accept only if..."
    )


class FeeDetail(BaseModel):
    """Enhanced fee with negotiation guidance"""

    name: str = Field(..., description="Fee name")
    typical_amount: float = Field(..., description="Typical amount")
    negotiable: bool = Field(..., description="True if junk fee, false if mandatory")
    strategy: str = Field(..., description="How to handle this fee")


class DealerFinancingOffer(BaseModel):
    """Enhanced dealer financing offer with warnings"""

    apr: float = Field(..., description="Dealer's APR offer")
    term_months: int = Field(..., description="Loan term in months")
    monthly_payment: float = Field(..., description="Monthly payment amount")
    notes: str = Field(..., description="Warnings about dealer financing tactics")


class NegotiatedDeal(BaseModel):
    """Enhanced schema for negotiation agent deal summary"""

    vehicle_vin: str = Field(..., description="VIN of negotiated vehicle")
    final_price: float = Field(..., description="Recommended target price")
    opening_offer: float = Field(..., description="Aggressive opening offer (10-15% below asking)")
    walk_away_price: float = Field(..., description="Maximum acceptable out-the-door price")
    add_ons: list[AddOnRecommendation] = Field(
        default_factory=list, description="Add-ons with recommendations"
    )
    fees: list[FeeDetail] = Field(default_factory=list, description="Fees with negotiation strategy")
    dealer_financing_offer: DealerFinancingOffer | None = Field(
        None, description="Estimated dealer financing offer with warnings"
    )
    negotiation_summary: str = Field(
        ..., description="Comprehensive 400-600 word negotiation guide"
    )


class QAIssue(BaseModel):
    """Quality assurance issue found in report"""

    severity: str = Field(..., description="Critical, Moderate, or Minor")
    category: str = Field(
        ...,
        description="Consistency, Clarity, Completeness, Math, Logic, or Buyer Advocacy",
    )
    description: str = Field(..., description="Specific problem found")
    location: str = Field(..., description="Where in report (section name or Throughout)")


class QAReport(BaseModel):
    """Enhanced schema for quality assurance agent review"""

    is_valid: bool = Field(
        ..., description="True if report passes all quality checks with no critical issues"
    )
    validation_summary: str = Field(..., description="One sentence overall assessment")
    issues: list[QAIssue] = Field(
        default_factory=list, description="List of issues found (empty if none)"
    )
    suggested_revision: str = Field(
        default="",
        description="Fully edited report with all issues corrected, or empty if no changes needed",
    )
    quality_score: float = Field(..., ge=1.0, le=10.0, description="1-10 score for report quality")
    recommendations: list[str] = Field(
        default_factory=list, description="Suggestions for improvement even if valid"
    )

"""
Loan calculation endpoints (anonymous, secure)
"""
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.models.models import User
from app.schemas.loan_schemas import (
    LenderRecommendationRequest,
    LenderRecommendationResponse,
    LoanCalculationRequest,
    LoanCalculationResponse,
    LoanOffer,
    LoanOffersResponse,
)
from app.services.lender_service import LenderService
from app.services.loan_calculator_service import (
    APR_RATES,
    CreditScoreRange,
    LoanCalculatorService,
)

router = APIRouter()

# Mock lender rate adjustments (relative to base APR for credit score)
BEST_LENDER_DISCOUNT = 0.005  # 0.5% below base rate
HIGHER_LENDER_PREMIUM = 0.01  # 1.0% above base rate


def generate_mock_loan_offers(
    loan_amount: float,
    credit_score: str,
    loan_term: int,
) -> list[LoanOffer]:
    """Generate mock loan offers based on credit score and term.

    In production this would be replaced with real lender integrations.
    Uses APR rates consistent with LoanCalculatorService for accuracy.
    """
    # Get base rate for credit score
    try:
        credit_range = CreditScoreRange(credit_score.lower())
        base_rate = APR_RATES[credit_range]
    except (ValueError, KeyError):
        base_rate = APR_RATES[CreditScoreRange.GOOD]  # Default to good credit

    def _monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
        monthly_rate = annual_rate / 12
        if monthly_rate == 0:
            return principal / term_months
        return (principal * monthly_rate * (1 + monthly_rate) ** term_months) / (
            (1 + monthly_rate) ** term_months - 1
        )

    # Generate offers from different lenders with varying rates
    lenders = [
        ("AutoBank Prime", base_rate - BEST_LENDER_DISCOUNT),
        ("CarFinance Plus", base_rate),
        ("Neighborhood Credit Union", base_rate + HIGHER_LENDER_PREMIUM),
    ]

    offers: list[LoanOffer] = []
    for name, rate in lenders:
        monthly = _monthly_payment(loan_amount, rate, loan_term)
        total_paid = monthly * loan_term
        offers.append(
            LoanOffer(
                lender_name=name,
                interest_rate=rate,
                monthly_payment=round(monthly, 2),
                total_cost=round(total_paid, 2),
                term_months=loan_term,
                pre_approved=credit_score.lower() in {"excellent", "good"},
            )
        )

    return offers


@router.post("/calculate", response_model=LoanCalculationResponse)
async def calculate_loan_payment(
    calculation: LoanCalculationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Calculate monthly payment and total cost for a loan.

    Interest rates are determined server-side based on credit score range.
    Uses the LoanCalculatorService for accurate calculations.
    """
    try:
        # Use the loan calculator service
        result = LoanCalculatorService.calculate_loan(
            loan_amount=calculation.loan_amount,
            down_payment=calculation.down_payment,
            loan_term_months=calculation.loan_term_months,
            credit_score_range=calculation.credit_score_range,
            include_amortization=False,  # Don't include full schedule in API response
        )

        # Convert to response schema
        return LoanCalculationResponse(
            monthly_payment=result.monthly_payment,
            total_interest=result.total_interest,
            total_amount=result.total_amount,
            interest_rate=result.interest_rate,
            apr=result.apr,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/offers", response_model=LoanOffersResponse)
async def get_loan_offers(
    loan_amount: float,
    credit_score: str,
    loan_term: int,
    current_user: User = Depends(get_current_user),
):
    """
    Get available loan offers from various lenders

    In production, this would integrate with actual lender APIs
    For now, returns mock data based on credit score
    """
    # Mock lender offers
    offers = generate_mock_loan_offers(loan_amount, credit_score, loan_term)

    return LoanOffersResponse(
        offers=offers,
        comparison_url=None,
    )


@router.post("/lenders", response_model=LenderRecommendationResponse)
async def get_lender_recommendations(
    request: LenderRecommendationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Get personalized lender recommendations based on loan criteria.

    This endpoint provides:
    - Curated list of partner lenders that match user criteria
    - Match scores indicating how well each lender fits user needs
    - Estimated APR and monthly payments for each lender
    - Recommendation reasons explaining why each lender is suggested
    - Affiliate tracking URLs for commission attribution (no PII collected)

    The ranking algorithm considers:
    - APR competitiveness (40% weight)
    - Loan amount fit (20% weight)
    - Credit score fit (20% weight)
    - Term flexibility (10% weight)
    - Features and benefits (10% weight)

    Returns up to 5 top recommendations sorted by match score.
    """
    try:
        recommendations = LenderService.get_recommendations(request, max_results=5)
        return recommendations
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

"""
Loan application endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.repositories.loan_repository import LoanRepository
from app.schemas.loan_schemas import (
    LoanApplicationCreate,
    LoanApplicationResponse,
    LoanCalculationRequest,
    LoanCalculationResponse,
    LoanOffer,
    LoanOffersResponse,
)

router = APIRouter()


def generate_mock_loan_offers(
    loan_amount: float,
    credit_score: str,
    loan_term: int,
) -> list[LoanOffer]:
    """Generate mock loan offers based on credit score and term.

    In production this would be replaced with real lender integrations.
    """
    base_rates = {
        "excellent": 0.035,
        "good": 0.045,
        "fair": 0.065,
        "poor": 0.095,
    }
    base_rate = base_rates.get(credit_score.lower(), 0.055)

    def _monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
        monthly_rate = annual_rate / 12
        if monthly_rate == 0:
            return principal / term_months
        return (
            principal * monthly_rate * (1 + monthly_rate) ** term_months
        ) / ((1 + monthly_rate) ** term_months - 1)

    lenders = [
        ("AutoBank Prime", base_rate),
        ("CarFinance Plus", base_rate + 0.005),
        ("Neighborhood Credit Union", base_rate + 0.01),
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
    """
    # Interest rates based on credit score (server-side for security)
    interest_rates = {
        "excellent": 0.039,  # 3.9%
        "good": 0.059,  # 5.9%
        "fair": 0.089,  # 8.9%
        "poor": 0.129,  # 12.9%
    }
    
    rate = interest_rates.get(calculation.credit_score_range, 0.059)
    principal = calculation.loan_amount - calculation.down_payment
    
    # Validate term to prevent division by zero
    if calculation.loan_term_months <= 0:
        raise ValueError("Loan term must be greater than 0")
    
    monthly_rate = rate / 12
    
    # Handle edge case where monthly_rate is 0 (unlikely but safe)
    if monthly_rate == 0:
        monthly_payment = principal / calculation.loan_term_months
    else:
        # Calculate monthly payment using loan formula
        monthly_payment = (
            principal * monthly_rate * (1 + monthly_rate) ** calculation.loan_term_months
        ) / ((1 + monthly_rate) ** calculation.loan_term_months - 1)
    
    total_paid = monthly_payment * calculation.loan_term_months
    total_interest = total_paid - principal
    
    return LoanCalculationResponse(
        monthly_payment=round(monthly_payment, 2),
        total_interest=round(total_interest, 2),
        total_amount=round(total_paid + calculation.down_payment, 2),
        interest_rate=rate,
        apr=rate,  # Simplified, actual APR may include fees
    )

@router.post("/applications", response_model=LoanApplicationResponse)
async def create_loan_application(
    application: LoanApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new loan application
    """
    repo = LoanRepository(db)
    loan_app = repo.create(user_id=current_user.id, application_data=application)
    return loan_app

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
"""
Loan application endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.models import User, LoanApplication
from app.repositories.loan_repository import LoanRepository
from app.schemas.loan_schemas import (
    LoanApplicationCreate,
    LoanApplicationResponse,
    LoanCalculationRequest,
    LoanCalculationResponse,
    LoanOffersResponse,
)

router = APIRouter()

@router.post("/calculate", response_model=LoanCalculationResponse)
def calculate_loan_payment(
    calculation: LoanCalculationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Calculate monthly payment and total cost for a loan
    """
    # Interest rates based on credit score
    interest_rates = {
        "excellent": 0.039,
        "good": 0.059,
        "fair": 0.089,
        "poor": 0.129,
    }
    
    rate = interest_rates.get(calculation.credit_score_range, 0.059)
    principal = calculation.loan_amount - calculation.down_payment
    monthly_rate = rate / 12
    
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
def create_loan_application(
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
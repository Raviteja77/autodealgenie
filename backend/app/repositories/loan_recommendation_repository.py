"""
Repository for loan recommendation operations (PostgreSQL)
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models.ai_response import LoanRecommendation

logger = logging.getLogger(__name__)


class LoanRecommendationRepository:
    """Repository for managing loan recommendations in PostgreSQL"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        deal_id: int,
        user_id: int,
        loan_amount: float,
        down_payment: float,
        loan_term_months: int,
        credit_score_range: str,
        monthly_payment: float,
        apr: float,
        total_interest: float,
        total_amount: float,
        additional_data: dict[str, Any] | None = None,
    ) -> LoanRecommendation:
        """
        Create a loan recommendation record

        Args:
            deal_id: Deal ID
            user_id: User ID
            loan_amount: Loan amount
            down_payment: Down payment amount
            loan_term_months: Loan term in months
            credit_score_range: Credit score range
            monthly_payment: Monthly payment
            apr: APR
            total_interest: Total interest
            total_amount: Total amount to be paid
            additional_data: Additional data (amortization schedule, etc.)

        Returns:
            Created LoanRecommendation
        """
        loan_rec = LoanRecommendation(
            deal_id=deal_id,
            user_id=user_id,
            loan_amount=loan_amount,
            down_payment=down_payment,
            loan_term_months=loan_term_months,
            credit_score_range=credit_score_range,
            monthly_payment=monthly_payment,
            apr=apr,
            total_interest=total_interest,
            total_amount=total_amount,
            additional_data=additional_data,
        )
        self.db.add(loan_rec)
        self.db.commit()
        self.db.refresh(loan_rec)
        logger.info(
            f"Created loan recommendation {loan_rec.id} for deal {deal_id}, "
            f"term {loan_term_months}mo, APR {apr}%"
        )
        return loan_rec

    def get_by_deal_id(self, deal_id: int) -> list[LoanRecommendation]:
        """
        Get all loan recommendations for a deal

        Args:
            deal_id: Deal ID

        Returns:
            List of loan recommendations
        """
        return (
            self.db.query(LoanRecommendation)
            .filter(LoanRecommendation.deal_id == deal_id)
            .order_by(LoanRecommendation.created_at.desc())
            .all()
        )

    def get_by_user_id(self, user_id: int, limit: int = 50) -> list[LoanRecommendation]:
        """
        Get loan recommendations for a user

        Args:
            user_id: User ID
            limit: Maximum number of records to return

        Returns:
            List of loan recommendations
        """
        return (
            self.db.query(LoanRecommendation)
            .filter(LoanRecommendation.user_id == user_id)
            .order_by(LoanRecommendation.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_id(self, loan_rec_id: int) -> LoanRecommendation | None:
        """
        Get a loan recommendation by ID

        Args:
            loan_rec_id: Loan recommendation ID

        Returns:
            LoanRecommendation or None
        """
        return (
            self.db.query(LoanRecommendation).filter(LoanRecommendation.id == loan_rec_id).first()
        )

    def delete(self, loan_rec_id: int) -> bool:
        """
        Delete a loan recommendation

        Args:
            loan_rec_id: Loan recommendation ID

        Returns:
            True if deleted, False if not found
        """
        loan_rec = self.get_by_id(loan_rec_id)
        if loan_rec:
            self.db.delete(loan_rec)
            self.db.commit()
            logger.info(f"Deleted loan recommendation {loan_rec_id}")
            return True
        return False

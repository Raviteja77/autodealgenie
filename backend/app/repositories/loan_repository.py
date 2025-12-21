"""
Repository for loan application data access
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import LoanApplication, LoanStatus
from app.schemas.loan_schemas import LoanApplicationCreate


class LoanRepository:
    """Repository for managing loan applications"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self, user_id: int, application_data: LoanApplicationCreate
    ) -> LoanApplication:
        """Create a new loan application"""
        loan_app = LoanApplication(
            user_id=user_id,
            deal_id=application_data.deal_id,
            loan_amount=application_data.loan_amount,
            down_payment=application_data.down_payment,
            trade_in_value=application_data.trade_in_value,
            loan_term_months=application_data.loan_term_months,
            credit_score_range=application_data.credit_score_range,
            annual_income=application_data.annual_income,
            employment_status=application_data.employment_status,
            status=LoanStatus.DRAFT,
        )

        self.db.add(loan_app)
        self.db.commit()
        self.db.refresh(loan_app)
        return loan_app

    def get_by_id(self, loan_id: int) -> Optional[LoanApplication]:
        """Get a loan application by ID"""
        stmt = select(LoanApplication).where(LoanApplication.id == loan_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_user_id(self, user_id: int) -> list[LoanApplication]:
        """Get all loan applications for a user"""
        stmt = (
            select(LoanApplication)
            .where(LoanApplication.user_id == user_id)
            .order_by(LoanApplication.created_at.desc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_by_deal_id(self, deal_id: int) -> Optional[LoanApplication]:
        """Get loan application associated with a deal"""
        stmt = select(LoanApplication).where(LoanApplication.deal_id == deal_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def update(
        self, loan_id: int, **kwargs
    ) -> Optional[LoanApplication]:
        """Update a loan application"""
        loan_app = self.get_by_id(loan_id)
        if not loan_app:
            return None

        for key, value in kwargs.items():
            if hasattr(loan_app, key):
                setattr(loan_app, key, value)

        self.db.commit()
        self.db.refresh(loan_app)
        return loan_app

    def update_status(
        self, loan_id: int, status: LoanStatus
    ) -> Optional[LoanApplication]:
        """Update loan application status"""
        return self.update(loan_id, status=status)

    def delete(self, loan_id: int) -> bool:
        """Delete a loan application"""
        loan_app = self.get_by_id(loan_id)
        if not loan_app:
            return False

        self.db.delete(loan_app)
        self.db.commit()
        return True

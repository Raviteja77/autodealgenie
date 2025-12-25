"""
SQLAlchemy models for AI-generated responses (PostgreSQL)
Stores loan and insurance recommendations
"""

import enum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.sql import func

from app.db.session import Base


class AIResponseType(str, enum.Enum):
    """AI response type enumeration"""

    LOAN_RECOMMENDATION = "loan_recommendation"
    INSURANCE_RECOMMENDATION = "insurance_recommendation"


class LoanRecommendation(Base):
    """
    Loan recommendation model - stores calculated loan options
    Links to Deal for traceability
    """

    __tablename__ = "loan_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Loan details
    loan_amount = Column(Float, nullable=False)
    down_payment = Column(Float, nullable=False)
    loan_term_months = Column(Integer, nullable=False)
    credit_score_range = Column(String(50), nullable=False)
    
    # Calculated values
    monthly_payment = Column(Float, nullable=False)
    apr = Column(Float, nullable=False)
    total_interest = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Additional data (amortization schedule, etc.)
    additional_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<LoanRecommendation {self.id}: Deal {self.deal_id}, Term {self.loan_term_months}mo>"


class InsuranceRecommendation(Base):
    """
    Insurance recommendation model - stores insurance quotes and provider matches
    Links to Deal for traceability
    """

    __tablename__ = "insurance_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Vehicle and driver info
    vehicle_value = Column(Float, nullable=False)
    vehicle_age = Column(Integer, nullable=False)
    coverage_type = Column(String(50), nullable=False)
    driver_age = Column(Integer, nullable=False)
    
    # Provider info
    provider_id = Column(String(100), nullable=False)
    provider_name = Column(String(255), nullable=False)
    
    # Recommendation details
    match_score = Column(Float, nullable=False)
    estimated_monthly_premium = Column(Float, nullable=False)
    estimated_annual_premium = Column(Float, nullable=False)
    recommendation_reason = Column(String(512), nullable=True)
    rank = Column(Integer, nullable=False)
    
    # Full recommendation data (features, benefits, etc.)
    full_recommendation_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<InsuranceRecommendation {self.id}: Deal {self.deal_id}, Provider {self.provider_name}>"

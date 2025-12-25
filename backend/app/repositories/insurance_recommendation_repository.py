"""
Repository for insurance recommendation operations (PostgreSQL)
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models.ai_response import InsuranceRecommendation

logger = logging.getLogger(__name__)


class InsuranceRecommendationRepository:
    """Repository for managing insurance recommendations in PostgreSQL"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        deal_id: int,
        user_id: int,
        vehicle_value: float,
        vehicle_age: int,
        coverage_type: str,
        driver_age: int,
        provider_id: str,
        provider_name: str,
        match_score: float,
        estimated_monthly_premium: float,
        estimated_annual_premium: float,
        recommendation_reason: str | None,
        rank: int,
        full_recommendation_data: dict[str, Any] | None = None,
    ) -> InsuranceRecommendation:
        """
        Create an insurance recommendation record

        Args:
            deal_id: Deal ID
            user_id: User ID
            vehicle_value: Vehicle value
            vehicle_age: Vehicle age
            coverage_type: Coverage type
            driver_age: Driver age
            provider_id: Provider ID
            provider_name: Provider name
            match_score: Match score
            estimated_monthly_premium: Estimated monthly premium
            estimated_annual_premium: Estimated annual premium
            recommendation_reason: Recommendation reason
            rank: Rank
            full_recommendation_data: Full recommendation data

        Returns:
            Created InsuranceRecommendation
        """
        insurance_recommendation = InsuranceRecommendation(
            deal_id=deal_id,
            user_id=user_id,
            vehicle_value=vehicle_value,
            vehicle_age=vehicle_age,
            coverage_type=coverage_type,
            driver_age=driver_age,
            provider_id=provider_id,
            provider_name=provider_name,
            match_score=match_score,
            estimated_monthly_premium=estimated_monthly_premium,
            estimated_annual_premium=estimated_annual_premium,
            recommendation_reason=recommendation_reason,
            rank=rank,
            full_recommendation_data=full_recommendation_data,
        )
        self.db.add(insurance_recommendation)
        self.db.commit()
        self.db.refresh(insurance_recommendation)
        logger.info(
            f"Created insurance recommendation {insurance_recommendation.id} for deal {deal_id}, "
            f"provider {provider_name}, rank {rank}"
        )
        return insurance_recommendation

    def get_by_deal_id(self, deal_id: int) -> list[InsuranceRecommendation]:
        """
        Get all insurance recommendations for a deal

        Args:
            deal_id: Deal ID

        Returns:
            List of insurance recommendations, ordered by rank
        """
        return (
            self.db.query(InsuranceRecommendation)
            .filter(InsuranceRecommendation.deal_id == deal_id)
            .order_by(InsuranceRecommendation.rank)
            .all()
        )

    def get_by_user_id(self, user_id: int, limit: int = 50) -> list[InsuranceRecommendation]:
        """
        Get insurance recommendations for a user

        Args:
            user_id: User ID
            limit: Maximum number of records to return

        Returns:
            List of insurance recommendations
        """
        return (
            self.db.query(InsuranceRecommendation)
            .filter(InsuranceRecommendation.user_id == user_id)
            .order_by(InsuranceRecommendation.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_id(
        self, insurance_recommendation_id: int
    ) -> InsuranceRecommendation | None:
        """
        Get an insurance recommendation by ID

        Args:
            insurance_recommendation_id: Insurance recommendation ID

        Returns:
            InsuranceRecommendation or None
        """
        return (
            self.db.query(InsuranceRecommendation)
            .filter(InsuranceRecommendation.id == insurance_recommendation_id)
            .first()
        )

    def delete(self, insurance_recommendation_id: int) -> bool:
        """
        Delete an insurance recommendation

        Args:
            insurance_recommendation_id: Insurance recommendation ID

        Returns:
            True if deleted, False if not found
        """
        insurance_recommendation = self.get_by_id(insurance_recommendation_id)
        if insurance_recommendation:
            self.db.delete(insurance_recommendation)
            self.db.commit()
            logger.info(f"Deleted insurance recommendation {insurance_recommendation_id}")
            return True
        return False

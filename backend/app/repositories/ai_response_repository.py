"""
Repository for AI response logging in PostgreSQL
Stores comprehensive AI interactions across all features for analytics and traceability
Previously used MongoDB, now using PostgreSQL JSONB
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.jsonb_data import AIResponse

logger = logging.getLogger(__name__)


class AIResponseRepository:
    """Repository for managing AI responses in PostgreSQL"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_response(
        self,
        feature: str,
        user_id: int | None,
        deal_id: int | None,
        prompt_id: str,
        prompt_variables: dict[str, Any],
        response_content: str | dict[str, Any],
        response_metadata: dict[str, Any] | None = None,
        model_used: str | None = None,
        tokens_used: int | None = None,
        temperature: float | None = None,
        llm_used: bool = True,
    ) -> AIResponse:
        """
        Create an AI response record

        Args:
            feature: Feature name (negotiation, evaluation, recommendation, loan, insurance)
            user_id: User ID (None for anonymous)
            deal_id: Deal ID (None if not associated with a deal)
            prompt_id: Prompt template ID used
            prompt_variables: Variables substituted in prompt
            response_content: AI-generated response content
            response_metadata: Additional metadata (scores, suggestions, etc.)
            model_used: OpenAI model used
            tokens_used: Tokens used
            temperature: Temperature used
            llm_used: Whether LLM was actually used (False for fallback)

        Returns:
            AIResponse: Created record
        """
        # Convert string response to dict if needed
        if isinstance(response_content, str):
            response_content = {"text": response_content}

        # Store temperature as integer (multiplied by 100) for database storage
        temperature_int = int(temperature * 100) if temperature is not None else None

        record = AIResponse(
            feature=feature,
            user_id=user_id,
            deal_id=deal_id,
            prompt_id=prompt_id,
            prompt_variables=prompt_variables,
            response_content=response_content,
            response_metadata=response_metadata or {},
            model_used=model_used,
            tokens_used=tokens_used,
            temperature=temperature_int,
            llm_used=1 if llm_used else 0,
        )

        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)

        logger.info(
            f"Logged AI response for feature={feature}, "
            f"deal_id={deal_id}, prompt_id={prompt_id}, llm_used={llm_used}"
        )
        return record

    async def get_by_deal_id(
        self, deal_id: int, limit: int = 100, skip: int = 0
    ) -> list[AIResponse]:
        """
        Get all AI responses for a deal

        Args:
            deal_id: Deal ID
            limit: Maximum number of records to return
            skip: Number of records to skip (for pagination)

        Returns:
            List of AI response records
        """
        # Validate deal_id
        if not isinstance(deal_id, int) or deal_id <= 0:
            raise ValueError(f"Invalid deal_id: {deal_id}")

        result = await self.db.execute(
            select(AIResponse)
            .filter(AIResponse.deal_id == deal_id)
            .order_by(desc(AIResponse.timestamp))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_user_id(
        self, user_id: int, limit: int = 100, skip: int = 0
    ) -> list[AIResponse]:
        """
        Get all AI responses for a user

        Args:
            user_id: User ID
            limit: Maximum number of records to return
            skip: Number of records to skip (for pagination)

        Returns:
            List of AI response records
        """
        # Validate user_id
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError(f"Invalid user_id: {user_id}")

        result = await self.db.execute(
            select(AIResponse)
            .filter(AIResponse.user_id == user_id)
            .order_by(desc(AIResponse.timestamp))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_feature(
        self,
        feature: str,
        user_id: int | None = None,
        limit: int = 100,
        skip: int = 0,
    ) -> list[AIResponse]:
        """
        Get AI responses for a specific feature

        Args:
            feature: Feature name
            user_id: Optional user ID filter
            limit: Maximum number of records to return
            skip: Number of records to skip (for pagination)

        Returns:
            List of AI response records
        """
        # Validate feature name
        ALLOWED_FEATURES = {
            "negotiation",
            "deal_evaluation",
            "car_recommendation",
            "loan",
            "insurance",
        }
        if feature not in ALLOWED_FEATURES:
            raise ValueError(f"Invalid feature: {feature}. Must be one of {ALLOWED_FEATURES}")

        query = select(AIResponse).filter(AIResponse.feature == feature)

        if user_id is not None:
            if not isinstance(user_id, int) or user_id <= 0:
                raise ValueError(f"Invalid user_id: {user_id}")
            query = query.filter(AIResponse.user_id == user_id)

        query = query.order_by(desc(AIResponse.timestamp)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_deal_lifecycle(self, deal_id: int) -> dict[str, Any]:
        """
        Get comprehensive lifecycle of AI interactions for a deal

        Args:
            deal_id: Deal ID

        Returns:
            Dictionary with all AI responses grouped by feature
        """
        # Get all responses for the deal
        result = await self.db.execute(
            select(AIResponse).filter(AIResponse.deal_id == deal_id).order_by(AIResponse.timestamp)
        )
        responses = result.scalars().all()

        # Group by feature
        lifecycle = {"deal_id": deal_id, "features": {}}

        for response in responses:
            feature = response.feature
            if feature not in lifecycle["features"]:
                lifecycle["features"][feature] = {"count": 0, "responses": []}

            lifecycle["features"][feature]["count"] += 1
            lifecycle["features"][feature]["responses"].append(
                {
                    "prompt_id": response.prompt_id,
                    "response_content": response.response_content,
                    "response_metadata": response.response_metadata,
                    "timestamp": response.timestamp.isoformat(),
                    "llm_used": bool(response.llm_used),
                }
            )

        return lifecycle

    async def get_analytics(self, days: int = 30) -> dict[str, Any]:
        """
        Get analytics about AI usage

        Args:
            days: Number of days to look back

        Returns:
            Analytics data
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        print("DEBUG: Cutoff date:", cutoff_date)
        # Aggregate by feature
        result = await self.db.execute(
            select(
                AIResponse.feature,
                func.count(AIResponse.id).label("count"),
                func.sum(case((AIResponse.llm_used == 1, 1), else_=0)).label("llm_count"),
                func.sum(case((AIResponse.llm_used == 0, 1), else_=0)).label("fallback_count"),
                func.sum(AIResponse.tokens_used).label("total_tokens"),
            )
            .filter(AIResponse.timestamp >= cutoff_date)
            .group_by(AIResponse.feature)
        )
        results = result.all()
        print("DEBUG:", results)

        analytics = {"period_days": days, "features": {}}
        for row in results:
            analytics["features"][row.feature] = {
                "total_calls": row.count,
                "llm_calls": row.llm_count or 0,
                "fallback_calls": row.fallback_count or 0,
                "total_tokens": row.total_tokens or 0,
            }
        print("DEBUG:", analytics)
        return analytics

    async def delete_by_deal_id(self, deal_id: int) -> int:
        """
        Delete all AI responses for a deal

        Args:
            deal_id: Deal ID

        Returns:
            Number of records deleted
        """
        result = await self.db.execute(select(AIResponse).filter(AIResponse.deal_id == deal_id))
        responses_to_delete = result.scalars().all()
        for response in responses_to_delete:
            await self.db.delete(response)
        await self.db.commit()
        count = len(responses_to_delete)
        logger.info(f"Deleted {count} AI responses for deal {deal_id}")
        return count


# Factory function to create repository with db session
def get_ai_response_repository(db: AsyncSession) -> AIResponseRepository:
    """Factory function to create repository with db session"""
    return AIResponseRepository(db)

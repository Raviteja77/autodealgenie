"""
Repository for AI response logging in MongoDB
Stores comprehensive AI interactions across all features for analytics and traceability
"""

import logging
from datetime import datetime
from typing import Any

from app.db.mongodb import mongodb

logger = logging.getLogger(__name__)


class AIResponseRepository:
    """Repository for managing AI responses in MongoDB"""

    COLLECTION_NAME = "ai_responses"

    def __init__(self):
        """Initialize repository"""
        pass

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
    ) -> str:
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
            str: Inserted document ID
        """
        collection = mongodb.get_collection(self.COLLECTION_NAME)

        document = {
            "feature": feature,
            "user_id": user_id,
            "deal_id": deal_id,
            "prompt_id": prompt_id,
            "prompt_variables": prompt_variables,
            "response_content": response_content,
            "response_metadata": response_metadata or {},
            "model_used": model_used,
            "tokens_used": tokens_used,
            "temperature": temperature,
            "llm_used": llm_used,
            "timestamp": datetime.utcnow(),
        }

        result = await collection.insert_one(document)
        logger.info(
            f"Logged AI response for feature={feature}, "
            f"deal_id={deal_id}, prompt_id={prompt_id}, llm_used={llm_used}"
        )
        return str(result.inserted_id)

    async def get_by_deal_id(
        self, deal_id: int, limit: int = 100, skip: int = 0
    ) -> list[dict[str, Any]]:
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

        collection = mongodb.get_collection(self.COLLECTION_NAME)

        cursor = (
            collection.find({"deal_id": deal_id})
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )

        records = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            records.append(doc)

        return records

    async def get_by_user_id(
        self, user_id: int, limit: int = 100, skip: int = 0
    ) -> list[dict[str, Any]]:
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

        collection = mongodb.get_collection(self.COLLECTION_NAME)

        cursor = (
            collection.find({"user_id": user_id})
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )

        records = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            records.append(doc)

        return records

    async def get_by_feature(
        self,
        feature: str,
        user_id: int | None = None,
        limit: int = 100,
        skip: int = 0,
    ) -> list[dict[str, Any]]:
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
            raise ValueError(
                f"Invalid feature: {feature}. Must be one of {ALLOWED_FEATURES}"
            )

        collection = mongodb.get_collection(self.COLLECTION_NAME)

        query = {"feature": feature}
        if user_id is not None:
            if not isinstance(user_id, int) or user_id <= 0:
                raise ValueError(f"Invalid user_id: {user_id}")
            query["user_id"] = user_id

        cursor = collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)

        records = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            records.append(doc)

        return records

    async def get_deal_lifecycle(self, deal_id: int) -> dict[str, Any]:
        """
        Get comprehensive lifecycle of AI interactions for a deal

        Args:
            deal_id: Deal ID

        Returns:
            Dictionary with all AI responses grouped by feature
        """
        collection = mongodb.get_collection(self.COLLECTION_NAME)

        # Aggregate AI responses by feature
        pipeline = [
            {"$match": {"deal_id": deal_id}},
            {"$sort": {"timestamp": 1}},
            {
                "$group": {
                    "_id": "$feature",
                    "responses": {
                        "$push": {
                            "prompt_id": "$prompt_id",
                            "response_content": "$response_content",
                            "response_metadata": "$response_metadata",
                            "timestamp": "$timestamp",
                            "llm_used": "$llm_used",
                        }
                    },
                    "count": {"$sum": 1},
                }
            },
        ]

        lifecycle = {"deal_id": deal_id, "features": {}}
        async for doc in collection.aggregate(pipeline):
            feature = doc["_id"]
            lifecycle["features"][feature] = {
                "count": doc["count"],
                "responses": doc["responses"],
            }

        return lifecycle

    async def get_analytics(self, days: int = 30) -> dict[str, Any]:
        """
        Get analytics about AI usage

        Args:
            days: Number of days to look back

        Returns:
            Analytics data
        """
        from datetime import timedelta

        collection = mongodb.get_collection(self.COLLECTION_NAME)

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}}},
            {
                "$group": {
                    "_id": "$feature",
                    "count": {"$sum": 1},
                    "llm_count": {
                        "$sum": {"$cond": [{"$eq": ["$llm_used", True]}, 1, 0]}
                    },
                    "fallback_count": {
                        "$sum": {"$cond": [{"$eq": ["$llm_used", False]}, 1, 0]}
                    },
                    "total_tokens": {"$sum": "$tokens_used"},
                }
            },
        ]

        analytics = {"period_days": days, "features": {}}
        async for doc in collection.aggregate(pipeline):
            feature = doc["_id"]
            analytics["features"][feature] = {
                "total_calls": doc["count"],
                "llm_calls": doc["llm_count"],
                "fallback_calls": doc["fallback_count"],
                "total_tokens": doc["total_tokens"] or 0,
            }

        return analytics

    async def delete_by_deal_id(self, deal_id: int) -> int:
        """
        Delete all AI responses for a deal

        Args:
            deal_id: Deal ID

        Returns:
            Number of records deleted
        """
        collection = mongodb.get_collection(self.COLLECTION_NAME)
        result = await collection.delete_many({"deal_id": deal_id})
        logger.info(f"Deleted {result.deleted_count} AI responses for deal {deal_id}")
        return result.deleted_count


# Singleton instance
ai_response_repository = AIResponseRepository()

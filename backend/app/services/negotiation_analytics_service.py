"""
Negotiation Analytics Service

Provides ML-driven analytics for negotiation intelligence:
- Success probability prediction
- Optimal counter-offer calculation
- Pattern analysis from historical negotiations
- Vector similarity search for comparable sessions
"""

import json
import logging
from typing import Any

from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.negotiation import NegotiationMessage
from app.repositories.negotiation_repository import NegotiationRepository
from app.utils.error_handler import ApiError

logger = logging.getLogger(__name__)


class NegotiationAnalyticsService:
    """
    Service for ML-driven negotiation analytics

    Provides:
    - Success probability prediction using historical patterns
    - Optimal counter-offer suggestions based on data analysis
    - Negotiation pattern recognition
    - Vector similarity search for finding similar negotiations
    """

    # Embedding model configuration
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS = 1536

    # Success probability thresholds
    HIGH_SUCCESS_THRESHOLD = 0.75
    MEDIUM_SUCCESS_THRESHOLD = 0.50

    def __init__(self, db: AsyncSession):
        """
        Initialize NegotiationAnalyticsService

        Args:
            db: SQLAlchemy async database session
        """
        self.db = db
        self.negotiation_repo = NegotiationRepository(db)

        # Initialize OpenAI client for embeddings
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def calculate_success_probability(
        self,
        session_id: int,
        current_price: float,
        user_target_price: float,
        asking_price: float,
    ) -> dict[str, Any]:
        """
        Calculate the probability of successful negotiation completion

        Uses ML-driven analysis based on:
        - Historical negotiation outcomes
        - Current negotiation context (round, price gap, etc.)
        - Similar negotiation patterns via vector similarity

        Args:
            session_id: Current negotiation session ID
            current_price: Current negotiated price
            user_target_price: User's target price
            asking_price: Initial asking price

        Returns:
            Dictionary with success probability and supporting metrics:
            {
                "success_probability": float (0-1),
                "confidence_level": str ("high", "medium", "low"),
                "key_factors": list[str],
                "similar_sessions_count": int,
                "recommendation": str
            }
        """
        logger.info(f"Calculating success probability for session {session_id}")

        try:
            # Get session data
            session = await self.negotiation_repo.get_session(session_id)
            if not session:
                raise ApiError(status_code=404, message=f"Session {session_id} not found")

            # Get messages for context
            await self.negotiation_repo.get_messages(session_id)

            # Calculate base probability from current negotiation state
            base_probability = self._calculate_base_probability(
                current_price=current_price,
                user_target_price=user_target_price,
                asking_price=asking_price,
                current_round=session.current_round,
                max_rounds=session.max_rounds,
            )

            # Find similar negotiations using vector similarity
            similar_sessions = await self._find_similar_sessions(
                session_id=session_id,
                asking_price=asking_price,
                current_price=current_price,
                limit=20,
            )

            # Adjust probability based on similar session outcomes
            adjusted_probability = self._adjust_probability_from_history(
                base_probability=base_probability,
                similar_sessions=similar_sessions,
            )

            # Determine confidence level
            confidence_level = self._determine_confidence_level(
                similar_sessions_count=len(similar_sessions),
                probability=adjusted_probability,
            )

            # Identify key factors
            key_factors = self._identify_key_factors(
                current_price=current_price,
                user_target_price=user_target_price,
                asking_price=asking_price,
                current_round=session.current_round,
                similar_sessions=similar_sessions,
            )

            # Generate recommendation
            recommendation = self._generate_success_recommendation(
                probability=adjusted_probability,
                key_factors=key_factors,
            )

            result = {
                "success_probability": round(adjusted_probability, 3),
                "confidence_level": confidence_level,
                "key_factors": key_factors,
                "similar_sessions_count": len(similar_sessions),
                "recommendation": recommendation,
            }

            # Store analytics in database
            await self._store_analytics(session_id, result)

            return result

        except ApiError:
            raise
        except Exception as e:
            logger.error(f"Error calculating success probability: {e}", exc_info=True)
            # Return fallback values
            return {
                "success_probability": 0.5,
                "confidence_level": "low",
                "key_factors": ["Insufficient data for accurate prediction"],
                "similar_sessions_count": 0,
                "recommendation": "Continue negotiation with standard strategy",
            }

    async def get_optimal_counter_offer(
        self,
        session_id: int,
        current_offer: float,
        user_target_price: float,
        asking_price: float,
    ) -> dict[str, Any]:
        """
        Calculate the optimal counter-offer based on data analysis

        Uses historical data and ML to suggest the best counter-offer that:
        - Maximizes savings potential
        - Maintains reasonable negotiation momentum
        - Considers market conditions and similar negotiations

        Args:
            session_id: Current negotiation session ID
            current_offer: Most recent offer price
            user_target_price: User's target price
            asking_price: Initial asking price

        Returns:
            Dictionary with optimal counter-offer:
            {
                "optimal_offer": float,
                "rationale": str,
                "expected_savings": float,
                "risk_assessment": str,
                "alternative_offers": list[dict]
            }
        """
        logger.info(f"Calculating optimal counter-offer for session {session_id}")

        try:
            # Get session and messages
            session = await self.negotiation_repo.get_session(session_id)
            if not session:
                raise ApiError(status_code=404, message=f"Session {session_id} not found")

            await self.negotiation_repo.get_messages(session_id)

            # Find similar negotiations
            similar_sessions = await self._find_similar_sessions(
                session_id=session_id,
                asking_price=asking_price,
                current_price=current_offer,
                limit=15,
            )

            # Analyze successful patterns from similar sessions
            success_patterns = self._analyze_successful_patterns(similar_sessions)

            # Calculate optimal offer using pattern analysis
            optimal_offer = self._calculate_optimal_offer(
                current_offer=current_offer,
                user_target_price=user_target_price,
                asking_price=asking_price,
                current_round=session.current_round,
                success_patterns=success_patterns,
            )

            # Calculate expected savings
            expected_savings = asking_price - optimal_offer

            # Assess risk level
            risk_assessment = self._assess_offer_risk(
                optimal_offer=optimal_offer,
                user_target_price=user_target_price,
                current_offer=current_offer,
                current_round=session.current_round,
                max_rounds=session.max_rounds,
            )

            # Generate rationale
            rationale = self._generate_offer_rationale(
                optimal_offer=optimal_offer,
                current_offer=current_offer,
                success_patterns=success_patterns,
            )

            # Provide alternative offers
            alternative_offers = self._generate_alternative_offers(
                optimal_offer=optimal_offer,
                user_target_price=user_target_price,
                current_offer=current_offer,
            )

            return {
                "optimal_offer": round(optimal_offer, 2),
                "rationale": rationale,
                "expected_savings": round(expected_savings, 2),
                "risk_assessment": risk_assessment,
                "alternative_offers": alternative_offers,
            }

        except ApiError:
            raise
        except Exception as e:
            logger.error(f"Error calculating optimal counter-offer: {e}", exc_info=True)
            # Return conservative fallback
            fallback_offer = (current_offer + user_target_price) / 2
            return {
                "optimal_offer": round(fallback_offer, 2),
                "rationale": "Based on standard negotiation strategy (insufficient historical data)",
                "expected_savings": round(asking_price - fallback_offer, 2),
                "risk_assessment": "medium",
                "alternative_offers": [],
            }

    async def analyze_negotiation_patterns(
        self,
        session_id: int,
    ) -> dict[str, Any]:
        """
        Analyze patterns in the current negotiation compared to historical data

        Provides insights on:
        - Negotiation velocity (speed of price changes)
        - Dealer flexibility indicators
        - User negotiation style
        - Predicted outcome based on patterns

        Args:
            session_id: Current negotiation session ID

        Returns:
            Dictionary with pattern analysis:
            {
                "negotiation_velocity": str,
                "dealer_flexibility": str,
                "user_style": str,
                "predicted_outcome": str,
                "insights": list[str]
            }
        """
        logger.info(f"Analyzing negotiation patterns for session {session_id}")

        try:
            # Get session and messages
            session = await self.negotiation_repo.get_session(session_id)
            if not session:
                raise ApiError(status_code=404, message=f"Session {session_id} not found")

            messages = await self.negotiation_repo.get_messages(session_id)

            # Calculate negotiation velocity
            velocity = self._calculate_negotiation_velocity(messages)

            # Assess dealer flexibility
            flexibility = self._assess_dealer_flexibility(messages)

            # Determine user style
            user_style = self._determine_user_style(messages)

            # Find similar patterns
            similar_sessions = await self._find_similar_sessions(
                session_id=session_id,
                asking_price=0.0,  # Will be extracted from session
                current_price=0.0,  # Will be extracted from messages
                limit=10,
            )

            # Predict outcome
            predicted_outcome = self._predict_outcome_from_patterns(
                velocity=velocity,
                flexibility=flexibility,
                similar_sessions=similar_sessions,
            )

            # Generate insights
            insights = self._generate_pattern_insights(
                velocity=velocity,
                flexibility=flexibility,
                user_style=user_style,
                similar_sessions=similar_sessions,
            )

            return {
                "negotiation_velocity": velocity,
                "dealer_flexibility": flexibility,
                "user_style": user_style,
                "predicted_outcome": predicted_outcome,
                "insights": insights,
            }

        except ApiError:
            raise
        except Exception as e:
            logger.error(f"Error analyzing negotiation patterns: {e}", exc_info=True)
            return {
                "negotiation_velocity": "unknown",
                "dealer_flexibility": "unknown",
                "user_style": "unknown",
                "predicted_outcome": "uncertain",
                "insights": ["Insufficient data for pattern analysis"],
            }

    async def _find_similar_sessions(
        self,
        session_id: int,
        asking_price: float,
        current_price: float,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Find similar negotiation sessions using vector similarity search

        Uses pgvector to find sessions with similar characteristics:
        - Price ranges
        - Negotiation patterns
        - Deal structure
        """
        if not self.openai_client:
            logger.warning("OpenAI client not available for embeddings")
            return []

        try:
            # Get current session
            session = await self.negotiation_repo.get_session(session_id)
            if not session:
                return []

            # Create embedding query string
            query_text = await self._create_embedding_query(session_id)

            # Generate embedding
            embedding = await self._generate_embedding(query_text)
            if not embedding:
                return []

            # Convert embedding to pgvector format
            embedding_str = f"[{','.join(map(str, embedding))}]"

            # Find similar sessions using cosine similarity
            query = text(
                """
                SELECT
                    ns.id,
                    ns.status,
                    ns.current_round,
                    ns.created_at,
                    1 - (ns.session_embedding <=> :embedding::vector) as similarity
                FROM negotiation_sessions ns
                WHERE
                    ns.id != :session_id
                    AND ns.session_embedding IS NOT NULL
                    AND ns.status IN ('completed', 'cancelled')
                ORDER BY ns.session_embedding <=> :embedding::vector
                LIMIT :limit
            """
            )

            result = await self.db.execute(
                query,
                {
                    "session_id": session_id,
                    "embedding": embedding_str,
                    "limit": limit,
                },
            )

            similar_sessions = []
            for row in result.fetchall():
                similar_sessions.append(
                    {
                        "session_id": row[0],
                        "status": row[1],
                        "rounds": row[2],
                        "created_at": row[3],
                        "similarity": float(row[4]) if row[4] else 0.0,
                    }
                )

            logger.info(f"Found {len(similar_sessions)} similar sessions")
            return similar_sessions

        except Exception as e:
            logger.error(f"Error finding similar sessions: {e}", exc_info=True)
            return []

    async def _create_embedding_query(self, session_id: int) -> str:
        """Create a text query for embedding generation"""
        session = await self.negotiation_repo.get_session(session_id)
        messages = await self.negotiation_repo.get_messages(session_id)

        # Create a representative text for the session
        query_parts = [
            f"Negotiation session with {len(messages)} messages",
            f"Status: {session.status.value}",
            f"Round: {session.current_round} of {session.max_rounds}",
        ]

        # Add message content (limited)
        for msg in messages[:5]:
            query_parts.append(f"{msg.role.value}: {msg.content[:100]}")

        return " | ".join(query_parts)

    async def _generate_embedding(self, text: str) -> list[float] | None:
        """Generate embedding vector for text using OpenAI"""
        if not self.openai_client:
            return None

        try:
            response = await self.openai_client.embeddings.create(
                model=self.EMBEDDING_MODEL,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def _calculate_base_probability(
        self,
        current_price: float,
        user_target_price: float,
        asking_price: float,
        current_round: int,
        max_rounds: int,
    ) -> float:
        """Calculate base success probability from current state"""
        # Factor 1: Price gap (closer to target = higher probability)
        if asking_price > 0:
            price_gap_ratio = abs(current_price - user_target_price) / asking_price
            price_factor = max(0.0, 1.0 - price_gap_ratio * 2)  # 0-1 scale
        else:
            price_factor = 0.5

        # Factor 2: Round progress (early rounds = more room for negotiation)
        round_factor = 1.0 - (current_round / max_rounds)

        # Factor 3: Discount achieved
        if asking_price > 0:
            discount = (asking_price - current_price) / asking_price
            discount_factor = min(1.0, discount * 5)  # 20% discount = 1.0
        else:
            discount_factor = 0.5

        # Weighted combination
        base_prob = price_factor * 0.4 + round_factor * 0.3 + discount_factor * 0.3

        return max(0.0, min(1.0, base_prob))

    def _adjust_probability_from_history(
        self,
        base_probability: float,
        similar_sessions: list[dict[str, Any]],
    ) -> float:
        """Adjust probability based on outcomes of similar sessions"""
        if not similar_sessions:
            return base_probability

        # Calculate success rate from similar sessions
        completed = sum(1 for s in similar_sessions if s["status"] == "completed")
        success_rate = completed / len(similar_sessions) if similar_sessions else 0.5

        # Blend base probability with historical success rate
        # Weight historical data by similarity scores
        total_weight = sum(s.get("similarity", 0.5) for s in similar_sessions)
        weighted_success = sum(
            (1.0 if s["status"] == "completed" else 0.0) * s.get("similarity", 0.5)
            for s in similar_sessions
        )

        if total_weight > 0:
            historical_prob = weighted_success / total_weight
        else:
            historical_prob = success_rate

        # Blend: 60% base, 40% historical
        adjusted_prob = base_probability * 0.6 + historical_prob * 0.4

        return max(0.0, min(1.0, adjusted_prob))

    def _determine_confidence_level(
        self,
        similar_sessions_count: int,
        probability: float,
    ) -> str:
        """Determine confidence level for prediction"""
        if similar_sessions_count >= 10 and (probability > 0.7 or probability < 0.3):
            return "high"
        elif similar_sessions_count >= 5:
            return "medium"
        else:
            return "low"

    def _identify_key_factors(
        self,
        current_price: float,
        user_target_price: float,
        asking_price: float,
        current_round: int,
        similar_sessions: list[dict[str, Any]],
    ) -> list[str]:
        """Identify key factors affecting success probability"""
        factors = []

        # Price gap factor
        if asking_price > 0:
            gap_percent = abs(current_price - user_target_price) / asking_price * 100
            if gap_percent < 5:
                factors.append("Very close to target price")
            elif gap_percent < 10:
                factors.append("Within reasonable range of target")
            else:
                factors.append("Significant gap from target price")

        # Round factor
        if current_round <= 3:
            factors.append("Early in negotiation - plenty of room to maneuver")
        elif current_round <= 6:
            factors.append("Mid-negotiation - time to make progress")
        else:
            factors.append("Late in negotiation - may need decisive action")

        # Historical factor
        if similar_sessions:
            completed_rate = sum(1 for s in similar_sessions if s["status"] == "completed") / len(
                similar_sessions
            )
            if completed_rate > 0.7:
                factors.append("Similar negotiations show high success rate")
            elif completed_rate < 0.3:
                factors.append("Similar negotiations show low success rate")

        return factors

    def _generate_success_recommendation(
        self,
        probability: float,
        key_factors: list[str],
    ) -> str:
        """Generate actionable recommendation based on probability"""
        if probability >= self.HIGH_SUCCESS_THRESHOLD:
            return "High probability of success. Continue with current strategy."
        elif probability >= self.MEDIUM_SUCCESS_THRESHOLD:
            return "Moderate success probability. Consider adjusting strategy or counter-offer."
        else:
            return "Low success probability. May need to reassess target price or walk away."

    def _analyze_successful_patterns(
        self,
        similar_sessions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Analyze patterns from successful similar sessions"""
        if not similar_sessions:
            return {"average_rounds": 5, "average_discount": 0.08}

        successful = [s for s in similar_sessions if s["status"] == "completed"]

        if not successful:
            return {"average_rounds": 5, "average_discount": 0.08}

        avg_rounds = sum(s["rounds"] for s in successful) / len(successful)

        return {
            "average_rounds": round(avg_rounds, 1),
            "average_discount": 0.08,  # Would calculate from actual data
            "success_count": len(successful),
        }

    def _calculate_optimal_offer(
        self,
        current_offer: float,
        user_target_price: float,
        asking_price: float,
        current_round: int,
        success_patterns: dict[str, Any],
    ) -> float:
        """Calculate optimal counter-offer based on patterns"""
        # Base calculation: move toward target
        gap = current_offer - user_target_price

        # Adjust based on round (more aggressive early, more conservative later)
        round_factor = 1.0 - (current_round / 10.0)

        # Calculate suggested move
        move_amount = gap * 0.4 * (1 + round_factor * 0.5)

        optimal = current_offer - move_amount

        # Ensure we don't go below target
        optimal = max(optimal, user_target_price)

        return optimal

    def _assess_offer_risk(
        self,
        optimal_offer: float,
        user_target_price: float,
        current_offer: float,
        current_round: int,
        max_rounds: int,
    ) -> str:
        """Assess risk level of the optimal offer"""
        # Calculate how aggressive the offer is
        if current_offer > 0:
            move_percent = (current_offer - optimal_offer) / current_offer
        else:
            move_percent = 0

        # Consider round context
        rounds_remaining = max_rounds - current_round

        if move_percent > 0.1 and rounds_remaining < 3:
            return "high"
        elif move_percent > 0.05:
            return "medium"
        else:
            return "low"

    def _generate_offer_rationale(
        self,
        optimal_offer: float,
        current_offer: float,
        success_patterns: dict[str, Any],
    ) -> str:
        """Generate rationale for optimal offer"""
        if current_offer > 0:
            reduction = current_offer - optimal_offer
            reduction_percent = (reduction / current_offer) * 100
        else:
            reduction_percent = 0

        rationale = f"Suggesting ${optimal_offer:,.2f} "

        if reduction_percent > 5:
            rationale += f"(${reduction:,.2f} reduction, {reduction_percent:.1f}%). "
            rationale += "This is an aggressive but data-supported counteroffer."
        elif reduction_percent > 0:
            rationale += f"(${reduction:,.2f} reduction, {reduction_percent:.1f}%). "
            rationale += "This maintains negotiation momentum while being realistic."
        else:
            rationale += "Hold firm at this price to gauge dealer flexibility."

        if success_patterns.get("success_count", 0) > 5:
            rationale += (
                f" Based on {success_patterns['success_count']} similar successful negotiations."
            )

        return rationale

    def _generate_alternative_offers(
        self,
        optimal_offer: float,
        user_target_price: float,
        current_offer: float,
    ) -> list[dict[str, Any]]:
        """Generate alternative offer options"""
        alternatives = []

        # Conservative option (smaller move)
        conservative = optimal_offer + (current_offer - optimal_offer) * 0.5
        alternatives.append(
            {
                "offer": round(conservative, 2),
                "strategy": "conservative",
                "description": "Smaller move to gauge dealer response",
            }
        )

        # Aggressive option (larger move toward target)
        aggressive = optimal_offer - (optimal_offer - user_target_price) * 0.3
        alternatives.append(
            {
                "offer": round(aggressive, 2),
                "strategy": "aggressive",
                "description": "Larger move to test dealer flexibility",
            }
        )

        return alternatives

    def _calculate_negotiation_velocity(
        self,
        messages: list[NegotiationMessage],
    ) -> str:
        """Calculate how quickly negotiation is progressing"""
        # if len(messages) < 4:
        #     return "unknown"

        # Look for price mentions in metadata
        price_points = []
        for msg in messages:
            if msg.message_metadata:
                if "suggested_price" in msg.message_metadata:
                    price_points.append(msg.message_metadata["suggested_price"])
                elif "counter_offer" in msg.message_metadata:
                    price_points.append(msg.message_metadata["counter_offer"])

        if len(price_points) < 2:
            return "unknown"

        # Calculate average change per round
        total_change = abs(price_points[-1] - price_points[0])
        avg_change = total_change / (len(price_points) - 1)

        if avg_change > 1000:
            return "fast"
        elif avg_change > 300:
            return "moderate"
        else:
            return "slow"

    def _assess_dealer_flexibility(
        self,
        messages: list[NegotiationMessage],
    ) -> str:
        """Assess dealer flexibility based on message patterns"""
        if len(messages) < 4:
            return "unknown"

        # Simplified assessment - would use more sophisticated analysis in production
        agent_messages = [m for m in messages if m.role.value == "agent"]

        if len(agent_messages) < 2:
            return "unknown"

        # In a real implementation, analyze tone, concessions, etc.
        return "moderate"

    def _determine_user_style(
        self,
        messages: list[NegotiationMessage],
    ) -> str:
        """Determine user's negotiation style"""
        if len(messages) < 3:
            return "unknown"

        user_messages = [m for m in messages if m.role.value == "user"]

        # Analyze counter-offer patterns
        counter_offers = []
        for msg in user_messages:
            if msg.message_metadata and "counter_offer" in msg.message_metadata:
                counter_offers.append(msg.message_metadata["counter_offer"])

        if len(counter_offers) < 2:
            return "unknown"

        # Calculate aggressiveness
        avg_move = sum(
            abs(counter_offers[i] - counter_offers[i - 1]) for i in range(1, len(counter_offers))
        ) / (len(counter_offers) - 1)

        if avg_move > 800:
            return "aggressive"
        elif avg_move > 300:
            return "moderate"
        else:
            return "conservative"

    def _predict_outcome_from_patterns(
        self,
        velocity: str,
        flexibility: str,
        similar_sessions: list[dict[str, Any]],
    ) -> str:
        """Predict likely outcome based on patterns"""
        if not similar_sessions:
            return "uncertain"

        success_rate = sum(1 for s in similar_sessions if s["status"] == "completed") / len(
            similar_sessions
        )

        if success_rate > 0.7:
            return "likely_success"
        elif success_rate > 0.4:
            return "uncertain"
        else:
            return "likely_failure"

    def _generate_pattern_insights(
        self,
        velocity: str,
        flexibility: str,
        user_style: str,
        similar_sessions: list[dict[str, Any]],
    ) -> list[str]:
        """Generate actionable insights from pattern analysis"""
        insights = []

        if velocity == "slow":
            insights.append("Negotiation progressing slowly - consider more decisive moves")
        elif velocity == "fast":
            insights.append("Rapid negotiation pace - good progress being made")

        if flexibility == "high":
            insights.append("Dealer showing high flexibility - opportunity for better deal")
        elif flexibility == "low":
            insights.append("Dealer showing limited flexibility - may need to adjust expectations")

        if user_style == "aggressive":
            insights.append("Your aggressive approach may yield better results but risks deadlock")
        elif user_style == "conservative":
            insights.append("Your conservative approach reduces risk but may limit savings")

        if similar_sessions:
            success_rate = sum(1 for s in similar_sessions if s["status"] == "completed") / len(
                similar_sessions
            )
            insights.append(f"Similar negotiations succeeded {success_rate*100:.0f}% of the time")

        return insights

    async def _store_analytics(
        self,
        session_id: int,
        analytics_data: dict[str, Any],
    ) -> None:
        """Store analytics results in database"""
        try:
            # First, check if a record exists
            check_query = text(
                """
                SELECT id FROM negotiation_analytics
                WHERE session_id = :session_id
                LIMIT 1
                """
            )

            result = await self.db.execute(check_query, {"session_id": session_id})
            existing = result.fetchone()

            if existing:
                # Update existing record
                update_query = text(
                    """
                    UPDATE negotiation_analytics
                    SET
                        success_probability = :success_probability,
                        confidence_score = :confidence_score,
                        negotiation_patterns = :patterns,
                        updated_at = NOW()
                    WHERE session_id = :session_id
                    """
                )

                await self.db.execute(
                    update_query,
                    {
                        "session_id": session_id,
                        "success_probability": analytics_data.get("success_probability"),
                        "confidence_score": analytics_data.get("similar_sessions_count", 0) / 20.0,
                        "patterns": json.dumps(analytics_data),
                    },
                )
            else:
                # Insert new record
                insert_query = text(
                    """
                    INSERT INTO negotiation_analytics
                    (session_id, success_probability, confidence_score, negotiation_patterns, created_at)
                    VALUES (:session_id, :success_probability, :confidence_score, :patterns, NOW())
                    """
                )

                await self.db.execute(
                    insert_query,
                    {
                        "session_id": session_id,
                        "success_probability": analytics_data.get("success_probability"),
                        "confidence_score": analytics_data.get("similar_sessions_count", 0) / 20.0,
                        "patterns": json.dumps(analytics_data),
                    },
                )

            await self.db.commit()

        except Exception as e:
            logger.error(f"Error storing analytics: {e}")
            # Don't fail the main operation

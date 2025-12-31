import logging
from typing import Any

from app.repositories.negotiation_repository import NegotiationRepository
from app.services.market_intelligence_service import MarketIntelligenceService
from app.services.negotiation_analytics_service import NegotiationAnalyticsService

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Handles all AI-driven metrics, market intelligence, and ML predictions for negotiations."""

    def __init__(self, db):
        self.db = db
        self.negotiation_repo = NegotiationRepository(db)
        self.analytics_service = NegotiationAnalyticsService(db)
        self.market_intelligence_service = MarketIntelligenceService()

    async def _calculate_ai_metrics(
        self,
        session_id: int,
        deal: Any,
        current_price: float,
        user_target: float,
        messages: list[Any] | None = None,
    ) -> dict[str, Any]:
        """
        Calculate enhanced AI metrics for negotiation intelligence

        Now integrates:
        - Market intelligence data (real-time comps, price trends)
        - ML-based success probability prediction
        - Historical negotiation pattern analysis
        - Competitor analysis

        Args:
            session_id: Session ID for message history
            deal: Deal object with asking price and vehicle details
            current_price: Current suggested/negotiated price
            user_target: User's target price
            messages: Optional pre-fetched messages to avoid redundant queries

        Returns:
            Dictionary with enhanced AI metrics including market intelligence,
            ML predictions, and historical analysis
        """
        # Use provided messages or fetch if not provided
        if messages is None:
            messages = await self.negotiation_repo.get_messages(session_id)

        # Calculate confidence score based on deal quality
        # Handle edge case where current_price > asking_price (negative discount)
        if deal.asking_price > 0:
            discount_percent = ((deal.asking_price - current_price) / deal.asking_price) * 100
        else:
            discount_percent = 0

        # Confidence based on discount percentage and negotiation progress
        # Handle negative discounts (price increases) with low confidence
        if discount_percent < 0:  # Price increase - very poor deal
            confidence_score = 0.20
        elif discount_percent >= 15:  # Excellent deal (15%+ off)
            confidence_score = 0.95
        elif discount_percent >= 10:  # Very good deal (10-15% off)
            confidence_score = 0.85
        elif discount_percent >= 5:  # Good deal (5-10% off)
            confidence_score = 0.75
        elif discount_percent >= 2:  # Fair deal (2-5% off)
            confidence_score = 0.65
        else:  # Marginal deal (<2% off)
            confidence_score = 0.50

        # Calculate dealer concession rate (total price movement / asking price)
        initial_asking = deal.asking_price
        dealer_concession_rate = (
            (initial_asking - current_price) / initial_asking if initial_asking > 0 else 0
        )

        # Calculate negotiation velocity (average price change per round)
        round_count = max(len({msg.round_number for msg in messages}), 1)
        negotiation_velocity = (initial_asking - current_price) / round_count

        # === PHASE 3 ENHANCEMENTS: Market Intelligence Integration ===
        market_intelligence = {}
        try:
            # Get real-time comparable pricing data
            comps_data = await self.market_intelligence_service.get_real_time_comps(
                make=deal.vehicle_make,
                model=deal.vehicle_model,
                year=deal.vehicle_year,
                mileage=deal.vehicle_mileage or 0,
                zip_code=None,  # Could be extracted from user preferences
                max_results=10,
            )

            # Get price trend analysis
            trend_data = await self.market_intelligence_service.get_price_trend(
                make=deal.vehicle_make,
                model=deal.vehicle_model,
                year=deal.vehicle_year,
            )

            market_intelligence = {
                "average_market_price": comps_data.get("average_price", 0),
                "median_market_price": comps_data.get("median_price", 0),
                "comparables_found": comps_data.get("total_found", 0),
                "market_summary": comps_data.get("market_summary", ""),
                "price_trend": trend_data.get("trend_direction", "stable"),
                "demand_level": trend_data.get("demand_level", "medium"),
                "market_days_supply": trend_data.get("market_days_supply", 0),
            }

            # Adjust confidence based on market data
            if comps_data.get("average_price", 0) > 0:
                market_avg = comps_data["average_price"]
                # If current price is below market average, boost confidence
                if current_price < market_avg:
                    price_vs_market = (market_avg - current_price) / market_avg
                    confidence_score = min(1.0, confidence_score + price_vs_market * 0.15)

        except Exception as e:
            logger.warning(f"Failed to get market intelligence: {e}")
            # Continue with basic metrics if market data unavailable

        # === PHASE 3 ENHANCEMENTS: ML-Based Success Probability ===
        ml_prediction = {}
        try:
            success_analysis = await self.analytics_service.calculate_success_probability(
                session_id=session_id,
                current_price=current_price,
                user_target_price=user_target,
                asking_price=deal.asking_price,
            )

            ml_prediction = {
                "success_probability": success_analysis.get("success_probability", 0.5),
                "ml_confidence_level": success_analysis.get("confidence_level", "low"),
                "key_factors": success_analysis.get("key_factors", []),
                "similar_sessions": success_analysis.get("similar_sessions_count", 0),
            }

            # Blend ML confidence with rule-based confidence
            ml_success_prob = success_analysis.get("success_probability", 0.5)
            confidence_score = (confidence_score * 0.6) + (ml_success_prob * 0.4)

        except Exception as e:
            logger.warning(f"Failed to calculate ML prediction: {e}")
            # Continue with basic metrics if ML unavailable

        # === PHASE 3 ENHANCEMENTS: Historical Pattern Analysis ===
        pattern_analysis = {}
        try:
            patterns = await self.analytics_service.analyze_negotiation_patterns(
                session_id=session_id,
            )

            pattern_analysis = {
                "negotiation_velocity_pattern": patterns.get("negotiation_velocity", "unknown"),
                "dealer_flexibility_pattern": patterns.get("dealer_flexibility", "unknown"),
                "predicted_outcome": patterns.get("predicted_outcome", "uncertain"),
                "pattern_insights": patterns.get("insights", []),
            }

        except Exception as e:
            logger.warning(f"Failed to analyze patterns: {e}")
            # Continue with basic metrics if pattern analysis unavailable

        # === PHASE 3 ENHANCEMENTS: Optimal Counter-Offer Suggestion ===
        optimal_offer_data = {}
        try:
            optimal_offer_result = await self.analytics_service.get_optimal_counter_offer(
                session_id=session_id,
                current_offer=current_price,
                user_target_price=user_target,
                asking_price=deal.asking_price,
            )

            optimal_offer_data = {
                "ml_optimal_offer": optimal_offer_result.get("optimal_offer", current_price),
                "optimal_offer_rationale": optimal_offer_result.get("rationale", ""),
                "expected_savings": optimal_offer_result.get("expected_savings", 0),
                "offer_risk_assessment": optimal_offer_result.get("risk_assessment", "medium"),
            }

        except Exception as e:
            logger.warning(f"Failed to calculate optimal offer: {e}")
            # Continue with basic metrics if optimal offer calculation unavailable

        # Determine recommended action (enhanced with market/ML data)
        if discount_percent < 0:  # Price increase
            recommended_action = "reject"
        elif current_price <= user_target:
            recommended_action = "accept"
        elif discount_percent >= 8:  # Getting decent discount
            recommended_action = "consider"
        # Check if ML prediction suggests accepting
        elif ml_prediction.get("success_probability", 0) > 0.75:
            recommended_action = "consider"
        else:
            recommended_action = "counter"

        # Generate enhanced strategy adjustments
        strategy_adjustments = self._generate_enhanced_strategy(
            dealer_concession_rate=dealer_concession_rate,
            round_count=round_count,
            market_intelligence=market_intelligence,
            pattern_analysis=pattern_analysis,
            ml_prediction=ml_prediction,
        )

        # Enhanced market comparison with real data
        market_comparison = self._generate_market_comparison(
            discount_percent=discount_percent,
            current_price=current_price,
            market_intelligence=market_intelligence,
        )

        # === Return Enhanced Metrics ===
        return {
            # Original metrics
            "confidence_score": round(confidence_score, 2),
            "recommended_action": recommended_action,
            "strategy_adjustments": strategy_adjustments,
            "dealer_concession_rate": round(dealer_concession_rate, 3),
            "negotiation_velocity": round(negotiation_velocity, 2),
            "market_comparison": market_comparison,
            # Phase 3: Market Intelligence
            **market_intelligence,
            # Phase 3: ML Predictions
            **ml_prediction,
            # Phase 3: Pattern Analysis
            **pattern_analysis,
            # Phase 3: Optimal Offer
            **optimal_offer_data,
        }

    def _generate_enhanced_strategy(
        self,
        dealer_concession_rate: float,
        round_count: int,
        market_intelligence: dict[str, Any],
        pattern_analysis: dict[str, Any],
        ml_prediction: dict[str, Any],
    ) -> str:
        """Generate enhanced strategy adjustments using market and ML data"""
        # Start with base strategy
        if dealer_concession_rate > 0.10:
            strategy = (
                "Dealer showing strong flexibility. You have significant leverage—push for more!"
            )
        elif dealer_concession_rate > 0.05:
            strategy = "Moderate progress. Consider one more counter to maximize your savings."
        elif round_count > 5:
            strategy = (
                "Limited movement detected. Consider accepting current offer or walking away."
            )
        elif dealer_concession_rate <= 0.02:
            strategy = (
                "Early in the negotiation, but the dealer has shown limited flexibility so far. "
                "Consider refining your counteroffer rationale and be prepared with a walk-away price "
                "if movement remains minimal."
            )
        else:
            strategy = "Early stage. Continue negotiating strategically to secure the best price."

        # Enhance with market intelligence
        if market_intelligence.get("demand_level") == "high":
            strategy += " Market demand is high—consider negotiating quickly."
        elif market_intelligence.get("demand_level") == "low":
            strategy += " Low market demand gives you strong negotiating leverage."

        # Add ML insights
        if ml_prediction.get("success_probability", 0) > 0.75:
            strategy += " ML analysis suggests high probability of success with current approach."
        elif ml_prediction.get("success_probability", 0) < 0.3:
            strategy += " ML analysis suggests reconsidering your strategy or target price."

        return strategy

    def _generate_market_comparison(
        self,
        discount_percent: float,
        current_price: float,
        market_intelligence: dict[str, Any],
    ) -> str:
        """Generate market comparison with real comparable data"""
        # Base comparison
        if discount_percent < 0:
            comparison = f"Warning: Price is {abs(discount_percent):.1f}% above asking. This is unusual and not recommended."
        elif discount_percent >= 10:
            comparison = f"Excellent! You're {discount_percent:.1f}% below asking—better than typical market deals."
        elif discount_percent >= 5:
            comparison = (
                f"Solid progress at {discount_percent:.1f}% off. Average market discount is 3-7%."
            )
        else:
            comparison = (
                f"Currently at {discount_percent:.1f}% off. Most buyers achieve 5-10% discounts."
            )

        # Enhance with real market data
        avg_market = market_intelligence.get("average_market_price", 0)
        if avg_market > 0 and current_price > 0:
            vs_market = ((avg_market - current_price) / avg_market) * 100
            if vs_market > 5:
                comparison += f" Current price is {vs_market:.1f}% below market average of ${avg_market:,.0f}!"
            elif vs_market < -5:
                comparison += (
                    f" Warning: {abs(vs_market):.1f}% above market average of ${avg_market:,.0f}."
                )
            else:
                comparison += f" Price aligns with market average of ${avg_market:,.0f}."

        # Add market trend context
        trend = market_intelligence.get("price_trend", "")
        if trend == "increasing":
            comparison += " Prices are trending upward—act soon."
        elif trend == "decreasing":
            comparison += " Prices are trending downward—you may get better deals soon."

        return comparison

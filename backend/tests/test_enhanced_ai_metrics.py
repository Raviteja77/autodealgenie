"""
Integration tests for enhanced AI metrics in negotiation service
Tests the Phase 3 enhancements to _calculate_ai_metrics
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.negotiation import MessageRole
from app.services.negotiation import NegotiationService


class MockDeal:
    """Mock Deal object for testing"""

    def __init__(self):
        self.id = 1
        self.asking_price = 25000
        self.vehicle_make = "Toyota"
        self.vehicle_model = "Camry"
        self.vehicle_year = 2022
        self.vehicle_mileage = 15000
        self.vehicle_vin = "TEST_VIN_123"


class MockMessage:
    """Mock NegotiationMessage object"""

    def __init__(self, round_number, role="user", metadata=None):
        self.round_number = round_number
        self.role = MessageRole.USER if role == "user" else MessageRole.AGENT
        self.message_metadata = metadata or {}
        self.content = "Test message"


@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    return MagicMock()


@pytest.fixture
def negotiation_service(mock_db_session):
    """Create NegotiationService with mocked dependencies"""
    service = NegotiationService(mock_db_session)
    service.negotiation_repo = MagicMock()
    return service


class TestEnhancedAIMetrics:
    """Tests for enhanced _calculate_ai_metrics with Phase 3 integrations"""

    @pytest.mark.asyncio
    async def test_calculate_ai_metrics_with_market_intelligence(self, negotiation_service):
        """Test AI metrics calculation with market intelligence data"""
        deal = MockDeal()
        messages = [MockMessage(1), MockMessage(2)]

        # Mock market intelligence service
        negotiation_service.metrics.market_intelligence_service.get_real_time_comps = AsyncMock(
            return_value={
                "average_price": 24000,
                "median_price": 23500,
                "total_found": 20,
                "market_summary": "Found 20 comparable vehicles",
            }
        )

        negotiation_service.metrics.market_intelligence_service.get_price_trend = AsyncMock(
            return_value={
                "trend_direction": "decreasing",
                "demand_level": "low",
                "market_days_supply": 65.0,
            }
        )

        # Mock analytics service to avoid ML calls
        negotiation_service.metrics.analytics_service.calculate_success_probability = AsyncMock(
            side_effect=Exception("Skip ML")
        )
        negotiation_service.metrics.analytics_service.analyze_negotiation_patterns = AsyncMock(
            side_effect=Exception("Skip ML")
        )
        negotiation_service.metrics.analytics_service.get_optimal_counter_offer = AsyncMock(
            side_effect=Exception("Skip ML")
        )

        metrics = await negotiation_service.metrics._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=22000,
            user_target=21000,
            messages=messages,
        )

        # Verify market intelligence data is included
        assert "average_market_price" in metrics
        assert metrics["average_market_price"] == 24000
        assert metrics["median_market_price"] == 23500
        assert metrics["comparables_found"] == 20
        assert metrics["price_trend"] == "decreasing"
        assert metrics["demand_level"] == "low"
        assert metrics["market_days_supply"] == 65.0

        # Verify basic metrics still present
        assert "confidence_score" in metrics
        assert "recommended_action" in metrics
        assert "strategy_adjustments" in metrics

    @pytest.mark.asyncio
    async def test_calculate_ai_metrics_with_ml_prediction(self, negotiation_service):
        """Test AI metrics calculation with ML success probability"""
        deal = MockDeal()
        messages = [MockMessage(1)]

        # Mock market intelligence to skip
        negotiation_service.metrics.market_intelligence_service.get_real_time_comps = AsyncMock(
            side_effect=Exception("Skip market")
        )
        negotiation_service.metrics.market_intelligence_service.get_price_trend = AsyncMock(
            side_effect=Exception("Skip market")
        )

        # Mock ML prediction
        negotiation_service.metrics.analytics_service.calculate_success_probability = AsyncMock(
            return_value={
                "success_probability": 0.85,
                "confidence_level": "high",
                "key_factors": ["Close to target", "Early stage"],
                "similar_sessions_count": 12,
            }
        )

        # Mock other analytics
        negotiation_service.metrics.analytics_service.analyze_negotiation_patterns = AsyncMock(
            side_effect=Exception("Skip")
        )
        negotiation_service.metrics.analytics_service.get_optimal_counter_offer = AsyncMock(
            side_effect=Exception("Skip")
        )

        metrics = await negotiation_service.metrics._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=21500,
            user_target=21000,
            messages=messages,
        )

        # Verify ML prediction data is included
        assert "success_probability" in metrics
        assert metrics["success_probability"] == 0.85
        assert metrics["ml_confidence_level"] == "high"
        assert "key_factors" in metrics
        assert metrics["similar_sessions"] == 12

        # Confidence score should be blended with ML prediction
        assert metrics["confidence_score"] > 0.5

    @pytest.mark.asyncio
    async def test_calculate_ai_metrics_with_pattern_analysis(self, negotiation_service):
        """Test AI metrics calculation with pattern analysis"""
        deal = MockDeal()
        messages = [MockMessage(i) for i in range(1, 5)]

        # Skip other services
        negotiation_service.metrics.market_intelligence_service.get_real_time_comps = AsyncMock(
            side_effect=Exception("Skip")
        )
        negotiation_service.metrics.market_intelligence_service.get_price_trend = AsyncMock(
            side_effect=Exception("Skip")
        )
        negotiation_service.metrics.analytics_service.calculate_success_probability = AsyncMock(
            side_effect=Exception("Skip")
        )

        # Mock pattern analysis
        negotiation_service.metrics.analytics_service.analyze_negotiation_patterns = AsyncMock(
            return_value={
                "negotiation_velocity": "fast",
                "dealer_flexibility": "high",
                "predicted_outcome": "likely_success",
                "insights": ["Good progress", "Dealer flexible"],
            }
        )

        negotiation_service.metrics.analytics_service.get_optimal_counter_offer = AsyncMock(
            side_effect=Exception("Skip")
        )

        metrics = await negotiation_service.metrics._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=22500,
            user_target=21000,
            messages=messages,
        )

        # Verify pattern analysis data is included
        assert metrics["negotiation_velocity_pattern"] == "fast"
        assert metrics["dealer_flexibility_pattern"] == "high"
        assert metrics["predicted_outcome"] == "likely_success"
        assert "pattern_insights" in metrics

    @pytest.mark.asyncio
    async def test_calculate_ai_metrics_with_optimal_offer(self, negotiation_service):
        """Test AI metrics calculation with optimal counter-offer"""
        deal = MockDeal()
        messages = [MockMessage(1)]

        # Skip other services
        negotiation_service.metrics.market_intelligence_service.get_real_time_comps = AsyncMock(
            side_effect=Exception("Skip")
        )
        negotiation_service.metrics.market_intelligence_service.get_price_trend = AsyncMock(
            side_effect=Exception("Skip")
        )
        negotiation_service.metrics.analytics_service.calculate_success_probability = AsyncMock(
            side_effect=Exception("Skip")
        )
        negotiation_service.metrics.analytics_service.analyze_negotiation_patterns = AsyncMock(
            side_effect=Exception("Skip")
        )

        # Mock optimal offer calculation
        negotiation_service.metrics.analytics_service.get_optimal_counter_offer = AsyncMock(
            return_value={
                "optimal_offer": 21800,
                "rationale": "Data-driven suggestion based on similar negotiations",
                "expected_savings": 3200,
                "risk_assessment": "low",
            }
        )

        metrics = await negotiation_service.metrics._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=23000,
            user_target=21000,
            messages=messages,
        )

        # Verify optimal offer data is included
        assert metrics["ml_optimal_offer"] == 21800
        assert "optimal_offer_rationale" in metrics
        assert metrics["expected_savings"] == 3200
        assert metrics["offer_risk_assessment"] == "low"

    @pytest.mark.asyncio
    async def test_calculate_ai_metrics_all_integrations(self, negotiation_service):
        """Test AI metrics with all Phase 3 integrations working"""
        deal = MockDeal()
        messages = [MockMessage(i) for i in range(1, 4)]

        # Mock all services successfully
        negotiation_service.metrics.market_intelligence_service.get_real_time_comps = AsyncMock(
            return_value={
                "average_price": 24000,
                "median_price": 23800,
                "total_found": 25,
                "market_summary": "Strong market data",
            }
        )

        negotiation_service.metrics.market_intelligence_service.get_price_trend = AsyncMock(
            return_value={
                "trend_direction": "stable",
                "demand_level": "medium",
                "market_days_supply": 45.0,
            }
        )

        negotiation_service.metrics.analytics_service.calculate_success_probability = AsyncMock(
            return_value={
                "success_probability": 0.75,
                "confidence_level": "high",
                "key_factors": ["Good positioning"],
                "similar_sessions_count": 10,
            }
        )

        negotiation_service.metrics.analytics_service.analyze_negotiation_patterns = AsyncMock(
            return_value={
                "negotiation_velocity": "moderate",
                "dealer_flexibility": "moderate",
                "predicted_outcome": "uncertain",
                "insights": ["Standard progress"],
            }
        )

        negotiation_service.metrics.analytics_service.get_optimal_counter_offer = AsyncMock(
            return_value={
                "optimal_offer": 22200,
                "rationale": "Balanced approach",
                "expected_savings": 2800,
                "risk_assessment": "medium",
            }
        )

        metrics = await negotiation_service.metrics._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=23000,
            user_target=21500,
            messages=messages,
        )

        # Verify all enhancements are present
        # Market Intelligence
        assert metrics["average_market_price"] == 24000
        assert metrics["price_trend"] == "stable"

        # ML Predictions
        assert metrics["success_probability"] == 0.75
        assert metrics["ml_confidence_level"] == "high"

        # Pattern Analysis
        assert metrics["negotiation_velocity_pattern"] == "moderate"
        assert metrics["predicted_outcome"] == "uncertain"

        # Optimal Offer
        assert metrics["ml_optimal_offer"] == 22200
        assert metrics["expected_savings"] == 2800

        # Original metrics still present
        assert "confidence_score" in metrics
        assert "recommended_action" in metrics

    @pytest.mark.asyncio
    async def test_calculate_ai_metrics_graceful_degradation(self, negotiation_service):
        """Test that metrics work even when all enhancements fail"""
        deal = MockDeal()
        messages = [MockMessage(1)]

        # All services fail
        negotiation_service.metrics.market_intelligence_service.get_real_time_comps = AsyncMock(
            side_effect=Exception("Market service down")
        )
        negotiation_service.metrics.market_intelligence_service.get_price_trend = AsyncMock(
            side_effect=Exception("Market service down")
        )
        negotiation_service.metrics.analytics_service.calculate_success_probability = AsyncMock(
            side_effect=Exception("ML service down")
        )
        negotiation_service.metrics.analytics_service.analyze_negotiation_patterns = AsyncMock(
            side_effect=Exception("ML service down")
        )
        negotiation_service.metrics.analytics_service.get_optimal_counter_offer = AsyncMock(
            side_effect=Exception("ML service down")
        )

        # Should still return basic metrics without crashing
        metrics = await negotiation_service.metrics._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=22000,
            user_target=21000,
            messages=messages,
        )

        # Basic metrics should still be present
        assert "confidence_score" in metrics
        assert "recommended_action" in metrics
        assert "strategy_adjustments" in metrics
        assert "dealer_concession_rate" in metrics
        assert "negotiation_velocity" in metrics
        assert "market_comparison" in metrics


class TestEnhancedStrategyGeneration:
    """Tests for enhanced strategy generation with market and ML data"""

    def test_generate_enhanced_strategy_high_demand(self, negotiation_service):
        """Test strategy with high market demand"""
        strategy = negotiation_service.metrics._generate_enhanced_strategy(
            dealer_concession_rate=0.08,
            round_count=3,
            market_intelligence={"demand_level": "high", "price_trend": "increasing"},
            pattern_analysis={},
            ml_prediction={},
        )

        assert "high" in strategy.lower() or "demand" in strategy.lower()
        assert "quickly" in strategy.lower() or "negotiate quickly" in strategy.lower()

    def test_generate_enhanced_strategy_low_demand(self, negotiation_service):
        """Test strategy with low market demand"""
        strategy = negotiation_service.metrics._generate_enhanced_strategy(
            dealer_concession_rate=0.03,
            round_count=2,
            market_intelligence={"demand_level": "low", "price_trend": "decreasing"},
            pattern_analysis={},
            ml_prediction={},
        )

        assert "low" in strategy.lower() or "leverage" in strategy.lower()

    def test_generate_enhanced_strategy_high_ml_success(self, negotiation_service):
        """Test strategy with high ML success probability"""
        strategy = negotiation_service.metrics._generate_enhanced_strategy(
            dealer_concession_rate=0.06,
            round_count=3,
            market_intelligence={},
            pattern_analysis={},
            ml_prediction={"success_probability": 0.85},
        )

        assert "ml" in strategy.lower() or "high probability" in strategy.lower()

    def test_generate_enhanced_strategy_low_ml_success(self, negotiation_service):
        """Test strategy with low ML success probability"""
        strategy = negotiation_service.metrics._generate_enhanced_strategy(
            dealer_concession_rate=0.02,
            round_count=7,
            market_intelligence={},
            pattern_analysis={},
            ml_prediction={"success_probability": 0.25},
        )

        assert "reconsider" in strategy.lower() or "strategy" in strategy.lower()


class TestEnhancedMarketComparison:
    """Tests for enhanced market comparison with real data"""

    def test_generate_market_comparison_below_market(self, negotiation_service):
        """Test comparison when price is below market average"""
        comparison = negotiation_service.metrics._generate_market_comparison(
            discount_percent=8.0,
            current_price=22000,
            market_intelligence={"average_market_price": 24000},
        )

        assert "below market average" in comparison.lower()
        assert "24,000" in comparison or "24000" in comparison

    def test_generate_market_comparison_above_market(self, negotiation_service):
        """Test comparison when price is above market average"""
        comparison = negotiation_service.metrics._generate_market_comparison(
            discount_percent=2.0,
            current_price=25000,
            market_intelligence={"average_market_price": 23000},
        )

        assert "above market average" in comparison.lower()
        assert "warning" in comparison.lower()

    def test_generate_market_comparison_with_trend(self, negotiation_service):
        """Test comparison with price trend data"""
        comparison = negotiation_service.metrics._generate_market_comparison(
            discount_percent=5.0,
            current_price=23000,
            market_intelligence={
                "average_market_price": 23500,
                "price_trend": "increasing",
            },
        )

        assert "increasing" in comparison.lower() or "upward" in comparison.lower()
        assert "soon" in comparison.lower() or "act" in comparison.lower()

"""Test AI metrics calculation in negotiation service"""

import pytest
from unittest.mock import MagicMock

from app.services.negotiation_service import NegotiationService


class MockDeal:
    """Mock Deal object for testing"""

    def __init__(self, asking_price):
        self.asking_price = asking_price
        self.vehicle_make = "Toyota"
        self.vehicle_model = "Camry"
        self.vehicle_year = 2022
        self.vehicle_mileage = 15000


class MockMessage:
    """Mock NegotiationMessage object for testing"""

    def __init__(self, round_number, metadata=None):
        self.round_number = round_number
        self.metadata = metadata or {}


@pytest.fixture
def negotiation_service(db):
    """Create a NegotiationService instance for testing"""
    return NegotiationService(db)


class TestCalculateAIMetrics:
    """Test suite for _calculate_ai_metrics method"""

    def test_excellent_deal_15_percent_off(self, negotiation_service):
        """Test excellent deal with 15% discount"""
        deal = MockDeal(asking_price=25000)
        current_price = 21250  # 15% off
        user_target = 22000
        messages = [MockMessage(1), MockMessage(2)]

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        assert metrics["confidence_score"] == 0.95
        assert metrics["recommended_action"] == "accept"
        assert "Excellent" in metrics["market_comparison"]

    def test_very_good_deal_10_to_15_percent_off(self, negotiation_service):
        """Test very good deal with 10-15% discount"""
        deal = MockDeal(asking_price=25000)
        current_price = 22500  # 10% off
        user_target = 23000
        messages = [MockMessage(1)]

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        assert metrics["confidence_score"] == 0.85
        assert metrics["recommended_action"] == "accept"

    def test_good_deal_5_to_10_percent_off(self, negotiation_service):
        """Test good deal with 5-10% discount"""
        deal = MockDeal(asking_price=25000)
        current_price = 23750  # 5% off
        user_target = 23500
        messages = [MockMessage(1)]

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        assert metrics["confidence_score"] == 0.75
        assert metrics["recommended_action"] == "accept"

    def test_fair_deal_2_to_5_percent_off(self, negotiation_service):
        """Test fair deal with 2-5% discount"""
        deal = MockDeal(asking_price=25000)
        current_price = 24375  # 2.5% off
        user_target = 23000
        messages = [MockMessage(1)]

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        assert metrics["confidence_score"] == 0.65
        assert metrics["recommended_action"] == "counter"

    def test_marginal_deal_less_than_2_percent_off(self, negotiation_service):
        """Test marginal deal with <2% discount"""
        deal = MockDeal(asking_price=25000)
        current_price = 24750  # 1% off
        user_target = 23000
        messages = [MockMessage(1)]

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        assert metrics["confidence_score"] == 0.50
        assert metrics["recommended_action"] == "counter"

    def test_negative_discount_price_increase(self, negotiation_service):
        """Test negative discount when current_price > asking_price"""
        deal = MockDeal(asking_price=25000)
        current_price = 26000  # 4% increase
        user_target = 23000
        messages = [MockMessage(1)]

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        assert metrics["confidence_score"] == 0.20
        assert metrics["recommended_action"] == "reject"
        assert "Warning" in metrics["market_comparison"]
        assert "above asking" in metrics["market_comparison"]

    def test_dealer_very_flexible(self, negotiation_service):
        """Test dealer concession rate > 10%"""
        deal = MockDeal(asking_price=25000)
        current_price = 22000  # 12% off
        user_target = 23000
        messages = [MockMessage(1)]

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        assert metrics["dealer_concession_rate"] == 0.12
        assert "strong flexibility" in metrics["strategy_adjustments"]

    def test_dealer_moderate_flexibility(self, negotiation_service):
        """Test dealer concession rate 5-10%"""
        deal = MockDeal(asking_price=25000)
        current_price = 23750  # 5% off
        user_target = 23000
        messages = [MockMessage(1)]

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        assert metrics["dealer_concession_rate"] == 0.05
        assert "Moderate progress" in metrics["strategy_adjustments"]

    def test_many_rounds_little_movement(self, negotiation_service):
        """Test strategy when round_count > 5"""
        deal = MockDeal(asking_price=25000)
        current_price = 24500  # 2% off
        user_target = 23000
        messages = [
            MockMessage(1),
            MockMessage(2),
            MockMessage(3),
            MockMessage(4),
            MockMessage(5),
            MockMessage(6),
        ]

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        assert "Limited movement detected" in metrics["strategy_adjustments"]

    def test_early_stage_low_concession(self, negotiation_service):
        """Test early stage with low dealer concession"""
        deal = MockDeal(asking_price=25000)
        current_price = 24900  # 0.4% off (very low)
        user_target = 23000
        messages = [MockMessage(1), MockMessage(2)]  # Only 2 rounds

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        assert "limited flexibility" in metrics["strategy_adjustments"]
        assert "walk-away price" in metrics["strategy_adjustments"]

    def test_early_stage_normal_concession(self, negotiation_service):
        """Test early stage with normal dealer concession"""
        deal = MockDeal(asking_price=25000)
        current_price = 24250  # 3% off
        user_target = 23000
        messages = [MockMessage(1), MockMessage(2)]

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        assert "Early stage" in metrics["strategy_adjustments"]
        assert "strategically" in metrics["strategy_adjustments"]

    def test_zero_round_count_edge_case(self, negotiation_service):
        """Test edge case with empty messages list"""
        deal = MockDeal(asking_price=25000)
        current_price = 23750  # 5% off
        user_target = 23000
        messages = []

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        # Should use max(len(set(...)), 1) to avoid division by zero
        assert metrics["negotiation_velocity"] == 1250.0  # (25000 - 23750) / 1

    def test_zero_asking_price_edge_case(self, negotiation_service):
        """Test edge case with zero asking price"""
        deal = MockDeal(asking_price=0)
        current_price = 100
        user_target = 50
        messages = [MockMessage(1)]

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        # Should handle division by zero gracefully
        assert metrics["dealer_concession_rate"] == 0

    def test_consider_action_with_decent_discount(self, negotiation_service):
        """Test 'consider' recommendation with 8%+ discount"""
        deal = MockDeal(asking_price=25000)
        current_price = 23000  # 8% off
        user_target = 22500  # Target is lower, but getting decent discount
        messages = [MockMessage(1)]

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        assert metrics["recommended_action"] == "consider"

    def test_negotiation_velocity_multiple_rounds(self, negotiation_service):
        """Test negotiation velocity calculation over multiple rounds"""
        deal = MockDeal(asking_price=25000)
        current_price = 22000  # 3000 off
        user_target = 21000
        messages = [MockMessage(1), MockMessage(2), MockMessage(3)]

        metrics = negotiation_service._calculate_ai_metrics(
            session_id=1,
            deal=deal,
            current_price=current_price,
            user_target=user_target,
            messages=messages,
        )

        # 3000 price reduction / 3 rounds = 1000 per round
        assert metrics["negotiation_velocity"] == 1000.0

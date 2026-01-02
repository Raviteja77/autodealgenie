"""
Tests for modular evaluation service components
"""

from unittest.mock import patch

import pytest

from app.core.evaluation_config import EvaluationConfig
from app.llm.schemas import DealEvaluation, VehicleConditionAssessment
from app.services.evaluation.condition import ConditionEvaluator
from app.services.evaluation.financing import FinancingEvaluator
from app.services.evaluation.pricing import PricingEvaluator
from app.services.evaluation.risk import RiskEvaluator


class TestConditionEvaluator:
    """Test ConditionEvaluator module"""

    @pytest.mark.asyncio
    async def test_evaluate_with_llm(self):
        """Test condition evaluation with LLM available"""
        evaluator = ConditionEvaluator()

        mock_assessment = VehicleConditionAssessment(
            condition_score=8.5,
            condition_notes=["Excellent condition", "Well maintained"],
            recommended_inspection=False,
        )

        with patch("app.services.evaluation.condition.llm_client") as mock_client:
            mock_client.is_available.return_value = True

            with patch("app.services.evaluation.condition.generate_structured_json") as mock_gen:
                mock_gen.return_value = mock_assessment

                result = await evaluator.evaluate(
                    make="Honda",
                    model="Accord",
                    year=2020,
                    vin="1HGBH41JXMN109186",
                    mileage=30000,
                    condition_description="excellent condition",
                )

                assert result["condition_score"] == 8.5
                assert len(result["condition_notes"]) == 2
                assert result["recommended_inspection"] is False

    @pytest.mark.asyncio
    async def test_evaluate_fallback(self):
        """Test condition evaluation fallback"""
        evaluator = ConditionEvaluator()

        with patch("app.services.evaluation.condition.llm_client") as mock_client:
            mock_client.is_available.return_value = False

            result = await evaluator.evaluate(
                make="Honda",
                model="Accord",
                year=2020,
                vin="1HGBH41JXMN109186",
                mileage=30000,
                condition_description="good",
            )

            assert result["condition_score"] == 7.0
            assert result["recommended_inspection"] is True
            assert len(result["condition_notes"]) > 0

    def test_get_mileage_assessment(self):
        """Test mileage assessment logic"""
        evaluator = ConditionEvaluator()

        # Exceptionally low
        assessment, adjustment = evaluator.get_mileage_assessment(25000)
        assert "exceptionally low" in assessment
        assert adjustment == EvaluationConfig.MILEAGE_EXCEPTIONALLY_LOW_BONUS

        # Low
        assessment, adjustment = evaluator.get_mileage_assessment(50000)
        assert "low" in assessment
        assert adjustment == EvaluationConfig.MILEAGE_LOW_BONUS

        # Moderate
        assessment, adjustment = evaluator.get_mileage_assessment(80000)
        assert "moderate" in assessment
        assert adjustment == 0.0

        # High
        assessment, adjustment = evaluator.get_mileage_assessment(120000)
        assert "high" in assessment
        assert adjustment == EvaluationConfig.MILEAGE_HIGH_PENALTY

        # Very high
        assessment, adjustment = evaluator.get_mileage_assessment(180000)
        assert "very high" in assessment
        assert adjustment == EvaluationConfig.MILEAGE_VERY_HIGH_PENALTY

    def test_get_condition_adjustment(self):
        """Test condition adjustment logic"""
        evaluator = ConditionEvaluator()

        assert evaluator.get_condition_adjustment("excellent") > 0
        assert evaluator.get_condition_adjustment("like new") > 0
        assert evaluator.get_condition_adjustment("good") > 0
        assert evaluator.get_condition_adjustment("fair") < 0
        assert evaluator.get_condition_adjustment("poor") < 0


class TestPricingEvaluator:
    """Test PricingEvaluator module"""

    @pytest.mark.asyncio
    async def test_evaluate_with_market_data(self):
        """Test pricing evaluation with MarketCheck data"""
        evaluator = PricingEvaluator()

        mock_market_data = {
            "predicted_price": 24000.0,
            "confidence": "high",
            "price_range": {"min": 23000.0, "max": 25000.0},
        }

        mock_evaluation = DealEvaluation(
            fair_value=24000.0,
            score=8.0,
            insights=["Great deal"],
            talking_points=["Strong leverage"],
        )

        with patch.object(evaluator, "_get_market_data", return_value=mock_market_data):
            with patch("app.services.evaluation.pricing.llm_client") as mock_client:
                mock_client.is_available.return_value = True

                with patch("app.services.evaluation.pricing.generate_structured_json") as mock_gen:
                    mock_gen.return_value = mock_evaluation

                    result = await evaluator.evaluate(
                        vehicle_vin="1HGBH41JXMN109186",
                        asking_price=24500.0,
                        condition="good",
                        mileage=50000,
                        make="Honda",
                        model="Accord",
                        year=2020,
                    )

                    assert result["fair_value"] == 24000.0
                    assert result["score"] == 8.0
                    assert "market_data" in result

    @pytest.mark.asyncio
    async def test_heuristic_evaluation(self):
        """Test heuristic evaluation fallback"""
        evaluator = PricingEvaluator()

        result = evaluator._heuristic_evaluation(
            vehicle_vin="1HGBH41JXMN109186",
            asking_price=25000.0,
            condition="excellent",
            mileage=30000,
        )

        assert "fair_value" in result
        assert "score" in result
        assert "insights" in result
        assert "talking_points" in result
        assert 1.0 <= result["score"] <= 10.0

    def test_calculate_price_score(self):
        """Test price score calculation"""
        evaluator = PricingEvaluator()

        # Excellent discount
        score = evaluator._calculate_price_score(-16.0)
        assert score == EvaluationConfig.PRICE_SCORE_EXCELLENT

        # At market
        score = evaluator._calculate_price_score(0.0)
        assert score == EvaluationConfig.PRICE_SCORE_AT_MARKET

        # High premium
        score = evaluator._calculate_price_score(12.0)
        assert score == EvaluationConfig.PRICE_SCORE_HIGH_PREMIUM


class TestFinancingEvaluator:
    """Test FinancingEvaluator module"""

    def test_evaluate_cash(self):
        """Test cash purchase evaluation"""
        evaluator = FinancingEvaluator()

        result = evaluator.evaluate(
            asking_price=25000.0,
            financing_type="cash",
            price_score=8.0,
        )

        assert result["financing_type"] == "cash"
        assert result["monthly_payment"] is None
        assert result["total_cost"] == 25000.0
        assert result["total_interest"] is None
        assert result["affordability_score"] == 10.0
        assert result["recommendation"] == "cash"

    def test_evaluate_loan(self):
        """Test loan financing evaluation"""
        evaluator = FinancingEvaluator()

        result = evaluator.evaluate(
            asking_price=25000.0,
            financing_type="loan",
            price_score=7.0,
            interest_rate=5.0,
            down_payment=5000.0,
            monthly_income=5000.0,
        )

        assert result["financing_type"] == "loan"
        assert result["monthly_payment"] > 0
        assert result["total_cost"] > 25000.0
        assert result["total_interest"] > 0
        assert result["loan_amount"] == 20000.0
        assert 1.0 <= result["affordability_score"] <= 10.0

    def test_affordability_scoring(self):
        """Test affordability score calculation"""
        evaluator = FinancingEvaluator()

        # Excellent affordability (low payment ratio)
        result_excellent = evaluator.evaluate(
            asking_price=20000.0,
            financing_type="loan",
            price_score=7.0,
            interest_rate=4.0,
            down_payment=4000.0,
            monthly_income=10000.0,  # High income, low payment ratio
        )
        assert result_excellent["affordability_score"] >= 7.0

        # Poor affordability (high payment ratio)
        result_poor = evaluator.evaluate(
            asking_price=50000.0,
            financing_type="loan",
            price_score=7.0,
            interest_rate=8.0,
            down_payment=5000.0,
            monthly_income=3000.0,  # Low income, high payment ratio
        )
        assert result_poor["affordability_score"] <= 5.0


class TestRiskEvaluator:
    """Test RiskEvaluator module"""

    def test_evaluate_low_risk(self):
        """Test low risk evaluation"""
        evaluator = RiskEvaluator()

        result = evaluator.evaluate(
            vehicle_year=2022,
            vehicle_mileage=15000,
            asking_price=30000.0,
            fair_value=30000.0,
            inspection_completed=True,
        )

        assert result["risk_score"] < EvaluationConfig.RISK_LOW_THRESHOLD
        assert "Low risk" in result["recommendation"]
        assert len(result["risk_factors"]) == 0

    def test_evaluate_high_risk(self):
        """Test high risk evaluation"""
        evaluator = RiskEvaluator()

        result = evaluator.evaluate(
            vehicle_year=2010,  # Old
            vehicle_mileage=150000,  # High mileage
            asking_price=20000.0,
            fair_value=15000.0,  # Overpriced
            inspection_completed=False,
            recommended_inspection=True,
        )

        assert result["risk_score"] >= EvaluationConfig.RISK_MODERATE_THRESHOLD
        assert len(result["risk_factors"]) > 2

    def test_mileage_risk_factors(self):
        """Test mileage risk scoring"""
        evaluator = RiskEvaluator()

        # High mileage
        result_high = evaluator.evaluate(
            vehicle_year=2018,
            vehicle_mileage=120000,
            asking_price=15000.0,
        )
        assert any("mileage" in factor.lower() for factor in result_high["risk_factors"])

    def test_age_risk_factors(self):
        """Test age risk scoring"""
        evaluator = RiskEvaluator()

        # Old vehicle
        result_old = evaluator.evaluate(
            vehicle_year=2010,
            vehicle_mileage=80000,
            asking_price=10000.0,
        )
        assert any(
            "old" in factor.lower() or "age" in factor.lower()
            for factor in result_old["risk_factors"]
        )


class TestIntegration:
    """Integration tests for orchestrator"""

    @pytest.mark.asyncio
    async def test_orchestrator_integration(self):
        """Test that orchestrator properly delegates to sub-modules"""
        from app.services.evaluation import DealEvaluationService

        service = DealEvaluationService()

        # Verify all sub-modules are initialized
        assert service.condition_evaluator is not None
        assert service.pricing_evaluator is not None
        assert service.financing_evaluator is not None
        assert service.risk_evaluator is not None

        # Verify orchestrator has key methods
        assert hasattr(service, "evaluate_deal")
        assert hasattr(service, "process_evaluation_step")
        assert hasattr(service, "_evaluate_vehicle_condition")
        assert hasattr(service, "_evaluate_price")
        assert hasattr(service, "_evaluate_financing")
        assert hasattr(service, "_evaluate_risk")
        assert hasattr(service, "_evaluate_final")


class TestBackwardCompatibility:
    """Test backward compatibility with old service"""

    @pytest.mark.asyncio
    async def test_singleton_import(self):
        """Test that deal_evaluation_service singleton can be imported"""
        from app.services.evaluation import deal_evaluation_service

        assert deal_evaluation_service is not None
        assert hasattr(deal_evaluation_service, "evaluate_deal")

    def test_config_constants_available(self):
        """Test that configuration constants are accessible"""
        from app.core.evaluation_config import EvaluationConfig

        # Verify key constants exist
        assert hasattr(EvaluationConfig, "MAX_INSIGHTS")
        assert hasattr(EvaluationConfig, "LENDER_RECOMMENDATION_MIN_SCORE")
        assert hasattr(EvaluationConfig, "DEFAULT_LOAN_TERM_MONTHS")
        assert hasattr(EvaluationConfig, "AFFORDABILITY_EXCELLENT")
        assert hasattr(EvaluationConfig, "LOW_INTEREST_RATE")

    @pytest.mark.asyncio
    async def test_evaluate_deal_signature(self):
        """Test that evaluate_deal has the same signature as before"""
        from app.services.evaluation import DealEvaluationService

        service = DealEvaluationService()

        # Check method signature matches old service
        import inspect

        sig = inspect.signature(service.evaluate_deal)
        params = list(sig.parameters.keys())

        # Verify required parameters
        assert "vehicle_vin" in params
        assert "asking_price" in params
        assert "condition" in params
        assert "mileage" in params

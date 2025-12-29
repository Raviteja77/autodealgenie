"""Tests for Agent Orchestrator Service"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.agent_orchestrator import AgentOrchestrator
from app.models.models import Deal
from app.utils.error_handler import ApiError


@pytest.fixture
def mock_db():
    """Mock database session"""
    return MagicMock()


@pytest.fixture
def mock_deal():
    """Mock deal object"""
    deal = MagicMock(spec=Deal)
    deal.id = 1
    deal.vehicle_make = "Toyota"
    deal.vehicle_model = "Camry"
    deal.vehicle_year = 2022
    deal.vehicle_mileage = 25000
    deal.asking_price = 28000.0
    deal.vin = "1HGBH41JXMN109186"
    return deal


@pytest.fixture
def orchestrator(mock_db):
    """Create orchestrator instance"""
    return AgentOrchestrator(mock_db)


@pytest.fixture
def mock_llm_responses():
    """Mock LLM responses for all agents"""
    return {
        "research": {
            "top_vehicles": [
                {
                    "make": "Toyota",
                    "model": "Camry",
                    "year": 2022,
                    "price": 28000.0,
                    "mileage": 25000,
                }
            ],
            "market_summary": "Good market conditions",
        },
        "evaluation": {
            "fair_value": 27000.0,
            "score": 7.5,
            "insights": ["Good mileage", "Fair price"],
            "talking_points": ["Ask for service history"],
        },
        "financing": {
            "recommended_option": {
                "lender_name": "Bank",
                "apr": 4.5,
                "loan_term_months": 60,
                "monthly_payment": 450.0,
                "total_cost": 32000.0,
            },
            "affordability_assessment": {
                "is_affordable": True,
                "notes": ["Payment is affordable"],
            },
        },
        "negotiation": {
            "target_price": 26500.0,
            "opening_offer": 25000.0,
            "walk_away_price": 27500.0,
            "negotiation_summary": "Strong negotiating position",
            "talking_points": ["Reference market value"],
        },
        "qa": {
            "is_valid": True,
            "issues": [],
            "suggested_revision": "",
        },
    }


class TestAgentOrchestrator:
    """Test AgentOrchestrator class"""

    @pytest.mark.asyncio
    async def test_negotiate_deal_not_found(self, orchestrator):
        """Test negotiate_deal with non-existent deal"""
        orchestrator.deal_repo.get = MagicMock(return_value=None)

        with pytest.raises(ApiError) as exc_info:
            await orchestrator.negotiate_deal(deal_id=999, user_context={})

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_negotiate_deal_success(
        self, orchestrator, mock_deal, mock_llm_responses
    ):
        """Test successful orchestrated negotiation"""
        # Mock deal repository
        orchestrator.deal_repo.get = MagicMock(return_value=mock_deal)

        # Mock all agent methods
        with patch.object(
            orchestrator,
            "_research_vehicle",
            new=AsyncMock(return_value=mock_llm_responses["research"]),
        ), patch.object(
            orchestrator,
            "_evaluate_deal",
            new=AsyncMock(return_value=mock_llm_responses["evaluation"]),
        ), patch.object(
            orchestrator,
            "_analyze_financing",
            new=AsyncMock(return_value=mock_llm_responses["financing"]),
        ), patch.object(
            orchestrator,
            "_generate_negotiation_strategy",
            new=AsyncMock(return_value=mock_llm_responses["negotiation"]),
        ), patch.object(
            orchestrator,
            "_qa_review",
            new=AsyncMock(return_value=mock_llm_responses["qa"]),
        ):

            # Execute orchestration
            result = await orchestrator.negotiate_deal(
                deal_id=1,
                user_context={
                    "target_price": 26000.0,
                    "down_payment": 5000.0,
                },
            )

            # Verify result structure
            assert result["deal_id"] == 1
            assert "orchestration_steps" in result
            assert len(result["orchestration_steps"]) == 5

            # Verify all steps completed
            for step in result["orchestration_steps"]:
                assert step["status"] == "completed"

            # Verify agent outputs
            assert result["research"] == mock_llm_responses["research"]
            assert result["evaluation"] == mock_llm_responses["evaluation"]
            assert result["financing"] == mock_llm_responses["financing"]
            assert result["negotiation"] == mock_llm_responses["negotiation"]
            assert result["qa_validation"] == mock_llm_responses["qa"]

            # Verify overall recommendation
            assert "overall_recommendation" in result
            assert result["overall_recommendation"]["decision"] == "RECOMMEND"
            assert result["overall_recommendation"]["confidence"] == "High"

    @pytest.mark.asyncio
    async def test_negotiate_deal_with_agent_failure(self, orchestrator, mock_deal):
        """Test orchestration with agent failure and fallback"""
        # Mock deal repository
        orchestrator.deal_repo.get = MagicMock(return_value=mock_deal)

        # Mock research agent to fail, others to succeed
        with patch.object(
            orchestrator,
            "_research_vehicle",
            new=AsyncMock(side_effect=Exception("LLM error")),
        ), patch.object(
            orchestrator,
            "_evaluate_deal",
            new=AsyncMock(
                return_value={
                    "fair_value": 27000.0,
                    "score": 6.0,
                    "insights": [],
                    "talking_points": [],
                }
            ),
        ), patch.object(
            orchestrator, "_analyze_financing", new=AsyncMock(return_value={})
        ), patch.object(
            orchestrator, "_generate_negotiation_strategy", new=AsyncMock(return_value={})
        ), patch.object(
            orchestrator, "_qa_review", new=AsyncMock(return_value={"is_valid": True})
        ):

            # Execute orchestration
            result = await orchestrator.negotiate_deal(deal_id=1, user_context={})

            # Verify fallback was used for research
            research_step = next(
                s for s in result["orchestration_steps"] if s["step"] == "research"
            )
            assert research_step["status"] == "failed"
            assert "error" in research_step

            # Verify research fallback data
            assert result["research"]["market_summary"] == "Unable to fetch market data"

            # Verify other steps completed
            evaluation_step = next(
                s for s in result["orchestration_steps"] if s["step"] == "evaluation"
            )
            assert evaluation_step["status"] == "completed"

    @pytest.mark.asyncio
    async def test_generate_overall_recommendation_good_deal(self, orchestrator):
        """Test overall recommendation for good deal"""
        orchestration_result = {
            "evaluation": {"score": 8.0, "fair_value": 27000.0},
            "qa_validation": {"is_valid": True, "issues": []},
            "negotiation": {"target_price": 26500.0},
        }

        recommendation = orchestrator._generate_overall_recommendation(orchestration_result)

        assert recommendation["decision"] == "RECOMMEND"
        assert recommendation["confidence"] == "High"
        assert "good deal" in recommendation["summary"].lower()

    @pytest.mark.asyncio
    async def test_generate_overall_recommendation_mediocre_deal(self, orchestrator):
        """Test overall recommendation for mediocre deal"""
        orchestration_result = {
            "evaluation": {"score": 5.5, "fair_value": 28500.0},
            "qa_validation": {"is_valid": True, "issues": []},
            "negotiation": {"target_price": 28000.0},
        }

        recommendation = orchestrator._generate_overall_recommendation(orchestration_result)

        assert recommendation["decision"] == "CONSIDER"
        assert recommendation["confidence"] == "Medium"

    @pytest.mark.asyncio
    async def test_generate_overall_recommendation_poor_deal(self, orchestrator):
        """Test overall recommendation for poor deal"""
        orchestration_result = {
            "evaluation": {"score": 3.0, "fair_value": 22000.0},
            "qa_validation": {"is_valid": False, "issues": ["Price too high"]},
            "negotiation": {"target_price": 24000.0},
        }

        recommendation = orchestrator._generate_overall_recommendation(orchestration_result)

        assert recommendation["decision"] == "NOT_RECOMMENDED"
        assert recommendation["confidence"] == "Low"
        assert "concerns" in recommendation["summary"].lower()

    def test_fallback_research(self, orchestrator, mock_deal):
        """Test fallback research data generation"""
        fallback = orchestrator._fallback_research(mock_deal)

        assert "top_vehicles" in fallback
        assert len(fallback["top_vehicles"]) == 1
        assert fallback["top_vehicles"][0]["make"] == "Toyota"
        assert fallback["market_summary"] == "Unable to fetch market data"

    def test_fallback_evaluation(self, orchestrator, mock_deal):
        """Test fallback evaluation data generation"""
        fallback = orchestrator._fallback_evaluation(mock_deal)

        assert "fair_value" in fallback
        assert "score" in fallback
        assert fallback["score"] == 5.0
        assert "insights" in fallback
        assert "talking_points" in fallback

    def test_fallback_financing(self, orchestrator, mock_deal):
        """Test fallback financing data generation"""
        user_context = {"down_payment": 5000.0}
        fallback = orchestrator._fallback_financing(mock_deal, user_context)

        assert "recommended_option" in fallback
        assert fallback["recommended_option"]["loan_term_months"] == 60
        assert "affordability_assessment" in fallback

    def test_fallback_negotiation(self, orchestrator, mock_deal):
        """Test fallback negotiation data generation"""
        evaluation_data = {"fair_value": 27000.0, "score": 7.0}
        user_context = {}
        fallback = orchestrator._fallback_negotiation(
            mock_deal, evaluation_data, user_context
        )

        assert "target_price" in fallback
        assert "opening_offer" in fallback
        assert "walk_away_price" in fallback
        assert "negotiation_summary" in fallback
        assert "talking_points" in fallback


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

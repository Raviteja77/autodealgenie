"""Tests for AI Response Repository agent tracking enhancements"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.jsonb_data import AIResponse
from app.repositories.ai_response_repository import AIResponseRepository


@pytest.fixture
def mock_db_session():
    """Mock async database session"""
    session = AsyncMock()
    return session


@pytest.fixture
def ai_response_repo(mock_db_session):
    """Create AIResponseRepository instance"""
    return AIResponseRepository(mock_db_session)


@pytest.fixture
def sample_ai_response():
    """Sample AI response record with agent_role"""
    return AIResponse(
        id=1,
        feature="negotiation",
        user_id=1,
        deal_id=1,
        prompt_id="negotiation_initial",
        prompt_variables={"make": "Toyota", "model": "Camry"},
        response_content={"text": "Let's negotiate!"},
        response_metadata={"suggested_price": 25000},
        model_used="gpt-4",
        tokens_used=150,
        temperature=70,
        llm_used=1,
        agent_role="negotiation",
        timestamp=datetime.utcnow(),
    )


class TestAIResponseRepositoryAgentTracking:
    """Test AI Response Repository with agent role tracking"""

    @pytest.mark.asyncio
    async def test_create_response_with_agent_role(self, ai_response_repo, mock_db_session):
        """Test creating AI response with agent_role"""
        # Setup mock
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        # Create response
        await ai_response_repo.create_response(
            feature="negotiation",
            user_id=1,
            deal_id=1,
            prompt_id="negotiation_initial",
            prompt_variables={"make": "Toyota"},
            response_content="Test response",
            agent_role="negotiation",
        )

        # Verify add was called
        assert mock_db_session.add.called

        # Get the added object
        added_obj = mock_db_session.add.call_args[0][0]
        assert added_obj.agent_role == "negotiation"
        assert added_obj.feature == "negotiation"

    @pytest.mark.asyncio
    async def test_create_response_without_agent_role(self, ai_response_repo, mock_db_session):
        """Test creating AI response without agent_role (None)"""
        # Setup mock
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        # Create response without agent_role
        await ai_response_repo.create_response(
            feature="evaluation",
            user_id=1,
            deal_id=1,
            prompt_id="evaluation",
            prompt_variables={},
            response_content="Test response",
            agent_role=None,
        )

        # Get the added object
        added_obj = mock_db_session.add.call_args[0][0]
        assert added_obj.agent_role is None

    @pytest.mark.asyncio
    async def test_get_analytics_by_agent(self, ai_response_repo, mock_db_session):
        """Test get_analytics_by_agent method"""
        # Mock query result with multiple agents
        mock_row_1 = MagicMock()
        mock_row_1.agent_role = "negotiation"
        mock_row_1.feature = "negotiation"
        mock_row_1.count = 10
        mock_row_1.llm_count = 8
        mock_row_1.fallback_count = 2
        mock_row_1.total_tokens = 1500
        mock_row_1.avg_tokens = 150.0

        mock_row_2 = MagicMock()
        mock_row_2.agent_role = "evaluator"
        mock_row_2.feature = "deal_evaluation"
        mock_row_2.count = 15
        mock_row_2.llm_count = 14
        mock_row_2.fallback_count = 1
        mock_row_2.total_tokens = 2100
        mock_row_2.avg_tokens = 140.0

        mock_row_3 = MagicMock()
        mock_row_3.agent_role = "research"
        mock_row_3.feature = "car_recommendation"
        mock_row_3.count = 20
        mock_row_3.llm_count = 20
        mock_row_3.fallback_count = 0
        mock_row_3.total_tokens = 3000
        mock_row_3.avg_tokens = 150.0

        mock_result = MagicMock()
        mock_result.all = MagicMock(return_value=[mock_row_1, mock_row_2, mock_row_3])

        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Call method
        analytics = await ai_response_repo.get_analytics_by_agent(days=30)

        # Verify structure
        assert analytics["period_days"] == 30
        assert "agents" in analytics
        assert len(analytics["agents"]) == 3

        # Verify negotiation agent data
        negotiation_data = analytics["agents"]["negotiation"]
        assert negotiation_data["total_calls"] == 10
        assert negotiation_data["llm_calls"] == 8
        assert negotiation_data["fallback_calls"] == 2
        assert negotiation_data["total_tokens"] == 1500
        assert negotiation_data["avg_tokens"] == 150.0
        assert "features" in negotiation_data
        assert "negotiation" in negotiation_data["features"]

        # Verify evaluator agent data
        evaluator_data = analytics["agents"]["evaluator"]
        assert evaluator_data["total_calls"] == 15
        assert evaluator_data["llm_calls"] == 14
        assert evaluator_data["fallback_calls"] == 1
        assert evaluator_data["total_tokens"] == 2100

        # Verify research agent data
        research_data = analytics["agents"]["research"]
        assert research_data["total_calls"] == 20
        assert research_data["llm_calls"] == 20
        assert research_data["fallback_calls"] == 0
        assert research_data["total_tokens"] == 3000

    @pytest.mark.asyncio
    async def test_get_analytics_by_agent_no_data(self, ai_response_repo, mock_db_session):
        """Test get_analytics_by_agent with no data"""
        # Mock empty result
        mock_result = MagicMock()
        mock_result.all = MagicMock(return_value=[])

        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Call method
        analytics = await ai_response_repo.get_analytics_by_agent(days=7)

        # Verify structure
        assert analytics["period_days"] == 7
        assert "agents" in analytics
        assert len(analytics["agents"]) == 0

    @pytest.mark.asyncio
    async def test_get_analytics_by_agent_multiple_features_per_agent(
        self, ai_response_repo, mock_db_session
    ):
        """Test get_analytics_by_agent with multiple features per agent"""
        # Mock query result with same agent handling multiple features
        mock_row_1 = MagicMock()
        mock_row_1.agent_role = "evaluator"
        mock_row_1.feature = "deal_evaluation"
        mock_row_1.count = 10
        mock_row_1.llm_count = 10
        mock_row_1.fallback_count = 0
        mock_row_1.total_tokens = 1500
        mock_row_1.avg_tokens = 150.0

        mock_row_2 = MagicMock()
        mock_row_2.agent_role = "evaluator"
        mock_row_2.feature = "dealer_info_analysis"
        mock_row_2.count = 5
        mock_row_2.llm_count = 4
        mock_row_2.fallback_count = 1
        mock_row_2.total_tokens = 600
        mock_row_2.avg_tokens = 120.0

        mock_result = MagicMock()
        mock_result.all = MagicMock(return_value=[mock_row_1, mock_row_2])

        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Call method
        analytics = await ai_response_repo.get_analytics_by_agent(days=30)

        # Verify evaluator agent aggregated data
        evaluator_data = analytics["agents"]["evaluator"]
        assert evaluator_data["total_calls"] == 15  # 10 + 5
        assert evaluator_data["llm_calls"] == 14  # 10 + 4
        assert evaluator_data["fallback_calls"] == 1  # 0 + 1
        assert evaluator_data["total_tokens"] == 2100  # 1500 + 600
        assert evaluator_data["avg_tokens"] == 140.0  # 2100 / 15

        # Verify feature-specific data
        assert len(evaluator_data["features"]) == 2
        assert "deal_evaluation" in evaluator_data["features"]
        assert "dealer_info_analysis" in evaluator_data["features"]

        # Verify individual feature data
        deal_eval_data = evaluator_data["features"]["deal_evaluation"]
        assert deal_eval_data["total_calls"] == 10
        assert deal_eval_data["avg_tokens"] == 150.0

        dealer_info_data = evaluator_data["features"]["dealer_info_analysis"]
        assert dealer_info_data["total_calls"] == 5
        assert dealer_info_data["avg_tokens"] == 120.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

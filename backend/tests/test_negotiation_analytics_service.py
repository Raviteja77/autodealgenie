"""
Unit tests for NegotiationAnalyticsService
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import text

from app.services.negotiation_analytics_service import NegotiationAnalyticsService
from app.models.negotiation import NegotiationSession, NegotiationMessage, NegotiationStatus, MessageRole
from app.utils.error_handler import ApiError


class MockDeal:
    """Mock Deal object for testing"""
    def __init__(self, asking_price=25000):
        self.asking_price = asking_price
        self.vehicle_make = "Toyota"
        self.vehicle_model = "Camry"
        self.vehicle_year = 2022
        self.vehicle_mileage = 15000
        self.vehicle_vin = "TEST_VIN_123"


class MockMessage:
    """Mock NegotiationMessage object for testing"""
    def __init__(self, round_number, role="user", metadata=None):
        self.round_number = round_number
        self.role = MessageRole.USER if role == "user" else MessageRole.AGENT
        self.message_metadata = metadata or {}
        self.content = "Test message"


@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    session = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def analytics_service(mock_db_session):
    """Create NegotiationAnalyticsService with mocked dependencies"""
    service = NegotiationAnalyticsService(mock_db_session)
    # Mock the negotiation repo
    service.negotiation_repo = MagicMock()
    return service


class TestCalculateSuccessProbability:
    """Tests for calculate_success_probability method"""

    @pytest.mark.asyncio
    async def test_calculate_success_probability_high(self, analytics_service):
        """Test success probability calculation for favorable negotiation"""
        # Mock session
        mock_session = MagicMock()
        mock_session.id = 1
        mock_session.current_round = 2
        mock_session.max_rounds = 10
        analytics_service.negotiation_repo.get_session = AsyncMock(return_value=mock_session)
        
        # Mock messages
        messages = [MockMessage(1), MockMessage(2)]
        analytics_service.negotiation_repo.get_messages = AsyncMock(return_value=messages)
        
        # Mock similar sessions (mostly successful)
        analytics_service._find_similar_sessions = AsyncMock(
            return_value=[
                {"session_id": 2, "status": "completed", "rounds": 3, "similarity": 0.85},
                {"session_id": 3, "status": "completed", "rounds": 4, "similarity": 0.80},
                {"session_id": 4, "status": "completed", "rounds": 5, "similarity": 0.75},
            ]
        )
        
        # Mock analytics storage
        analytics_service._store_analytics = AsyncMock()
        
        result = await analytics_service.calculate_success_probability(
            session_id=1,
            current_price=22000,  # Close to target
            user_target_price=22000,
            asking_price=25000,
        )
        
        assert "success_probability" in result
        assert result["success_probability"] > 0.5  # Should be high
        assert result["confidence_level"] in ["high", "medium", "low"]
        assert "key_factors" in result
        assert "recommendation" in result
        assert result["similar_sessions_count"] == 3

    @pytest.mark.asyncio
    async def test_calculate_success_probability_low(self, analytics_service):
        """Test success probability calculation for unfavorable negotiation"""
        mock_session = MagicMock()
        mock_session.id = 1
        mock_session.current_round = 8
        mock_session.max_rounds = 10
        analytics_service.negotiation_repo.get_session = AsyncMock(return_value=mock_session)
        
        messages = [MockMessage(i) for i in range(1, 9)]
        analytics_service.negotiation_repo.get_messages = AsyncMock(return_value=messages)
        
        # Mock similar sessions (mostly failed)
        analytics_service._find_similar_sessions = AsyncMock(
            return_value=[
                {"session_id": 2, "status": "cancelled", "rounds": 8, "similarity": 0.75},
                {"session_id": 3, "status": "cancelled", "rounds": 9, "similarity": 0.70},
            ]
        )
        
        analytics_service._store_analytics = AsyncMock()
        
        result = await analytics_service.calculate_success_probability(
            session_id=1,
            current_price=24500,  # Far from target
            user_target_price=21000,
            asking_price=25000,
        )
        
        assert result["success_probability"] <= 0.5  # Should be low
        assert result["similar_sessions_count"] == 2

    @pytest.mark.asyncio
    async def test_calculate_success_probability_session_not_found(self, analytics_service):
        """Test handling of non-existent session"""
        analytics_service.negotiation_repo.get_session = AsyncMock(return_value=None)
        
        with pytest.raises(ApiError) as exc_info:
            await analytics_service.calculate_success_probability(
                session_id=999,
                current_price=22000,
                user_target_price=22000,
                asking_price=25000,
            )
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_calculate_success_probability_fallback(self, analytics_service):
        """Test fallback when ML analysis fails"""
        mock_session = MagicMock()
        mock_session.id = 1
        mock_session.current_round = 3
        mock_session.max_rounds = 10
        analytics_service.negotiation_repo.get_session = AsyncMock(return_value=mock_session)
        analytics_service.negotiation_repo.get_messages = AsyncMock(
            side_effect=Exception("Database error")
        )
        
        # Should return fallback without raising
        result = await analytics_service.calculate_success_probability(
            session_id=1,
            current_price=22000,
            user_target_price=22000,
            asking_price=25000,
        )
        
        assert result["success_probability"] == 0.5
        assert result["confidence_level"] == "low"


class TestGetOptimalCounterOffer:
    """Tests for get_optimal_counter_offer method"""

    @pytest.mark.asyncio
    async def test_get_optimal_counter_offer_success(self, analytics_service):
        """Test optimal counter-offer calculation"""
        mock_session = MagicMock()
        mock_session.id = 1
        mock_session.current_round = 3
        mock_session.max_rounds = 10
        analytics_service.negotiation_repo.get_session = AsyncMock(return_value=mock_session)
        
        messages = [MockMessage(i) for i in range(1, 4)]
        analytics_service.negotiation_repo.get_messages = AsyncMock(return_value=messages)
        
        # Mock similar sessions
        analytics_service._find_similar_sessions = AsyncMock(
            return_value=[
                {"session_id": 2, "status": "completed", "rounds": 4, "similarity": 0.85},
            ]
        )
        
        result = await analytics_service.get_optimal_counter_offer(
            session_id=1,
            current_offer=23000,
            user_target_price=21000,
            asking_price=25000,
        )
        
        assert "optimal_offer" in result
        assert result["optimal_offer"] >= 21000  # Should not go below target
        assert result["optimal_offer"] <= 23000  # Should not go above current
        assert "rationale" in result
        assert "expected_savings" in result
        assert "risk_assessment" in result
        assert result["risk_assessment"] in ["low", "medium", "high"]

    @pytest.mark.asyncio
    async def test_get_optimal_counter_offer_early_round(self, analytics_service):
        """Test optimal offer in early negotiation rounds"""
        mock_session = MagicMock()
        mock_session.id = 1
        mock_session.current_round = 1
        mock_session.max_rounds = 10
        analytics_service.negotiation_repo.get_session = AsyncMock(return_value=mock_session)
        
        messages = [MockMessage(1)]
        analytics_service.negotiation_repo.get_messages = AsyncMock(return_value=messages)
        analytics_service._find_similar_sessions = AsyncMock(return_value=[])
        
        result = await analytics_service.get_optimal_counter_offer(
            session_id=1,
            current_offer=24000,
            user_target_price=21000,
            asking_price=25000,
        )
        
        # Early round should suggest more aggressive move
        assert result["optimal_offer"] < 24000
        assert result["risk_assessment"] in ["low", "medium"]

    @pytest.mark.asyncio
    async def test_get_optimal_counter_offer_late_round(self, analytics_service):
        """Test optimal offer in late negotiation rounds"""
        mock_session = MagicMock()
        mock_session.id = 1
        mock_session.current_round = 9
        mock_session.max_rounds = 10
        analytics_service.negotiation_repo.get_session = AsyncMock(return_value=mock_session)
        
        messages = [MockMessage(i) for i in range(1, 10)]
        analytics_service.negotiation_repo.get_messages = AsyncMock(return_value=messages)
        analytics_service._find_similar_sessions = AsyncMock(return_value=[])
        
        result = await analytics_service.get_optimal_counter_offer(
            session_id=1,
            current_offer=22500,
            user_target_price=21000,
            asking_price=25000,
        )
        
        # Late round should be more conservative
        assert result["optimal_offer"] >= 21000

    @pytest.mark.asyncio
    async def test_get_optimal_counter_offer_fallback(self, analytics_service):
        """Test fallback when calculation fails"""
        mock_session = MagicMock()
        mock_session.id = 1
        mock_session.current_round = 3
        mock_session.max_rounds = 10
        analytics_service.negotiation_repo.get_session = AsyncMock(return_value=mock_session)
        analytics_service.negotiation_repo.get_messages = AsyncMock(
            side_effect=Exception("Error")
        )
        
        result = await analytics_service.get_optimal_counter_offer(
            session_id=1,
            current_offer=23000,
            user_target_price=21000,
            asking_price=25000,
        )
        
        # Should return conservative fallback (midpoint)
        expected_fallback = (23000 + 21000) / 2
        assert result["optimal_offer"] == expected_fallback
        assert "insufficient" in result["rationale"].lower()


class TestAnalyzeNegotiationPatterns:
    """Tests for analyze_negotiation_patterns method"""

    @pytest.mark.asyncio
    async def test_analyze_negotiation_patterns_success(self, analytics_service):
        """Test pattern analysis"""
        mock_session = MagicMock()
        mock_session.id = 1
        analytics_service.negotiation_repo.get_session = AsyncMock(return_value=mock_session)
        
        # Mock messages with price metadata
        messages = [
            MockMessage(1, "user", {"counter_offer": 21000}),
            MockMessage(1, "agent", {"suggested_price": 23000}),
            MockMessage(2, "user", {"counter_offer": 22000}),
            MockMessage(2, "agent", {"suggested_price": 22500}),
        ]
        analytics_service.negotiation_repo.get_messages = AsyncMock(return_value=messages)
        analytics_service._find_similar_sessions = AsyncMock(return_value=[])
        
        result = await analytics_service.analyze_negotiation_patterns(session_id=1)
        
        assert "negotiation_velocity" in result
        assert result["negotiation_velocity"] in ["fast", "moderate", "slow", "unknown"]
        assert "dealer_flexibility" in result
        assert "user_style" in result
        assert "predicted_outcome" in result
        assert "insights" in result
        assert isinstance(result["insights"], list)

    @pytest.mark.asyncio
    async def test_analyze_patterns_fast_velocity(self, analytics_service):
        """Test pattern analysis with fast negotiation velocity"""
        mock_session = MagicMock()
        mock_session.id = 1
        analytics_service.negotiation_repo.get_session = AsyncMock(return_value=mock_session)
        
        # Messages with large price changes
        messages = [
            MockMessage(1, "user", {"counter_offer": 20000}),
            MockMessage(1, "agent", {"suggested_price": 23000}),
            MockMessage(2, "user", {"counter_offer": 21500}),
            MockMessage(2, "agent", {"suggested_price": 22000}),
        ]
        analytics_service.negotiation_repo.get_messages = AsyncMock(return_value=messages)
        analytics_service._find_similar_sessions = AsyncMock(return_value=[])
        
        result = await analytics_service.analyze_negotiation_patterns(session_id=1)
        
        assert result["negotiation_velocity"] == "fast"


class TestVectorSimilaritySearch:
    """Tests for vector similarity search functionality"""

    @pytest.mark.asyncio
    async def test_find_similar_sessions_with_results(self, analytics_service):
        """Test finding similar sessions"""
        mock_session = MagicMock()
        mock_session.id = 1
        mock_session.status = NegotiationStatus.ACTIVE
        mock_session.current_round = 3
        mock_session.max_rounds = 10
        analytics_service.negotiation_repo.get_session = AsyncMock(return_value=mock_session)
        
        messages = [MockMessage(i) for i in range(1, 4)]
        analytics_service.negotiation_repo.get_messages = AsyncMock(return_value=messages)
        
        # Mock embedding generation
        analytics_service._generate_embedding = AsyncMock(
            return_value=[0.1] * 1536  # Mock embedding vector
        )
        
        # Mock database query results
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (2, "completed", 4, "2024-01-01", 0.85),
            (3, "completed", 5, "2024-01-02", 0.80),
        ]
        analytics_service.db.execute = AsyncMock(return_value=mock_result)
        
        similar_sessions = await analytics_service._find_similar_sessions(
            session_id=1,
            asking_price=25000,
            current_price=22000,
            limit=10,
        )
        
        assert len(similar_sessions) == 2
        assert similar_sessions[0]["session_id"] == 2
        assert similar_sessions[0]["status"] == "completed"
        assert similar_sessions[0]["similarity"] == 0.85

    @pytest.mark.asyncio
    async def test_find_similar_sessions_no_openai(self, analytics_service):
        """Test similarity search when OpenAI is unavailable"""
        analytics_service.openai_client = None
        
        similar_sessions = await analytics_service._find_similar_sessions(
            session_id=1,
            asking_price=25000,
            current_price=22000,
            limit=10,
        )
        
        # Should return empty list gracefully
        assert similar_sessions == []

    @pytest.mark.asyncio
    async def test_find_similar_sessions_db_error(self, analytics_service):
        """Test handling of database errors in similarity search"""
        mock_session = MagicMock()
        mock_session.id = 1
        analytics_service.negotiation_repo.get_session = AsyncMock(return_value=mock_session)
        analytics_service.negotiation_repo.get_messages = AsyncMock(return_value=[])
        analytics_service._generate_embedding = AsyncMock(return_value=[0.1] * 1536)
        
        # Mock database error
        analytics_service.db.execute = AsyncMock(side_effect=Exception("DB error"))
        
        similar_sessions = await analytics_service._find_similar_sessions(
            session_id=1,
            asking_price=25000,
            current_price=22000,
            limit=10,
        )
        
        # Should return empty list on error
        assert similar_sessions == []


class TestHelperMethods:
    """Tests for internal helper methods"""

    def test_calculate_base_probability_near_target(self, analytics_service):
        """Test base probability when close to target"""
        prob = analytics_service._calculate_base_probability(
            current_price=22000,
            user_target_price=22000,
            asking_price=25000,
            current_round=2,
            max_rounds=10,
        )
        
        assert prob > 0.5  # Should be high when at target

    def test_calculate_base_probability_far_from_target(self, analytics_service):
        """Test base probability when far from target"""
        prob = analytics_service._calculate_base_probability(
            current_price=24500,
            user_target_price=20000,
            asking_price=25000,
            current_round=8,
            max_rounds=10,
        )
        
        assert prob < 0.5  # Should be low when far from target

    def test_determine_confidence_level_high(self, analytics_service):
        """Test confidence level determination - high"""
        confidence = analytics_service._determine_confidence_level(
            similar_sessions_count=15,
            probability=0.85,
        )
        
        assert confidence == "high"

    def test_determine_confidence_level_medium(self, analytics_service):
        """Test confidence level determination - medium"""
        confidence = analytics_service._determine_confidence_level(
            similar_sessions_count=7,
            probability=0.55,
        )
        
        assert confidence == "medium"

    def test_determine_confidence_level_low(self, analytics_service):
        """Test confidence level determination - low"""
        confidence = analytics_service._determine_confidence_level(
            similar_sessions_count=2,
            probability=0.45,
        )
        
        assert confidence == "low"

    def test_calculate_negotiation_velocity_fast(self, analytics_service):
        """Test velocity calculation - fast"""
        messages = [
            MockMessage(1, "agent", {"suggested_price": 25000}),
            MockMessage(1, "user", {"counter_offer": 22000}),
            MockMessage(2, "agent", {"suggested_price": 23000}),
        ]
        
        velocity = analytics_service._calculate_negotiation_velocity(messages)
        assert velocity == "fast"

    def test_calculate_negotiation_velocity_slow(self, analytics_service):
        """Test velocity calculation - slow"""
        messages = [
            MockMessage(1, "agent", {"suggested_price": 25000}),
            MockMessage(1, "user", {"counter_offer": 24900}),
            MockMessage(2, "agent", {"suggested_price": 24850}),
        ]
        
        velocity = analytics_service._calculate_negotiation_velocity(messages)
        assert velocity == "slow"

    def test_determine_user_style_aggressive(self, analytics_service):
        """Test user style determination - aggressive"""
        messages = [
            MockMessage(1, "user", {"counter_offer": 20000}),
            MockMessage(2, "user", {"counter_offer": 19000}),
            MockMessage(3, "user", {"counter_offer": 18500}),
        ]
        
        style = analytics_service._determine_user_style(messages)
        assert style == "aggressive"

    def test_determine_user_style_conservative(self, analytics_service):
        """Test user style determination - conservative"""
        messages = [
            MockMessage(1, "user", {"counter_offer": 24500}),
            MockMessage(2, "user", {"counter_offer": 24400}),
            MockMessage(3, "user", {"counter_offer": 24350}),
        ]
        
        style = analytics_service._determine_user_style(messages)
        assert style == "conservative"

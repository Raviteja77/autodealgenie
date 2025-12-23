"""Test negotiation endpoints and services"""

from unittest.mock import patch

import pytest

from app.api.dependencies import get_current_user
from app.models.models import Deal, DealStatus, User
from app.models.negotiation import MessageRole, NegotiationStatus
from app.repositories.negotiation_repository import NegotiationRepository


@pytest.fixture
def mock_user(db):
    """Create a mock user for testing"""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password="hashed",
        full_name="Test User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def mock_deal(db):
    """Create a mock deal for testing"""
    deal = Deal(
        customer_name="John Doe",
        customer_email="john@example.com",
        vehicle_make="Toyota",
        vehicle_model="Camry",
        vehicle_year=2022,
        vehicle_mileage=15000,
        asking_price=25000.00,
        status=DealStatus.PENDING,
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return deal


@pytest.fixture
def authenticated_client(client, mock_user):
    """Override the get_current_user dependency to return mock user"""
    from app.main import app

    def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def negotiation_repo(db):
    """Create a negotiation repository instance"""
    return NegotiationRepository(db)


# Repository Tests


def test_create_negotiation_session(negotiation_repo, mock_user, mock_deal):
    """Test creating a negotiation session"""
    session = negotiation_repo.create_session(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        max_rounds=10,
    )

    assert session.id is not None
    assert session.user_id == mock_user.id
    assert session.deal_id == mock_deal.id
    assert session.status == NegotiationStatus.ACTIVE
    assert session.current_round == 1
    assert session.max_rounds == 10


def test_get_negotiation_session_repo(negotiation_repo, mock_user, mock_deal):
    """Test retrieving a negotiation session"""
    session = negotiation_repo.create_session(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
    )

    retrieved = negotiation_repo.get_session(session.id)
    assert retrieved is not None
    assert retrieved.id == session.id
    assert retrieved.user_id == mock_user.id


def test_get_nonexistent_session(negotiation_repo):
    """Test getting a non-existent session"""
    session = negotiation_repo.get_session(99999)
    assert session is None


def test_update_session_status(negotiation_repo, mock_user, mock_deal):
    """Test updating session status"""
    session = negotiation_repo.create_session(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
    )

    updated = negotiation_repo.update_session_status(session.id, NegotiationStatus.COMPLETED)
    assert updated is not None
    assert updated.status == NegotiationStatus.COMPLETED


def test_increment_round(negotiation_repo, mock_user, mock_deal):
    """Test incrementing negotiation round"""
    session = negotiation_repo.create_session(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
    )

    assert session.current_round == 1

    updated = negotiation_repo.increment_round(session.id)
    assert updated.current_round == 2


def test_add_message(negotiation_repo, mock_user, mock_deal):
    """Test adding a message to a session"""
    session = negotiation_repo.create_session(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
    )

    message = negotiation_repo.add_message(
        session_id=session.id,
        role=MessageRole.USER,
        content="I want to negotiate the price",
        round_number=1,
        metadata={"target_price": 20000},
    )

    assert message.id is not None
    assert message.session_id == session.id
    assert message.role == MessageRole.USER
    assert message.content == "I want to negotiate the price"
    assert message.round_number == 1
    assert message.message_metadata == {"target_price": 20000}


def test_get_messages(negotiation_repo, mock_user, mock_deal):
    """Test retrieving messages for a session"""
    session = negotiation_repo.create_session(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
    )

    # Add multiple messages
    negotiation_repo.add_message(
        session_id=session.id,
        role=MessageRole.USER,
        content="First message",
        round_number=1,
    )
    negotiation_repo.add_message(
        session_id=session.id,
        role=MessageRole.AGENT,
        content="Second message",
        round_number=1,
    )

    messages = negotiation_repo.get_messages(session.id)
    assert len(messages) == 2
    assert messages[0].content == "First message"
    assert messages[1].content == "Second message"


def test_get_latest_message(negotiation_repo, mock_user, mock_deal):
    """Test getting the latest message"""
    session = negotiation_repo.create_session(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
    )

    negotiation_repo.add_message(
        session_id=session.id,
        role=MessageRole.USER,
        content="First message",
        round_number=1,
    )
    negotiation_repo.add_message(
        session_id=session.id,
        role=MessageRole.AGENT,
        content="Latest message",
        round_number=1,
    )

    latest = negotiation_repo.get_latest_message(session.id)
    assert latest is not None
    assert latest.content == "Latest message"


def test_delete_session(negotiation_repo, mock_user, mock_deal):
    """Test deleting a negotiation session"""
    session = negotiation_repo.create_session(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
    )

    # Add a message
    negotiation_repo.add_message(
        session_id=session.id,
        role=MessageRole.USER,
        content="Test message",
        round_number=1,
    )

    # Delete session (should cascade delete messages)
    deleted = negotiation_repo.delete_session(session.id)
    assert deleted is True

    # Verify session is gone
    retrieved = negotiation_repo.get_session(session.id)
    assert retrieved is None


# Endpoint Tests


@pytest.mark.asyncio
async def test_create_negotiation_endpoint(authenticated_client, mock_deal):
    """Test creating a negotiation via API endpoint"""
    request_data = {
        "deal_id": mock_deal.id,
        "user_target_price": 22000.00,
        "strategy": "moderate",
    }

    with patch(
        "app.services.negotiation_service.langchain_service.generate_customer_response"
    ) as mock_llm:
        mock_llm.return_value = "Thank you for your interest. Let's find a fair price."

        response = authenticated_client.post("/api/v1/negotiations/", json=request_data)

        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert data["status"] == "active"
        assert data["current_round"] == 1
        assert "agent_message" in data


@pytest.mark.asyncio
async def test_create_negotiation_invalid_deal(authenticated_client):
    """Test creating negotiation with invalid deal ID"""
    request_data = {
        "deal_id": 99999,
        "user_target_price": 22000.00,
    }

    response = authenticated_client.post("/api/v1/negotiations/", json=request_data)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_process_next_round_counter(authenticated_client, mock_deal, db):
    """Test processing next round with counter offer"""
    from app.models.models import User
    from app.repositories.negotiation_repository import NegotiationRepository

    # Get the mock user
    user = db.query(User).filter(User.email == "testuser@example.com").first()

    # Create a session
    repo = NegotiationRepository(db)
    session = repo.create_session(user_id=user.id, deal_id=mock_deal.id)

    # Add initial message
    repo.add_message(
        session_id=session.id,
        role=MessageRole.USER,
        content="Initial message",
        round_number=1,
    )

    request_data = {"user_action": "counter", "counter_offer": 23000.00}

    with patch(
        "app.services.negotiation_service.langchain_service.generate_customer_response"
    ) as mock_llm:
        mock_llm.return_value = "I appreciate your offer. How about we meet in the middle?"

        response = authenticated_client.post(
            f"/api/v1/negotiations/{session.id}/next", json=request_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session.id
        assert data["status"] == "active"
        assert data["current_round"] == 2
        assert "agent_message" in data


@pytest.mark.asyncio
async def test_process_next_round_confirm(authenticated_client, mock_deal, db):
    """Test processing next round with confirm action and verify deal update"""
    from app.models.models import User
    from app.repositories.deal_repository import DealRepository
    from app.repositories.negotiation_repository import NegotiationRepository

    user = db.query(User).filter(User.email == "testuser@example.com").first()
    repo = NegotiationRepository(db)
    session = repo.create_session(user_id=user.id, deal_id=mock_deal.id)

    # Add a message with a suggested price to simulate negotiation
    repo.add_message(
        session_id=session.id,
        role=MessageRole.AGENT,
        content="I can offer $23,500 for this vehicle.",
        round_number=1,
        metadata={"suggested_price": 23500.00},
    )

    request_data = {"user_action": "confirm"}

    response = authenticated_client.post(
        f"/api/v1/negotiations/{session.id}/next", json=request_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"

    # Verify deal was updated with negotiated price and status
    deal_repo = DealRepository(db)
    updated_deal = deal_repo.get(mock_deal.id)
    assert updated_deal is not None
    assert updated_deal.status == "completed"
    assert updated_deal.offer_price == 23500.00
    assert "Negotiation completed" in (updated_deal.notes or "")


@pytest.mark.asyncio
async def test_process_next_round_reject(authenticated_client, mock_deal, db):
    """Test processing next round with reject action"""
    from app.models.models import User
    from app.repositories.negotiation_repository import NegotiationRepository

    user = db.query(User).filter(User.email == "testuser@example.com").first()
    repo = NegotiationRepository(db)
    session = repo.create_session(user_id=user.id, deal_id=mock_deal.id)

    request_data = {"user_action": "reject"}

    response = authenticated_client.post(
        f"/api/v1/negotiations/{session.id}/next", json=request_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"


@pytest.mark.asyncio
async def test_get_negotiation_session(authenticated_client, mock_deal, db):
    """Test retrieving a negotiation session"""
    from app.models.models import User
    from app.repositories.negotiation_repository import NegotiationRepository

    user = db.query(User).filter(User.email == "testuser@example.com").first()
    repo = NegotiationRepository(db)
    session = repo.create_session(user_id=user.id, deal_id=mock_deal.id)

    # Add messages
    repo.add_message(
        session_id=session.id,
        role=MessageRole.USER,
        content="User message",
        round_number=1,
    )
    repo.add_message(
        session_id=session.id,
        role=MessageRole.AGENT,
        content="Agent response",
        round_number=1,
    )

    response = authenticated_client.get(f"/api/v1/negotiations/{session.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session.id
    assert data["user_id"] == user.id
    assert data["deal_id"] == mock_deal.id
    assert len(data["messages"]) == 2


def test_get_nonexistent_negotiation(authenticated_client):
    """Test getting a non-existent negotiation session"""
    response = authenticated_client.get("/api/v1/negotiations/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_access_other_user_session(authenticated_client, mock_deal, db):
    """Test that users cannot access other users' sessions"""
    from app.models.models import User
    from app.repositories.negotiation_repository import NegotiationRepository

    # Create another user
    other_user = User(
        email="other@example.com",
        username="otheruser",
        hashed_password="hashed",
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    # Create session for other user
    repo = NegotiationRepository(db)
    session = repo.create_session(user_id=other_user.id, deal_id=mock_deal.id)

    # Try to access with authenticated client (different user)
    response = authenticated_client.get(f"/api/v1/negotiations/{session.id}")
    assert response.status_code == 403


# Chat Message Tests


@pytest.mark.asyncio
async def test_send_chat_message(authenticated_client, mock_deal, db):
    """Test sending a free-form chat message"""
    from app.models.models import User
    from app.repositories.negotiation_repository import NegotiationRepository

    # Get the mock user
    user = db.query(User).filter(User.email == "testuser@example.com").first()

    # Create a session
    repo = NegotiationRepository(db)
    session = repo.create_session(user_id=user.id, deal_id=mock_deal.id)

    request_data = {
        "message": "What's the best strategy for negotiating this price?",
        "message_type": "question",
    }

    with patch("app.llm.llm_client.async_openai_client.chat.completions.create") as mock_llm:
        # Mock LLM response
        mock_response = type(
            "MockResponse",
            (),
            {
                "choices": [
                    type(
                        "MockChoice",
                        (),
                        {
                            "message": type(
                                "MockMessage",
                                (),
                                {
                                    "content": "Based on the current market conditions, I recommend starting with a counter offer that's 5-8% below the asking price."
                                },
                            )()
                        },
                    )()
                ]
            },
        )()
        mock_llm.return_value = mock_response

        response = authenticated_client.post(
            f"/api/v1/negotiations/{session.id}/chat", json=request_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session.id
        assert "user_message" in data
        assert "agent_message" in data
        assert data["user_message"]["content"] == request_data["message"]
        assert data["user_message"]["metadata"]["message_type"] == "question"
        assert data["agent_message"]["role"] == "agent"


@pytest.mark.asyncio
async def test_send_chat_message_invalid_session(authenticated_client):
    """Test sending chat message to non-existent session"""
    request_data = {
        "message": "Test message",
        "message_type": "general",
    }

    response = authenticated_client.post("/api/v1/negotiations/99999/chat", json=request_data)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_send_chat_message_validation(authenticated_client, mock_deal, db):
    """Test chat message validation"""
    from app.models.models import User
    from app.repositories.negotiation_repository import NegotiationRepository

    # Get the mock user
    user = db.query(User).filter(User.email == "testuser@example.com").first()

    # Create a session
    repo = NegotiationRepository(db)
    session = repo.create_session(user_id=user.id, deal_id=mock_deal.id)

    # Test with empty message
    request_data = {"message": "", "message_type": "general"}
    response = authenticated_client.post(
        f"/api/v1/negotiations/{session.id}/chat", json=request_data
    )
    assert response.status_code == 422

    # Test with too long message
    request_data = {"message": "x" * 2001, "message_type": "general"}
    response = authenticated_client.post(
        f"/api/v1/negotiations/{session.id}/chat", json=request_data
    )
    assert response.status_code == 422


# Dealer Info Analysis Tests


@pytest.mark.asyncio
async def test_submit_dealer_info(authenticated_client, mock_deal, db):
    """Test submitting dealer-provided information"""
    from app.models.models import User
    from app.repositories.negotiation_repository import NegotiationRepository

    # Get the mock user
    user = db.query(User).filter(User.email == "testuser@example.com").first()

    # Create a session
    repo = NegotiationRepository(db)
    session = repo.create_session(user_id=user.id, deal_id=mock_deal.id)

    request_data = {
        "info_type": "price_quote",
        "content": "Dealer says they can do $23,500 if I finance through them",
        "price_mentioned": 23500.00,
        "metadata": {"financing_required": True},
    }

    with patch("app.llm.llm_client.async_openai_client.chat.completions.create") as mock_llm:
        # Mock LLM response
        mock_response = type(
            "MockResponse",
            (),
            {
                "choices": [
                    type(
                        "MockChoice",
                        (),
                        {
                            "message": type(
                                "MockMessage",
                                (),
                                {
                                    "content": "This dealer offer of $23,500 with financing is reasonable. However, be aware that dealer financing might have higher interest rates. I recommend comparing it with your bank's rates."
                                },
                            )()
                        },
                    )()
                ]
            },
        )()
        mock_llm.return_value = mock_response

        response = authenticated_client.post(
            f"/api/v1/negotiations/{session.id}/dealer-info", json=request_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session.id
        assert "analysis" in data
        assert "recommended_action" in data
        assert "user_message" in data
        assert "agent_message" in data
        assert data["user_message"]["metadata"]["info_type"] == "price_quote"
        assert data["user_message"]["metadata"]["price_mentioned"] == 23500.00


@pytest.mark.asyncio
async def test_submit_dealer_info_inactive_session(authenticated_client, mock_deal, db):
    """Test submitting dealer info to inactive session"""
    from app.models.models import User
    from app.models.negotiation import NegotiationStatus
    from app.repositories.negotiation_repository import NegotiationRepository

    # Get the mock user
    user = db.query(User).filter(User.email == "testuser@example.com").first()

    # Create a completed session
    repo = NegotiationRepository(db)
    session = repo.create_session(user_id=user.id, deal_id=mock_deal.id)
    repo.update_session_status(session.id, NegotiationStatus.COMPLETED)

    request_data = {
        "info_type": "price_quote",
        "content": "Test content",
        "price_mentioned": 23000.00,
    }

    response = authenticated_client.post(
        f"/api/v1/negotiations/{session.id}/dealer-info", json=request_data
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_submit_dealer_info_validation(authenticated_client, mock_deal, db):
    """Test dealer info validation"""
    from app.models.models import User
    from app.repositories.negotiation_repository import NegotiationRepository

    # Get the mock user
    user = db.query(User).filter(User.email == "testuser@example.com").first()

    # Create a session
    repo = NegotiationRepository(db)
    session = repo.create_session(user_id=user.id, deal_id=mock_deal.id)

    # Test with empty content
    request_data = {"info_type": "price_quote", "content": ""}
    response = authenticated_client.post(
        f"/api/v1/negotiations/{session.id}/dealer-info", json=request_data
    )
    assert response.status_code == 422

    # Test with too long content
    request_data = {"info_type": "price_quote", "content": "x" * 5001}
    response = authenticated_client.post(
        f"/api/v1/negotiations/{session.id}/dealer-info", json=request_data
    )
    assert response.status_code == 422

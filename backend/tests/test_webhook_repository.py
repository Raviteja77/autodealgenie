"""
Tests for webhook repository
"""

from unittest.mock import MagicMock

import pytest

from app.models.models import WebhookStatus, WebhookSubscription
from app.repositories.webhook_repository import WebhookRepository


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return MagicMock()


def test_create_webhook_subscription(mock_db):
    """Test creating a webhook subscription"""
    repo = WebhookRepository(mock_db)

    subscription_data = {
        "user_id": 1,
        "webhook_url": "https://example.com/webhook",
        "status": WebhookStatus.ACTIVE,
        "make": "Toyota",
        "model": "RAV4",
        "price_min": 20000,
        "price_max": 30000,
    }

    WebhookSubscription(**subscription_data)
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    # Mock the refresh to set ID
    def refresh_side_effect(obj):
        obj.id = 1

    mock_db.refresh.side_effect = refresh_side_effect

    repo.create(subscription_data)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_get_webhook_by_id(mock_db):
    """Test retrieving webhook subscription by ID"""
    repo = WebhookRepository(mock_db)

    mock_subscription = WebhookSubscription(
        id=1, user_id=1, webhook_url="https://example.com/webhook", status=WebhookStatus.ACTIVE
    )

    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_subscription
    mock_db.query.return_value = mock_query

    subscription = repo.get_by_id(1)

    assert subscription is not None
    assert subscription.id == 1
    assert subscription.webhook_url == "https://example.com/webhook"


def test_get_webhooks_by_user(mock_db):
    """Test retrieving all webhook subscriptions for a user"""
    repo = WebhookRepository(mock_db)

    mock_subscriptions = [
        WebhookSubscription(
            id=1, user_id=1, webhook_url="https://example.com/webhook1", status=WebhookStatus.ACTIVE
        ),
        WebhookSubscription(
            id=2, user_id=1, webhook_url="https://example.com/webhook2", status=WebhookStatus.ACTIVE
        ),
    ]

    mock_query = MagicMock()
    mock_query.filter.return_value.all.return_value = mock_subscriptions
    mock_db.query.return_value = mock_query

    subscriptions = repo.get_by_user(1)

    assert len(subscriptions) == 2
    assert all(sub.user_id == 1 for sub in subscriptions)


def test_get_active_subscriptions(mock_db):
    """Test retrieving all active webhook subscriptions"""
    repo = WebhookRepository(mock_db)

    mock_subscriptions = [
        WebhookSubscription(
            id=1, user_id=1, webhook_url="https://example.com/webhook1", status=WebhookStatus.ACTIVE
        ),
        WebhookSubscription(
            id=2, user_id=2, webhook_url="https://example.com/webhook2", status=WebhookStatus.ACTIVE
        ),
    ]

    mock_query = MagicMock()
    mock_query.filter.return_value.all.return_value = mock_subscriptions
    mock_db.query.return_value = mock_query

    subscriptions = repo.get_active_subscriptions()

    assert len(subscriptions) == 2
    assert all(sub.status == WebhookStatus.ACTIVE for sub in subscriptions)


def test_get_matching_subscriptions(mock_db):
    """Test retrieving webhook subscriptions matching vehicle criteria"""
    repo = WebhookRepository(mock_db)

    # Create mock subscription that should match
    mock_subscription = WebhookSubscription(
        id=1,
        user_id=1,
        webhook_url="https://example.com/webhook",
        status=WebhookStatus.ACTIVE,
        make="Toyota",
        model="RAV4",
        price_min=20000,
        price_max=30000,
        year_min=2020,
    )

    mock_query = MagicMock()
    # Chain the filters
    filtered_query = mock_query.filter.return_value
    for _ in range(7):  # Multiple filter calls
        filtered_query = filtered_query.filter.return_value
    filtered_query.all.return_value = [mock_subscription]
    mock_db.query.return_value = mock_query

    repo.get_matching_subscriptions(
        make="Toyota", model="RAV4", price=25000, year=2022, mileage=30000
    )

    # In a real scenario, this would match based on criteria
    # For now, just verify the query is constructed
    mock_db.query.assert_called_once()


def test_update_webhook_subscription(mock_db):
    """Test updating a webhook subscription"""
    repo = WebhookRepository(mock_db)

    mock_subscription = WebhookSubscription(
        id=1,
        user_id=1,
        webhook_url="https://example.com/webhook",
        status=WebhookStatus.ACTIVE,
        failure_count=0,
    )

    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_subscription
    mock_db.query.return_value = mock_query
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    update_data = {"status": WebhookStatus.INACTIVE, "failure_count": 5}

    updated_subscription = repo.update(1, update_data)

    assert updated_subscription is not None
    assert updated_subscription.status == WebhookStatus.INACTIVE
    assert updated_subscription.failure_count == 5
    mock_db.commit.assert_called_once()


def test_delete_webhook_subscription(mock_db):
    """Test deleting a webhook subscription"""
    repo = WebhookRepository(mock_db)

    mock_subscription = WebhookSubscription(
        id=1, user_id=1, webhook_url="https://example.com/webhook", status=WebhookStatus.ACTIVE
    )

    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_subscription
    mock_db.query.return_value = mock_query
    mock_db.delete = MagicMock()
    mock_db.commit = MagicMock()

    result = repo.delete(1)

    assert result is True
    mock_db.delete.assert_called_once_with(mock_subscription)
    mock_db.commit.assert_called_once()


def test_increment_failure_count(mock_db):
    """Test incrementing failure count"""
    repo = WebhookRepository(mock_db)

    mock_subscription = WebhookSubscription(
        id=1,
        user_id=1,
        webhook_url="https://example.com/webhook",
        status=WebhookStatus.ACTIVE,
        failure_count=0,
    )

    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_subscription
    mock_db.query.return_value = mock_query
    mock_db.commit = MagicMock()

    repo.increment_failure_count(1)

    assert mock_subscription.failure_count == 1
    assert mock_subscription.status == WebhookStatus.ACTIVE
    mock_db.commit.assert_called_once()


def test_increment_failure_count_auto_disable(mock_db):
    """Test that subscription is auto-disabled after 5 failures"""
    repo = WebhookRepository(mock_db)

    mock_subscription = WebhookSubscription(
        id=1,
        user_id=1,
        webhook_url="https://example.com/webhook",
        status=WebhookStatus.ACTIVE,
        failure_count=4,  # Already at 4 failures
    )

    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_subscription
    mock_db.query.return_value = mock_query
    mock_db.commit = MagicMock()

    repo.increment_failure_count(1)

    assert mock_subscription.failure_count == 5
    assert mock_subscription.status == WebhookStatus.FAILED
    mock_db.commit.assert_called_once()


def test_reset_failure_count(mock_db):
    """Test resetting failure count"""
    repo = WebhookRepository(mock_db)

    mock_subscription = WebhookSubscription(
        id=1,
        user_id=1,
        webhook_url="https://example.com/webhook",
        status=WebhookStatus.FAILED,
        failure_count=5,
    )

    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_subscription
    mock_db.query.return_value = mock_query
    mock_db.commit = MagicMock()

    repo.reset_failure_count(1)

    assert mock_subscription.failure_count == 0
    assert mock_subscription.status == WebhookStatus.ACTIVE
    mock_db.commit.assert_called_once()

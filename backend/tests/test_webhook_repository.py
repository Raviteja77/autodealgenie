"""Tests for webhook repository"""

import pytest
import pytest_asyncio

from app.models.models import User, WebhookStatus
from app.repositories.webhook_repository import WebhookRepository


class WebhookEvent:
    DEAL_CREATED = "deal_created"
    DEAL_UPDATED = "deal_updated"
    EVALUATION_COMPLETED = "evaluation_completed"


@pytest_asyncio.fixture
async def mock_user(async_db):
    """Create a mock user for testing"""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password="hashed",
        full_name="Test User",
    )
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)
    return user


@pytest.mark.asyncio
async def test_create_webhook_subscription(async_db, mock_user):
    """Test creating a webhook subscription"""
    repo = WebhookRepository(async_db)

    subscription = await repo.create(
        {
            "user_id": mock_user.id,
            "webhook_url": "https://example.com/webhook",
            "events": [WebhookEvent.DEAL_CREATED],
            "status": WebhookStatus.ACTIVE,
            "secret": "test_secret_123",
        }
    )

    assert subscription.id is not None
    assert subscription.user_id == mock_user.id
    assert subscription.webhook_url == "https://example.com/webhook"
    assert subscription.status == WebhookStatus.ACTIVE
    assert WebhookEvent.DEAL_CREATED in subscription.events
    assert WebhookEvent.DEAL_UPDATED in subscription.events


@pytest.mark.asyncio
async def test_get_webhook_by_id(async_db, mock_user):
    """Test getting webhook by ID"""
    repo = WebhookRepository(async_db)

    subscription = await repo.create(
        {
            "user_id": mock_user.id,
            "webhook_url": "https://example.com/webhook",
            "events": [WebhookEvent.DEAL_CREATED],
            "status": WebhookStatus.ACTIVE,
            "secret": "test_secret_123",
        }
    )

    retrieved = await repo.get(subscription.id)
    assert retrieved is not None
    assert retrieved.id == subscription.id
    assert retrieved.webhook_url == subscription.webhook_url


@pytest.mark.asyncio
async def test_get_webhooks_by_user(async_db, mock_user):
    """Test getting all webhooks for a user"""
    repo = WebhookRepository(async_db)

    # Create multiple webhooks
    sub1 = await repo.create(
        {
            "user_id": mock_user.id,
            "webhook_url": "https://example.com/webhook1",
            "events": [WebhookEvent.DEAL_CREATED],
            "status": WebhookStatus.ACTIVE,
            "secret": "test_secret_123",
        }
    )

    sub2 = await repo.create(
        {
            "user_id": mock_user.id,
            "webhook_url": "https://example.com/webhook2",
            "events": [WebhookEvent.DEAL_UPDATED],
            "status": WebhookStatus.ACTIVE,
            "secret": "test_secret_123",
        }
    )

    webhooks = await repo.get_by_user(mock_user.id)
    assert len(webhooks) == 2
    assert sub1.id in [w.id for w in webhooks]
    assert sub2.id in [w.id for w in webhooks]


@pytest.mark.asyncio
async def test_get_active_subscriptions(async_db, mock_user):
    """Test getting active subscriptions"""
    repo = WebhookRepository(async_db)

    # Create active webhook
    sub1 = await repo.create(
        {
            "user_id": mock_user.id,
            "webhook_url": "https://example.com/webhook1",
            "events": [WebhookEvent.DEAL_CREATED],
            "status": WebhookStatus.ACTIVE,
            "secret": "test_secret_123",
        }
    )

    # Create inactive webhook
    sub2 = await repo.create(
        {
            "user_id": mock_user.id,
            "webhook_url": "https://example.com/webhook2",
            "events": [WebhookEvent.DEAL_UPDATED],
            "status": WebhookStatus.ACTIVE,
            "secret": "test_secret_123",
        }
    )
    await repo.update_status(sub2.id, WebhookStatus.DISABLED)

    active = await repo.get_active_subscriptions(mock_user.id)
    assert len(active) == 1
    assert active[0].id == sub1.id
    assert active[0].status == WebhookStatus.ACTIVE


@pytest.mark.asyncio
async def test_get_matching_subscriptions(async_db, mock_user):
    """Test getting subscriptions matching an event"""
    repo = WebhookRepository(async_db)

    # Create webhooks with different events
    sub1 = await repo.create(
        {
            "user_id": mock_user.id,
            "webhook_url": "https://example.com/webhook1",
            "events": [WebhookEvent.DEAL_CREATED, WebhookEvent.DEAL_UPDATED],
            "status": WebhookStatus.ACTIVE,
            "secret": "test_secret_123",
        }
    )

    await repo.create(
        {
            "user_id": mock_user.id,
            "webhook_url": "https://example.com/webhook2",
            "events": [WebhookEvent.EVALUATION_COMPLETED],
            "status": WebhookStatus.ACTIVE,
            "secret": "test_secret_123",
        }
    )

    # Get subscriptions for DEAL_CREATED event
    matching = await repo.get_matching_subscriptions(WebhookEvent.DEAL_CREATED)
    assert len(matching) == 1
    assert matching[0].id == sub1.id


@pytest.mark.asyncio
async def test_update_webhook_subscription(async_db, mock_user):
    """Test updating a webhook subscription"""
    repo = WebhookRepository(async_db)

    subscription = await repo.create(
        {
            "user_id": mock_user.id,
            "webhook_url": "https://example.com/webhook",
            "events": [WebhookEvent.DEAL_CREATED],
            "status": WebhookStatus.ACTIVE,
            "secret": "test_secret_123",
        }
    )

    updated = await repo.create(
        {
            "user_id": mock_user.id,
            "webhook_url": "https://example.com/webhook",
            "events": [WebhookEvent.DEAL_UPDATED],
            "status": WebhookStatus.ACTIVE,
            "secret": "test_secret_123",
        }
    )

    assert updated is not None
    assert updated.webhook_url == "https://example.com/new-webhook"
    assert len(updated.events) == 2


@pytest.mark.asyncio
async def test_delete_webhook_subscription(async_db, mock_user):
    """Test deleting a webhook subscription"""
    repo = WebhookRepository(async_db)

    subscription = await repo.create(
        {
            "user_id": mock_user.id,
            "webhook_url": "https://example.com/webhook",
            "events": [WebhookEvent.DEAL_CREATED],
            "status": WebhookStatus.ACTIVE,
            "secret": "test_secret_123",
        }
    )

    deleted = await repo.delete(subscription.id)
    assert deleted is True

    # Verify it's deleted
    retrieved = await repo.get(subscription.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_increment_failure_count(async_db, mock_user):
    """Test incrementing failure count"""
    repo = WebhookRepository(async_db)

    subscription = await repo.create(
        {
            "user_id": mock_user.id,
            "webhook_url": "https://example.com/webhook",
            "events": [WebhookEvent.DEAL_CREATED],
            "status": WebhookStatus.ACTIVE,
            "secret": "test_secret_123",
        }
    )

    assert subscription.failure_count == 0

    updated = await repo.increment_failure_count(subscription.id)
    assert updated.failure_count == 1


@pytest.mark.asyncio
async def test_increment_failure_count_auto_disable(async_db, mock_user):
    """Test auto-disable after max failures"""
    repo = WebhookRepository(async_db)

    subscription = await repo.create(
        {
            "user_id": mock_user.id,
            "webhook_url": "https://example.com/webhook",
            "events": [WebhookEvent.DEAL_CREATED],
            "status": WebhookStatus.ACTIVE,
            "secret": "test_secret_123",
        }
    )

    # Increment to max failures (5)
    for _ in range(5):
        subscription = await repo.increment_failure_count(subscription.id)

    assert subscription.failure_count == 5
    assert subscription.status == WebhookStatus.DISABLED


@pytest.mark.asyncio
async def test_reset_failure_count(async_db, mock_user):
    """Test resetting failure count"""
    repo = WebhookRepository(async_db)

    subscription = await repo.create(
        {
            "user_id": mock_user.id,
            "webhook_url": "https://example.com/webhook",
            "events": [WebhookEvent.DEAL_CREATED],
            "status": WebhookStatus.ACTIVE,
            "secret": "test_secret_123",
        }
    )

    # Increment failure count
    for _ in range(5):
        await repo.increment_failure_count(subscription.id)

    # Reset
    updated = await repo.reset_failure_count(subscription.id)
    assert updated.failure_count == 0
    assert updated.status == WebhookStatus.ACTIVE

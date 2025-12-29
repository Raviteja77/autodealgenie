"""
Repository for webhook subscription operations
"""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import WebhookStatus, WebhookSubscription


class WebhookRepository:
    """Repository for managing webhook subscriptions"""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session"""
        self.db = db

    async def create(self, subscription_data: dict) -> WebhookSubscription:
        """
        Create a new webhook subscription

        Args:
            subscription_data: Dictionary containing subscription details

        Returns:
            Created WebhookSubscription instance
        """
        subscription = WebhookSubscription(**subscription_data)
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def get_by_id(self, subscription_id: int) -> WebhookSubscription | None:
        """Get webhook subscription by ID"""
        result = await self.db.execute(
            select(WebhookSubscription).filter(WebhookSubscription.id == subscription_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> list[WebhookSubscription]:
        """Get all webhook subscriptions for a user"""
        result = await self.db.execute(
            select(WebhookSubscription).filter(WebhookSubscription.user_id == user_id)
        )
        return result.scalars().all()

    async def get_active_subscriptions(self) -> list[WebhookSubscription]:
        """Get all active webhook subscriptions"""
        result = await self.db.execute(
            select(WebhookSubscription).filter(WebhookSubscription.status == WebhookStatus.ACTIVE)
        )
        return result.scalars().all()

    async def get_matching_subscriptions(
        self,
        make: str | None = None,
        model: str | None = None,
        price: float | None = None,
        year: int | None = None,
        mileage: int | None = None,
    ) -> list[WebhookSubscription]:
        """
        Get webhook subscriptions matching vehicle criteria

        Args:
            make: Vehicle make
            model: Vehicle model
            price: Vehicle price
            year: Vehicle year
            mileage: Vehicle mileage

        Returns:
            List of matching webhook subscriptions
        """
        query = select(WebhookSubscription).filter(
            WebhookSubscription.status == WebhookStatus.ACTIVE
        )

        # Filter by criteria (None or matching)
        if make:
            query = query.filter(
                or_(WebhookSubscription.make.is_(None), WebhookSubscription.make == make)
            )
        if model:
            query = query.filter(
                or_(WebhookSubscription.model.is_(None), WebhookSubscription.model == model)
            )
        if price:
            query = query.filter(
                or_(
                    WebhookSubscription.price_min.is_(None),
                    WebhookSubscription.price_min <= price,
                )
            )
            query = query.filter(
                or_(
                    WebhookSubscription.price_max.is_(None),
                    WebhookSubscription.price_max >= price,
                )
            )
        if year:
            query = query.filter(
                or_(WebhookSubscription.year_min.is_(None), WebhookSubscription.year_min <= year)
            )
            query = query.filter(
                or_(WebhookSubscription.year_max.is_(None), WebhookSubscription.year_max >= year)
            )
        if mileage:
            query = query.filter(
                or_(
                    WebhookSubscription.mileage_max.is_(None),
                    WebhookSubscription.mileage_max >= mileage,
                )
            )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(self, subscription_id: int, update_data: dict) -> WebhookSubscription | None:
        """
        Update webhook subscription

        Args:
            subscription_id: Subscription ID
            update_data: Dictionary of fields to update

        Returns:
            Updated WebhookSubscription or None
        """
        subscription = await self.get_by_id(subscription_id)
        if not subscription:
            return None

        for key, value in update_data.items():
            if hasattr(subscription, key):
                setattr(subscription, key, value)

        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def delete(self, subscription_id: int) -> bool:
        """
        Delete webhook subscription

        Args:
            subscription_id: Subscription ID

        Returns:
            True if deleted, False otherwise
        """
        subscription = await self.get_by_id(subscription_id)
        if not subscription:
            return False

        await self.db.delete(subscription)
        await self.db.commit()
        return True

    async def increment_failure_count(self, subscription_id: int) -> None:
        """Increment failure count for a subscription"""
        subscription = await self.get_by_id(subscription_id)
        if subscription:
            subscription.failure_count += 1
            # Auto-disable after 5 consecutive failures
            if subscription.failure_count >= 5:
                subscription.status = WebhookStatus.FAILED
            await self.db.commit()

    async def reset_failure_count(self, subscription_id: int) -> None:
        """Reset failure count for a subscription"""
        subscription = await self.get_by_id(subscription_id)
        if subscription:
            subscription.failure_count = 0
            if subscription.status == WebhookStatus.FAILED:
                subscription.status = WebhookStatus.ACTIVE
            await self.db.commit()

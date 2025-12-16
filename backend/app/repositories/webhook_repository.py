"""
Repository for webhook subscription operations
"""

from sqlalchemy.orm import Session

from app.models.models import WebhookStatus, WebhookSubscription


class WebhookRepository:
    """Repository for managing webhook subscriptions"""

    def __init__(self, db: Session):
        """Initialize repository with database session"""
        self.db = db

    def create(self, subscription_data: dict) -> WebhookSubscription:
        """
        Create a new webhook subscription

        Args:
            subscription_data: Dictionary containing subscription details

        Returns:
            Created WebhookSubscription instance
        """
        subscription = WebhookSubscription(**subscription_data)
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def get_by_id(self, subscription_id: int) -> WebhookSubscription | None:
        """Get webhook subscription by ID"""
        return (
            self.db.query(WebhookSubscription)
            .filter(WebhookSubscription.id == subscription_id)
            .first()
        )

    def get_by_user(self, user_id: int) -> list[WebhookSubscription]:
        """Get all webhook subscriptions for a user"""
        return (
            self.db.query(WebhookSubscription).filter(WebhookSubscription.user_id == user_id).all()
        )

    def get_active_subscriptions(self) -> list[WebhookSubscription]:
        """Get all active webhook subscriptions"""
        return (
            self.db.query(WebhookSubscription)
            .filter(WebhookSubscription.status == WebhookStatus.ACTIVE)
            .all()
        )

    def get_matching_subscriptions(
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
        query = self.db.query(WebhookSubscription).filter(
            WebhookSubscription.status == WebhookStatus.ACTIVE
        )

        # Filter by criteria (None or matching)
        if make:
            query = query.filter(
                (WebhookSubscription.make is None) | (WebhookSubscription.make == make)
            )
        if model:
            query = query.filter(
                (WebhookSubscription.model is None) | (WebhookSubscription.model == model)
            )
        if price:
            query = query.filter(
                (WebhookSubscription.price_min is None) | (WebhookSubscription.price_min <= price)
            )
            query = query.filter(
                (WebhookSubscription.price_max is None) | (WebhookSubscription.price_max >= price)
            )
        if year:
            query = query.filter(
                (WebhookSubscription.year_min is None) | (WebhookSubscription.year_min <= year)
            )
            query = query.filter(
                (WebhookSubscription.year_max is None) | (WebhookSubscription.year_max >= year)
            )
        if mileage:
            query = query.filter(
                (WebhookSubscription.mileage_max is None)
                | (WebhookSubscription.mileage_max >= mileage)
            )

        return query.all()

    def update(self, subscription_id: int, update_data: dict) -> WebhookSubscription | None:
        """
        Update webhook subscription

        Args:
            subscription_id: Subscription ID
            update_data: Dictionary of fields to update

        Returns:
            Updated WebhookSubscription or None
        """
        subscription = self.get_by_id(subscription_id)
        if not subscription:
            return None

        for key, value in update_data.items():
            if hasattr(subscription, key):
                setattr(subscription, key, value)

        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def delete(self, subscription_id: int) -> bool:
        """
        Delete webhook subscription

        Args:
            subscription_id: Subscription ID

        Returns:
            True if deleted, False otherwise
        """
        subscription = self.get_by_id(subscription_id)
        if not subscription:
            return False

        self.db.delete(subscription)
        self.db.commit()
        return True

    def increment_failure_count(self, subscription_id: int) -> None:
        """Increment failure count for a subscription"""
        subscription = self.get_by_id(subscription_id)
        if subscription:
            subscription.failure_count += 1
            # Auto-disable after 5 consecutive failures
            if subscription.failure_count >= 5:
                subscription.status = WebhookStatus.FAILED
            self.db.commit()

    def reset_failure_count(self, subscription_id: int) -> None:
        """Reset failure count for a subscription"""
        subscription = self.get_by_id(subscription_id)
        if subscription:
            subscription.failure_count = 0
            if subscription.status == WebhookStatus.FAILED:
                subscription.status = WebhookStatus.ACTIVE
            self.db.commit()

"""
Webhook subscription management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.models import User, WebhookStatus
from app.repositories.webhook_repository import WebhookRepository

router = APIRouter()


class WebhookSubscriptionCreate(BaseModel):
    """Schema for creating webhook subscription"""

    webhook_url: HttpUrl = Field(
        ..., description="URL to receive webhook notifications"
    )
    secret_token: str | None = Field(
        None, description="Secret token for webhook verification"
    )
    make: str | None = Field(None, description="Filter by vehicle make")
    model: str | None = Field(None, description="Filter by vehicle model")
    price_min: float | None = Field(None, description="Minimum price filter", ge=0)
    price_max: float | None = Field(None, description="Maximum price filter", ge=0)
    year_min: int | None = Field(None, description="Minimum year filter")
    year_max: int | None = Field(None, description="Maximum year filter")
    mileage_max: int | None = Field(None, description="Maximum mileage filter", ge=0)


class WebhookSubscriptionUpdate(BaseModel):
    """Schema for updating webhook subscription"""

    webhook_url: HttpUrl | None = None
    secret_token: str | None = None
    status: WebhookStatus | None = None
    make: str | None = None
    model: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    year_min: int | None = None
    year_max: int | None = None
    mileage_max: int | None = None


class WebhookSubscriptionResponse(BaseModel):
    """Schema for webhook subscription response"""

    id: int
    user_id: int
    webhook_url: str
    status: WebhookStatus
    make: str | None = None
    model: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    year_min: int | None = None
    year_max: int | None = None
    mileage_max: int | None = None
    failure_count: int
    created_at: str
    updated_at: str | None = None

    class Config:
        from_attributes = True


@router.post(
    "/", response_model=WebhookSubscriptionResponse, status_code=status.HTTP_201_CREATED
)
async def create_webhook_subscription(
    subscription_data: WebhookSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new webhook subscription for vehicle alerts

    Webhooks will be triggered when new vehicles matching the criteria are found.
    """
    webhook_repo = WebhookRepository(db)

    # Prepare subscription data
    data = subscription_data.model_dump()
    data["user_id"] = current_user.id
    data["status"] = WebhookStatus.ACTIVE

    try:
        subscription = webhook_repo.create(data)
        return subscription
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create webhook subscription: {str(e)}",
        ) from e


@router.get("/", response_model=list[WebhookSubscriptionResponse])
async def list_webhook_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all webhook subscriptions for the current user
    """
    webhook_repo = WebhookRepository(db)
    subscriptions = webhook_repo.get_by_user(current_user.id)
    return subscriptions


@router.get("/{subscription_id}", response_model=WebhookSubscriptionResponse)
async def get_webhook_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific webhook subscription by ID
    """
    webhook_repo = WebhookRepository(db)
    subscription = webhook_repo.get_by_id(subscription_id)

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook subscription not found",
        )

    # Verify ownership
    if subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this webhook subscription",
        )

    return subscription


@router.patch("/{subscription_id}", response_model=WebhookSubscriptionResponse)
async def update_webhook_subscription(
    subscription_id: int,
    update_data: WebhookSubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a webhook subscription
    """
    webhook_repo = WebhookRepository(db)
    subscription = webhook_repo.get_by_id(subscription_id)

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook subscription not found",
        )

    # Verify ownership
    if subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this webhook subscription",
        )

    # Update subscription
    data = update_data.model_dump(exclude_unset=True)
    updated_subscription = webhook_repo.update(subscription_id, data)

    return updated_subscription


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a webhook subscription
    """
    webhook_repo = WebhookRepository(db)
    subscription = webhook_repo.get_by_id(subscription_id)

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook subscription not found",
        )

    # Verify ownership
    if subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this webhook subscription",
        )

    # Delete subscription
    webhook_repo.delete(subscription_id)
    return None

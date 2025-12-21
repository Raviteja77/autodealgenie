"""
Pydantic schemas for Negotiation API
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NegotiationStatus(str, Enum):
    """Negotiation session status enumeration"""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MessageRole(str, Enum):
    """Message role enumeration"""

    USER = "user"
    AGENT = "agent"
    DEALER_SIM = "dealer_sim"


class UserAction(str, Enum):
    """User action for next round"""

    CONFIRM = "confirm"
    REJECT = "reject"
    COUNTER = "counter"


class CreateNegotiationRequest(BaseModel):
    """Schema for creating a negotiation session"""

    deal_id: int = Field(..., gt=0, description="ID of the deal being negotiated")
    user_target_price: float = Field(..., gt=0, description="User's target price in USD")
    strategy: str | None = Field(
        None, max_length=50, description="Negotiation strategy (e.g., aggressive, moderate)"
    )


class NextRoundRequest(BaseModel):
    """Schema for processing the next negotiation round"""

    user_action: UserAction = Field(..., description="User's action: confirm, reject, or counter")
    counter_offer: float | None = Field(
        None, gt=0, description="Counter offer price (required if action is counter)"
    )


class NegotiationMessageResponse(BaseModel):
    """Schema for negotiation message response"""

    id: int
    session_id: int
    role: MessageRole
    content: str
    round_number: int
    metadata: dict[str, Any] | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class NegotiationSessionResponse(BaseModel):
    """Schema for negotiation session response"""

    id: int
    user_id: int
    deal_id: int
    status: NegotiationStatus
    current_round: int
    max_rounds: int
    created_at: datetime
    updated_at: datetime | None = None
    messages: list[NegotiationMessageResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class NegotiationSessionSummary(BaseModel):
    """Schema for negotiation session summary (without messages)"""

    id: int
    user_id: int
    deal_id: int
    status: NegotiationStatus
    current_round: int
    max_rounds: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class FinancingOption(BaseModel):
    """Financing details for current negotiation price"""

    loan_amount: float = Field(..., description="Loan amount after down payment")
    down_payment: float = Field(..., description="Down payment amount")
    monthly_payment_estimate: float = Field(..., description="Estimated monthly payment")
    loan_term_months: int = Field(..., description="Loan term in months")
    estimated_apr: float = Field(..., description="Estimated APR as decimal")
    total_cost: float = Field(..., description="Total cost over loan term")
    total_interest: float = Field(..., description="Total interest paid")


class NegotiationRoundMetadata(BaseModel):
    """Enhanced metadata with financing options"""

    suggested_price: float
    asking_price: float
    user_action: str | None = None
    financing_options: list[FinancingOption] | None = None
    cash_savings: float | None = None  # vs financing total cost


class NextRoundResponse(BaseModel):
    """Response schema for next negotiation round with financing"""

    session_id: int
    status: NegotiationStatus
    current_round: int
    agent_message: str
    metadata: NegotiationRoundMetadata

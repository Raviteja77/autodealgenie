"""
Add webhook_subscriptions table

Revision ID: 002_add_webhook_subscriptions
Revises: 001_add_password_reset_fields
Create Date: 2025-12-14

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_add_webhook_subscriptions"
down_revision: str | None = "001_add_password_reset_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create webhook_subscriptions table"""
    op.create_table(
        "webhook_subscriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("webhook_url", sa.String(length=512), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "INACTIVE", "FAILED", name="webhookstatus"),
            nullable=False,
        ),
        sa.Column("make", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("price_min", sa.Float(), nullable=True),
        sa.Column("price_max", sa.Float(), nullable=True),
        sa.Column("year_min", sa.Integer(), nullable=True),
        sa.Column("year_max", sa.Integer(), nullable=True),
        sa.Column("mileage_max", sa.Integer(), nullable=True),
        sa.Column("secret_token", sa.String(length=255), nullable=True),
        sa.Column("last_triggered", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_webhook_subscriptions_id"), "webhook_subscriptions", ["id"])
    op.create_index(op.f("ix_webhook_subscriptions_user_id"), "webhook_subscriptions", ["user_id"])


def downgrade() -> None:
    """Drop webhook_subscriptions table"""
    op.drop_index(op.f("ix_webhook_subscriptions_user_id"), table_name="webhook_subscriptions")
    op.drop_index(op.f("ix_webhook_subscriptions_id"), table_name="webhook_subscriptions")
    op.drop_table("webhook_subscriptions")
    # Drop the enum type after dropping the table that uses it
    op.execute("DROP TYPE IF EXISTS webhookstatus")

"""
Add negotiation_sessions and negotiation_messages tables

Revision ID: 003_add_negotiation_tables
Revises: 002_add_webhook_subscriptions
Create Date: 2025-12-16

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003_add_negotiation_tables"
down_revision: str | None = "002_add_webhook_subscriptions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create negotiation_sessions and negotiation_messages tables"""

    # Create negotiation_sessions table
    op.create_table(
        "negotiation_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("deal_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "completed", "cancelled", name="negotiationstatus"),
            nullable=False,
            server_default="active",
        ),
        sa.Column("current_round", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("max_rounds", sa.Integer(), nullable=False, server_default="10"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_negotiation_sessions_id"), "negotiation_sessions", ["id"])
    op.create_index(op.f("ix_negotiation_sessions_user_id"), "negotiation_sessions", ["user_id"])
    op.create_index(op.f("ix_negotiation_sessions_deal_id"), "negotiation_sessions", ["deal_id"])
    op.create_index(op.f("ix_negotiation_sessions_status"), "negotiation_sessions", ["status"])

    # Create negotiation_messages table
    op.create_table(
        "negotiation_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("user", "agent", "dealer_sim", name="messagerole"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["session_id"], ["negotiation_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_negotiation_messages_id"), "negotiation_messages", ["id"])
    op.create_index(
        op.f("ix_negotiation_messages_session_id"),
        "negotiation_messages",
        ["session_id"],
    )
    op.create_index(
        op.f("ix_negotiation_messages_round_number"),
        "negotiation_messages",
        ["round_number"],
    )


def downgrade() -> None:
    """Drop negotiation_messages and negotiation_sessions tables"""
    op.drop_index(op.f("ix_negotiation_messages_round_number"), table_name="negotiation_messages")
    op.drop_index(op.f("ix_negotiation_messages_session_id"), table_name="negotiation_messages")
    op.drop_index(op.f("ix_negotiation_messages_id"), table_name="negotiation_messages")
    op.drop_table("negotiation_messages")

    op.drop_index(op.f("ix_negotiation_sessions_status"), table_name="negotiation_sessions")
    op.drop_index(op.f("ix_negotiation_sessions_deal_id"), table_name="negotiation_sessions")
    op.drop_index(op.f("ix_negotiation_sessions_user_id"), table_name="negotiation_sessions")
    op.drop_index(op.f("ix_negotiation_sessions_id"), table_name="negotiation_sessions")
    op.drop_table("negotiation_sessions")

    # Drop the enum types after dropping the tables that use them
    op.execute("DROP TYPE IF EXISTS messagerole")
    op.execute("DROP TYPE IF EXISTS negotiationstatus")

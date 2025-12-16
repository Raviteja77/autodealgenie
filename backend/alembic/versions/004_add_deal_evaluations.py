"""
Add deal_evaluations table

Revision ID: 004_add_deal_evaluations
Revises: 002_add_webhook_subscriptions
Create Date: 2025-12-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004_add_deal_evaluations"
down_revision: Union[str, None] = "003_add_negotiation_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create deal_evaluations table"""
    op.create_table(
        "deal_evaluations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("deal_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ANALYZING", "AWAITING_INPUT", "COMPLETED", name="evaluationstatus"),
            nullable=False,
        ),
        sa.Column(
            "current_step",
            sa.Enum(
                "VEHICLE_CONDITION",
                "PRICE",
                "FINANCING",
                "RISK",
                "FINAL",
                name="pipelinestep",
            ),
            nullable=False,
        ),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"]),
    )
    op.create_index(op.f("ix_deal_evaluations_id"), "deal_evaluations", ["id"])
    op.create_index(op.f("ix_deal_evaluations_user_id"), "deal_evaluations", ["user_id"])
    op.create_index(op.f("ix_deal_evaluations_deal_id"), "deal_evaluations", ["deal_id"])
    op.create_index(op.f("ix_deal_evaluations_status"), "deal_evaluations", ["status"])


def downgrade() -> None:
    """Drop deal_evaluations table"""
    op.drop_index(op.f("ix_deal_evaluations_status"), table_name="deal_evaluations")
    op.drop_index(op.f("ix_deal_evaluations_deal_id"), table_name="deal_evaluations")
    op.drop_index(op.f("ix_deal_evaluations_user_id"), table_name="deal_evaluations")
    op.drop_index(op.f("ix_deal_evaluations_id"), table_name="deal_evaluations")
    op.drop_table("deal_evaluations")
    # Drop the enum types after dropping the table that uses them
    op.execute("DROP TYPE IF EXISTS evaluationstatus")
    op.execute("DROP TYPE IF EXISTS pipelinestep")

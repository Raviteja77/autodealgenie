"""Add performance indexes for frequently queried fields

Revision ID: 008_add_performance_indexes
Revises: 007_add_ai_response_tables
Create Date: 2025-12-25 16:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008_add_performance_indexes"
down_revision: Union[str, None] = "007_add_ai_response_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for frequently queried fields"""

    # Composite indexes for common query patterns
    # Users table - search by active status
    op.create_index(
        "ix_users_is_active_created_at",
        "users",
        ["is_active", "created_at"],
        postgresql_where=sa.text("is_active = 1"),
    )

    # Deals table - filter by status and date
    op.create_index("ix_deals_status_created_at", "deals", ["status", "created_at"])

    # Deals table - search by vehicle
    op.create_index(
        "ix_deals_vehicle_lookup",
        "deals",
        ["vehicle_make", "vehicle_model", "vehicle_year"],
    )

    # Deals table - VIN lookup (if exists)
    try:
        op.create_index(
            "ix_deals_vehicle_vin",
            "deals",
            ["vehicle_vin"],
            unique=True,
            postgresql_where=sa.text("vehicle_vin IS NOT NULL"),
        )
    except Exception:
        # VIN column might not exist in all versions
        pass


def downgrade() -> None:
    """Drop performance indexes"""

    try:
        op.drop_index("ix_deals_vehicle_vin", table_name="deals")
    except Exception:
        pass

    op.drop_index("ix_deals_vehicle_lookup", table_name="deals")
    op.drop_index("ix_deals_status_created_at", table_name="deals")
    op.drop_index("ix_users_is_active_created_at", table_name="users")

"""Initial database schema with users and deals tables

Revision ID: 000_initial_tables
Revises:
Create Date: 2025-12-16 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "000_initial_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial users and deals tables"""

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_superuser", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"])
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    # Create deals table
    op.create_table(
        "deals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=False),
        sa.Column("customer_email", sa.String(length=255), nullable=False),
        sa.Column("vehicle_make", sa.String(length=100), nullable=False),
        sa.Column("vehicle_model", sa.String(length=100), nullable=False),
        sa.Column("vehicle_year", sa.Integer(), nullable=False),
        sa.Column("vehicle_mileage", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("vehicle_vin", sa.String(length=17), nullable=False),
        sa.Column("asking_price", sa.Float(), nullable=False),
        sa.Column("offer_price", sa.Float(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "in_progress", "completed", "cancelled", name="dealstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_deals_id"), "deals", ["id"])
    op.create_index(op.f("ix_deals_customer_email"), "deals", ["customer_email"])
    op.create_index(op.f("ix_deals_status"), "deals", ["status"])


def downgrade() -> None:
    """Drop users and deals tables"""
    op.drop_index(op.f("ix_deals_status"), table_name="deals")
    op.drop_index(op.f("ix_deals_customer_email"), table_name="deals")
    op.drop_index(op.f("ix_deals_id"), table_name="deals")
    op.drop_table("deals")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")

    # Drop the enum type after dropping the table that uses it
    op.execute("DROP TYPE IF EXISTS dealstatus")

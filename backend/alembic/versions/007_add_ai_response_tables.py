"""Add AI response tables for loan and insurance recommendations

Revision ID: 007_add_ai_response_tables
Revises: 006_add_saved_searches
Create Date: 2025-12-25 14:30:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "007_add_ai_response_tables"
down_revision = "006_add_saved_searches"
branch_labels = None
depends_on = None


def upgrade():
    # Create loan_recommendations table
    op.create_table(
        "loan_recommendations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("deal_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("loan_amount", sa.Float(), nullable=False),
        sa.Column("down_payment", sa.Float(), nullable=False),
        sa.Column("loan_term_months", sa.Integer(), nullable=False),
        sa.Column("credit_score_range", sa.String(length=50), nullable=False),
        sa.Column("monthly_payment", sa.Float(), nullable=False),
        sa.Column("apr", sa.Float(), nullable=False),
        sa.Column("total_interest", sa.Float(), nullable=False),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("additional_data", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for loan_recommendations
    op.create_index("ix_loan_recommendations_id", "loan_recommendations", ["id"])
    op.create_index("ix_loan_recommendations_deal_id", "loan_recommendations", ["deal_id"])
    op.create_index("ix_loan_recommendations_user_id", "loan_recommendations", ["user_id"])

    # Create insurance_recommendations table
    op.create_table(
        "insurance_recommendations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("deal_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("vehicle_value", sa.Float(), nullable=False),
        sa.Column("vehicle_age", sa.Integer(), nullable=False),
        sa.Column("coverage_type", sa.String(length=50), nullable=False),
        sa.Column("driver_age", sa.Integer(), nullable=False),
        sa.Column("provider_id", sa.String(length=100), nullable=False),
        sa.Column("provider_name", sa.String(length=255), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.Column("estimated_monthly_premium", sa.Float(), nullable=False),
        sa.Column("estimated_annual_premium", sa.Float(), nullable=False),
        sa.Column("recommendation_reason", sa.String(length=512), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("full_recommendation_data", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for insurance_recommendations
    op.create_index("ix_insurance_recommendations_id", "insurance_recommendations", ["id"])
    op.create_index(
        "ix_insurance_recommendations_deal_id", "insurance_recommendations", ["deal_id"]
    )
    op.create_index(
        "ix_insurance_recommendations_user_id", "insurance_recommendations", ["user_id"]
    )


def downgrade():
    # Drop indexes for insurance_recommendations
    op.drop_index("ix_insurance_recommendations_user_id", table_name="insurance_recommendations")
    op.drop_index("ix_insurance_recommendations_deal_id", table_name="insurance_recommendations")
    op.drop_index("ix_insurance_recommendations_id", table_name="insurance_recommendations")

    # Drop insurance_recommendations table
    op.drop_table("insurance_recommendations")

    # Drop indexes for loan_recommendations
    op.drop_index("ix_loan_recommendations_user_id", table_name="loan_recommendations")
    op.drop_index("ix_loan_recommendations_deal_id", table_name="loan_recommendations")
    op.drop_index("ix_loan_recommendations_id", table_name="loan_recommendations")

    # Drop loan_recommendations table
    op.drop_table("loan_recommendations")

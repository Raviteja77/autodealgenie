"""Add loan_applications table

Revision ID: 007_add_loan_applications
Revises: 006_add_saved_searches
Create Date: 2025-12-21 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = "007_add_loan_applications"
down_revision = "006_add_saved_searches"
branch_labels = None
depends_on = None


def upgrade():
    # Create loan_status enum type
    op.execute(
        """
        CREATE TYPE loanstatus AS ENUM (
            'draft', 'submitted', 'pre_approved', 'approved', 'rejected', 'completed'
        )
        """
    )

    # Create loan_applications table
    op.create_table(
        "loan_applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("deal_id", sa.Integer(), nullable=True),
        # Loan details
        sa.Column("loan_amount", sa.Float(), nullable=False),
        sa.Column("down_payment", sa.Float(), nullable=False),
        sa.Column("trade_in_value", sa.Float(), server_default="0", nullable=True),
        sa.Column("loan_term_months", sa.Integer(), nullable=False),
        sa.Column("interest_rate", sa.Float(), nullable=True),
        sa.Column("monthly_payment", sa.Float(), nullable=True),
        # Applicant info
        sa.Column("credit_score_range", sa.String(length=20), nullable=False),
        sa.Column("annual_income", sa.Float(), nullable=True),
        sa.Column("employment_status", sa.String(length=50), nullable=True),
        # Loan offers
        sa.Column("loan_offers", JSON, nullable=True),
        # Status
        sa.Column("status", sa.Enum(
            "DRAFT", "SUBMITTED", "PRE_APPROVED", "APPROVED", "REJECTED", "COMPLETED",
            name="loanstatus"
        ), nullable=False, server_default="DRAFT"),
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

    # Create indexes
    op.create_index("ix_loan_applications_id", "loan_applications", ["id"])
    op.create_index("ix_loan_applications_user_id", "loan_applications", ["user_id"])
    op.create_index("ix_loan_applications_deal_id", "loan_applications", ["deal_id"])
    op.create_index("ix_loan_applications_status", "loan_applications", ["status"])


def downgrade():
    # Drop indexes
    op.drop_index("ix_loan_applications_status", table_name="loan_applications")
    op.drop_index("ix_loan_applications_deal_id", table_name="loan_applications")
    op.drop_index("ix_loan_applications_user_id", table_name="loan_applications")
    op.drop_index("ix_loan_applications_id", table_name="loan_applications")

    # Drop table
    op.drop_table("loan_applications")

    # Drop enum type
    op.execute("DROP TYPE loanstatus")

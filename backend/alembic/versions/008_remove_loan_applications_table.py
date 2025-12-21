"""Remove loan_applications table

Revision ID: 008_remove_loan_applications_table
Revises: 007_add_loan_applications
Create Date: 2025-12-21 16:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = "008_remove_loan_applications_table"
down_revision = "007_add_loan_applications"
branch_labels = None
depends_on = None


def upgrade():
    """
    Backup and remove loan_applications table.
    
    This migration:
    1. Creates a backup table with all data from loan_applications
    2. Drops the loan_applications table
    3. Drops the loanstatus enum type
    """
    # Create backup table with same structure
    op.create_table(
        "loan_applications_backup",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("deal_id", sa.Integer(), nullable=True),
        # Loan details
        sa.Column("loan_amount", sa.Float(), nullable=False),
        sa.Column("down_payment", sa.Float(), nullable=False),
        sa.Column("trade_in_value", sa.Float(), nullable=True),
        sa.Column("loan_term_months", sa.Integer(), nullable=False),
        sa.Column("interest_rate", sa.Float(), nullable=True),
        sa.Column("monthly_payment", sa.Float(), nullable=True),
        # Applicant info
        sa.Column("credit_score_range", sa.String(length=20), nullable=False),
        sa.Column("annual_income", sa.Float(), nullable=True),
        sa.Column("employment_status", sa.String(length=50), nullable=True),
        # Loan offers
        sa.Column("loan_offers", JSON, nullable=True),
        # Status (stored as string in backup)
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("backup_timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Copy all data from loan_applications to backup table
    # Convert enum status to string for backup
    op.execute("""
        INSERT INTO loan_applications_backup (
            id, user_id, deal_id, loan_amount, down_payment, trade_in_value,
            loan_term_months, interest_rate, monthly_payment, credit_score_range,
            annual_income, employment_status, loan_offers, status, created_at, updated_at
        )
        SELECT 
            id, user_id, deal_id, loan_amount, down_payment, trade_in_value,
            loan_term_months, interest_rate, monthly_payment, credit_score_range,
            annual_income, employment_status, loan_offers, status::text, created_at, updated_at
        FROM loan_applications
    """)

    # Drop indexes first
    op.drop_index("ix_loan_applications_status", table_name="loan_applications")
    op.drop_index("ix_loan_applications_deal_id", table_name="loan_applications")
    op.drop_index("ix_loan_applications_user_id", table_name="loan_applications")
    op.drop_index("ix_loan_applications_id", table_name="loan_applications")

    # Drop the loan_applications table
    op.drop_table("loan_applications")

    # Drop the loanstatus enum type
    op.execute("DROP TYPE IF EXISTS loanstatus")


def downgrade():
    """
    Restore loan_applications table from backup.
    
    WARNING: This will only restore the table structure and data from backup.
    New loan applications created after upgrade will NOT be included.
    """
    # Recreate loanstatus enum type
    op.execute(
        """
        CREATE TYPE loanstatus AS ENUM (
            'draft', 'submitted', 'pre_approved', 'approved', 'rejected', 'completed'
        )
        """
    )

    # Recreate loan_applications table
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
            "draft", "submitted", "pre_approved", "approved", "rejected", "completed",
            name="loanstatus"
        ), nullable=False, server_default="draft"),
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

    # Restore indexes
    op.create_index("ix_loan_applications_id", "loan_applications", ["id"])
    op.create_index("ix_loan_applications_user_id", "loan_applications", ["user_id"])
    op.create_index("ix_loan_applications_deal_id", "loan_applications", ["deal_id"])
    op.create_index("ix_loan_applications_status", "loan_applications", ["status"])

    # Restore data from backup table
    # Convert string status back to enum
    op.execute("""
        INSERT INTO loan_applications (
            id, user_id, deal_id, loan_amount, down_payment, trade_in_value,
            loan_term_months, interest_rate, monthly_payment, credit_score_range,
            annual_income, employment_status, loan_offers, status, created_at, updated_at
        )
        SELECT 
            id, user_id, deal_id, loan_amount, down_payment, trade_in_value,
            loan_term_months, interest_rate, monthly_payment, credit_score_range,
            annual_income, employment_status, loan_offers, status::loanstatus, created_at, updated_at
        FROM loan_applications_backup
    """)

    # Drop the backup table
    op.drop_table("loan_applications_backup")

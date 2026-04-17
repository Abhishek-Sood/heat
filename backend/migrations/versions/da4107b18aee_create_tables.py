"""create tables

Revision ID: da4107b18aee
Revises: 
Create Date: 2026-04-07 16:17:51.981905

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da4107b18aee'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table first (required for foreign keys)
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("username", sa.String(255), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("medical_license_id", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("dob", sa.Date(), nullable=False),
        sa.Column("gender", sa.String(), nullable=False),
        sa.Column("contact", sa.String(), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "vitals",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(), nullable=True),
    )

    op.create_table(
        "lab_results",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("test_name", sa.String(), nullable=True),
        sa.Column("result", sa.String(), nullable=True),
        sa.Column("unit", sa.String(), nullable=True),
        sa.Column("reference_range", sa.String(), nullable=True),
    )

    op.create_table(
        "medications",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("dosage", sa.String(), nullable=True),
        sa.Column("frequency", sa.String(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
    )

    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=True),
        sa.Column("report_type", sa.String(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=True),
        sa.Column("vital_type", sa.String(), nullable=True),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("threshold", sa.Float(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("resolved", sa.Boolean(), nullable=True),
    )

    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=True),
        sa.Column("session_id", sa.String(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id"), nullable=True),
        sa.Column("sender", sa.String(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("alerts")
    op.drop_table("reports")
    op.drop_table("medications")
    op.drop_table("lab_results")
    op.drop_table("vitals")
    op.drop_table("patients")
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table("users")

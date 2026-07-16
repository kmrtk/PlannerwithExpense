"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_user_id", "user", ["id"])
    op.create_index("ix_user_email", "user", ["email"], unique=True)

    op.create_table(
        "schedule",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=True),
        sa.Column("memo", sa.String(1000), nullable=True),
        sa.Column("recurrence_type", sa.String(10), nullable=False, server_default="none"),
        sa.Column("recurrence_end", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_schedule_id", "schedule", ["id"])
    op.create_index("ix_schedule_user_id", "schedule", ["user_id"])

    op.create_table(
        "expense",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(10), nullable=False, server_default="expense"),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("category", sa.String(255), nullable=False),
        sa.Column("memo", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_expense_id", "expense", ["id"])
    op.create_index("ix_expense_user_id", "expense", ["user_id"])

    op.create_table(
        "budget",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("savings_target", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "year", "month", name="uq_budget_user_year_month"),
    )
    op.create_index("ix_budget_id", "budget", ["id"])
    op.create_index("ix_budget_user_id", "budget", ["user_id"])


def downgrade() -> None:
    op.drop_table("budget")
    op.drop_table("expense")
    op.drop_table("schedule")
    op.drop_table("user")

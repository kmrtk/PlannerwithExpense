"""add expense.schedule_id

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("expense", sa.Column("schedule_id", sa.Integer(), nullable=True))
    op.create_index("ix_expense_schedule_id", "expense", ["schedule_id"])
    op.create_foreign_key(
        "fk_expense_schedule_id_schedule",
        "expense",
        "schedule",
        ["schedule_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_expense_schedule_id_schedule", "expense", type_="foreignkey")
    op.drop_index("ix_expense_schedule_id", table_name="expense")
    op.drop_column("expense", "schedule_id")

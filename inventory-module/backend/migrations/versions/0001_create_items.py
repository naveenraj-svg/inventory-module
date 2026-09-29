"""create items

Revision ID: 0001_create_items
Revises:
Create Date: 2026-01-01 10:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_create_items"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("uom", sa.String(20), nullable=False),
        sa.Column("reorder_level", sa.Numeric(14, 3), nullable=False, server_default="0"),
        sa.Column("unit_cost", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_items_code", "items", ["code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_items_code", table_name="items")
    op.drop_table("items")

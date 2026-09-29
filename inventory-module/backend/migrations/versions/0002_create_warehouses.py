"""create warehouses

Revision ID: 0002_create_warehouses
Revises: 0001_create_items
Create Date: 2026-01-02 10:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_create_warehouses"
down_revision: Union[str, None] = "0001_create_items"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "warehouses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_warehouses_name", "warehouses", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_warehouses_name", table_name="warehouses")
    op.drop_table("warehouses")

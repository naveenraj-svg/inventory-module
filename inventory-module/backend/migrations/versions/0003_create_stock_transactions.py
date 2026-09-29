"""create stock_transactions

Revision ID: 0003_create_stock_transactions
Revises: 0002_create_warehouses
Create Date: 2026-01-03 10:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_create_stock_transactions"
down_revision: Union[str, None] = "0002_create_warehouses"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stock_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("items.id"), nullable=False),
        sa.Column(
            "warehouse_id", sa.Integer(), sa.ForeignKey("warehouses.id"), nullable=False
        ),
        sa.Column("transaction_type", sa.String(3), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("unit_cost", sa.Numeric(14, 2), nullable=True),
        sa.Column("supplier", sa.String(200), nullable=True),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "quantity > 0", name="ck_stock_transactions_quantity_positive"
        ),
        sa.CheckConstraint(
            "transaction_type IN ('IN', 'OUT')",
            name="ck_stock_transactions_type_valid",
        ),
    )
    op.create_index(
        "ix_stock_transactions_item_id", "stock_transactions", ["item_id"]
    )
    op.create_index(
        "ix_stock_transactions_warehouse_id", "stock_transactions", ["warehouse_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_stock_transactions_warehouse_id", table_name="stock_transactions")
    op.drop_index("ix_stock_transactions_item_id", table_name="stock_transactions")
    op.drop_table("stock_transactions")

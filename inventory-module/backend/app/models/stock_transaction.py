from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

IN = "IN"
OUT = "OUT"


class StockTransaction(Base):
    __tablename__ = "stock_transactions"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_stock_transactions_quantity_positive"),
        CheckConstraint(
            "transaction_type IN ('IN', 'OUT')",
            name="ck_stock_transactions_type_valid",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), index=True)
    transaction_type: Mapped[str] = mapped_column(String(3))
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    supplier: Mapped[str | None] = mapped_column(String(200), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    item = relationship("Item")
    warehouse = relationship("Warehouse")

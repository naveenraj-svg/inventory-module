from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _StockMovementBase(BaseModel):
    item_id: int = Field(gt=0)
    warehouse_id: int = Field(gt=0)
    quantity: Decimal = Field(gt=0, max_digits=14, decimal_places=3)
    transaction_date: date = Field(default_factory=date.today)
    remarks: str | None = Field(default=None, max_length=1000)

    @field_validator("remarks", mode="before")
    @classmethod
    def clean_remarks(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v


class StockInCreate(_StockMovementBase):
    unit_cost: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    supplier: str | None = Field(default=None, max_length=200)

    @field_validator("supplier", mode="before")
    @classmethod
    def clean_supplier(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v


class StockOutCreate(_StockMovementBase):
    pass


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    item_code: str
    item_name: str
    warehouse_id: int
    warehouse_name: str
    uom: str
    transaction_type: Literal["IN", "OUT"]
    quantity: float
    unit_cost: float | None
    supplier: str | None
    transaction_date: date
    remarks: str | None
    created_at: datetime


class AvailableStockResponse(BaseModel):
    item_id: int
    warehouse_id: int
    uom: str
    available: float


class CurrentStockRow(BaseModel):
    item_id: int
    item_code: str
    item_name: str
    category: str | None
    warehouse_id: int
    warehouse_name: str
    uom: str
    quantity: float
    reorder_level: float
    status: Literal["NORMAL", "LOW"]


class StockSummary(BaseModel):
    total_items: int
    total_warehouses: int
    low_stock_count: int
    total_transactions: int

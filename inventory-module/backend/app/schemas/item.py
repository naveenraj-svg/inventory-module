from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ItemCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    uom: str = Field(min_length=1, max_length=20)
    reorder_level: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=3)
    unit_cost: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=2)
    is_active: bool = True

    @field_validator("code", "uom", mode="before")
    @classmethod
    def clean_upper(cls, v):
        return v.strip().upper() if isinstance(v, str) else v

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("category", mode="before")
    @classmethod
    def clean_category(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    category: str | None
    uom: str
    reorder_level: float
    unit_cost: float
    is_active: bool
    created_at: datetime

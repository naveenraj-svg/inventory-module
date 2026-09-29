from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WarehouseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    location: str | None = Field(default=None, max_length=255)
    is_active: bool = True

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("location", mode="before")
    @classmethod
    def clean_location(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v


class WarehouseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str | None
    is_active: bool
    created_at: datetime

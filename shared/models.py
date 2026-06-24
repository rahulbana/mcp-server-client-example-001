"""Shared Pydantic models used by both server and client."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Unit(str, Enum):
    KG = "kg"
    GRAM = "gram"
    LITRE = "litre"
    ML = "ml"
    DOZEN = "dozen"
    PIECE = "piece"
    PACK = "pack"
    BOX = "box"


class Category(str, Enum):
    FRUIT = "fruit"
    VEGETABLE = "vegetable"
    GROCERY = "grocery"
    DAIRY = "dairy"
    BEVERAGE = "beverage"
    OTHER = "other"


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    category: Category
    quantity: float = Field(..., gt=0)
    unit: Unit
    price_per_unit: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=512)

    @field_validator("name")
    @classmethod
    def normalise_name(cls, v: str) -> str:
        return v.strip().lower()


class ItemUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[Unit] = None
    price_per_unit: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=512)


class ItemOut(BaseModel):
    id: int
    name: str
    category: Category
    quantity: float
    unit: Unit
    price_per_unit: Optional[float]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ItemList(BaseModel):
    items: list[ItemOut]
    total: int


class ToolError(BaseModel):
    error: str
    detail: Optional[str] = None

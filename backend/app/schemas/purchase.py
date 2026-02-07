from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PurchaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: Decimal
    currency: str
    category: str
    note: str | None
    purchase_date: date


class PurchaseCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3, default="USD")
    category: str = Field(min_length=1, max_length=64)
    note: str | None = Field(default=None, max_length=2000)
    purchase_date: date


class PurchasePatch(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    category: str | None = Field(default=None, min_length=1, max_length=64)
    note: str | None = Field(default=None, max_length=2000)
    purchase_date: date | None = None


class PurchaseSummaryDay(BaseModel):
    date: date
    total: Decimal


class PurchaseSummaryCategory(BaseModel):
    category: str
    total: Decimal


class PurchaseSummaryResponse(BaseModel):
    range: dict[str, date]
    total: Decimal
    by_day: list[PurchaseSummaryDay]
    by_category: list[PurchaseSummaryCategory]

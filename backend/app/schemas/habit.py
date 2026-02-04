from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class HabitTypeEnum(str, Enum):
    checkbox = "checkbox"
    timer = "timer"
    both = "both"


class HabitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    key: str
    title: str
    type: HabitTypeEnum
    target_minutes_per_day: int | None
    active: bool
    sort_order: int


class HabitCreate(BaseModel):
    key: str = Field(pattern=r"^[a-z0-9_]{2,32}$")
    title: str = Field(min_length=1, max_length=128)
    type: HabitTypeEnum
    target_minutes_per_day: int | None = Field(default=None, ge=0, le=1440)
    sort_order: int = 0


class HabitPatch(BaseModel):
    key: str | None = Field(default=None, pattern=r"^[a-z0-9_]{2,32}$")
    title: str | None = Field(default=None, min_length=1, max_length=128)
    type: HabitTypeEnum | None = None
    target_minutes_per_day: int | None = Field(default=None, ge=0, le=1440)
    active: bool | None = None
    sort_order: int | None = None

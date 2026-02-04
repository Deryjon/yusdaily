from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DayHabitRead(BaseModel):
    habit_id: str
    key: str
    title: str
    done: bool
    minutes: int
    comment: str


class DayRead(BaseModel):
    date: date
    note: str
    total_minutes: int
    habits: list[DayHabitRead]


class DayHabitInput(BaseModel):
    habit_id: UUID
    done: bool = False
    minutes: int = Field(default=0, ge=0)
    comment: str = Field(default="", max_length=2000)


class DayUpsertRequest(BaseModel):
    note: str = Field(default="", max_length=5000)
    habits: list[DayHabitInput] = Field(default_factory=list)


class DayHabitPatchRequest(BaseModel):
    done: bool | None = None
    minutes_delta: int | None = None
    minutes_set: int | None = Field(default=None, ge=0)
    comment: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_one_field(self) -> "DayHabitPatchRequest":
        provided = [
            self.done is not None,
            self.minutes_delta is not None,
            self.minutes_set is not None,
            self.comment is not None,
        ]
        if sum(provided) != 1:
            raise ValueError("Exactly one field must be provided")
        return self


class DayHabitPatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    habit_id: UUID
    done: bool
    minutes: int
    comment: str

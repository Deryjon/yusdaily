from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class StatsRange(BaseModel):
    from_date: date
    to_date: date


class SummaryHabitItem(BaseModel):
    habit_id: str
    key: str
    minutes: int
    done_days: int


class StatsSummaryResponse(BaseModel):
    range: dict[str, date]
    total_minutes: int
    done_days: int
    by_habit: list[SummaryHabitItem]


class CalendarDayItem(BaseModel):
    date: date
    total_minutes: int
    done: bool


class CalendarResponse(BaseModel):
    month: str
    days: list[CalendarDayItem]


class StreakHabitItem(BaseModel):
    habit_id: str
    key: str
    streak: int


class StreaksResponse(BaseModel):
    overall: int
    by_habit: list[StreakHabitItem]

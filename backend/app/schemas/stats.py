from datetime import datetime
from pydantic import BaseModel


class TaskNoDeadline(BaseModel):
    id: int
    title: str


class TaskWithDeadline(BaseModel):
    id: int
    title: str
    deadline: datetime | None


class TodayResponse(BaseModel):
    completed: int
    pending: int
    no_deadline: list[TaskNoDeadline]
    with_deadline: list[TaskWithDeadline]


class ProgressResponse(BaseModel):
    completed: int
    pending: int
    percent: int
    streak: int

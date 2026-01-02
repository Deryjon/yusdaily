from datetime import datetime
from pydantic import BaseModel, Field

from app.models import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    has_deadline: bool = False
    deadline: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    status: TaskStatus | None = None
    deadline: datetime | None = None


class TaskRead(BaseModel):
    id: int
    title: str
    status: TaskStatus
    has_deadline: bool
    deadline: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True

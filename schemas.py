from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    has_deadline: bool = False
    deadline: Optional[datetime] = None
    status: str = "new"

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    has_deadline: Optional[bool] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None

class Task(TaskBase):
    id: int

    class Config:
        from_attributes = True
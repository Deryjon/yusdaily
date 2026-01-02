# app/api/tasks.py
from fastapi import APIRouter
from typing import List
from app.schemas.task import TaskSchema  # если у тебя есть Pydantic схема
# из базы можно потом импортировать модель Task и сессии SQLAlchemy

router = APIRouter()

@router.get("/tasks", response_model=List[TaskSchema])
def get_tasks():
    # временно заглушка
    return []

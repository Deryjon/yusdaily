from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import DailyStat, Idea, Task, TaskStatus, User
from app.schemas import (
    IdeaCreatePayload,
    IdeaRead,
    ProfileRead,
    ProgressResponse,
    TaskCreate,
    TaskRead,
    TaskUpdate,
    TodayResponse,
    UserCreate,
    UserRead,
)
from app.services.stats import ensure_stats_range, get_day_bounds, upsert_daily_stat
from app.services.webapp_auth import verify_init_data


router = APIRouter()


class WebAppAuthRequest(BaseModel):
    initData: str


@router.get("/api/tg/profile", response_model=UserRead)
async def get_profile(phone: str, session: AsyncSession = Depends(get_session)) -> User:
    result = await session.execute(select(User).where(User.phone == phone))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return profile


@router.post("/api/tg/profile", response_model=UserRead)
async def create_or_update_profile(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> User:
    result = await session.execute(select(User).where(User.phone == payload.phone))
    profile = result.scalar_one_or_none()
    if profile:
        profile.username = payload.username
        profile.phone = payload.phone
        profile.first_name = payload.first_name
        profile.last_name = payload.last_name
        profile.birth_year = payload.birth_year
        profile.gender = payload.gender
        await session.commit()
        await session.refresh(profile)
        return profile

    profile = User(
        username=payload.username,
        phone=payload.phone,
        first_name=payload.first_name,
        last_name=payload.last_name,
        birth_year=payload.birth_year,
        gender=payload.gender,
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


@router.get("/api/profile", response_model=ProfileRead)
async def get_profile_current(user: User = Depends(get_current_user)) -> User:
    return user


@router.get("/api/today", response_model=TodayResponse)
async def get_today(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    today = date.today()
    await upsert_daily_stat(session, user.id, today)
    await session.commit()

    day_start, day_end = get_day_bounds(today)
    result = await session.execute(
        select(Task).where(
            Task.user_id == user.id,
            Task.has_deadline.is_(True),
            Task.deadline >= day_start,
            Task.deadline < day_end,
        )
    )
    deadline_tasks = result.scalars().all()
    completed = sum(1 for task in deadline_tasks if task.status == TaskStatus.done)
    pending_tasks = [task for task in deadline_tasks if task.status != TaskStatus.done]

    result = await session.execute(
        select(Task).where(
            Task.user_id == user.id,
            Task.has_deadline.is_(False),
            Task.status != TaskStatus.done,
        )
    )
    no_deadline_tasks = result.scalars().all()

    return {
        "completed": completed,
        "pending": len(pending_tasks),
        "no_deadline": [
            {"id": task.id, "title": task.title} for task in no_deadline_tasks
        ],
        "with_deadline": [
            {
                "id": task.id,
                "title": task.title,
                "deadline": task.deadline,
            }
            for task in pending_tasks
        ],
    }


@router.get("/api/progress", response_model=ProgressResponse)
async def get_progress(
    period: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, int]:
    if period == "week":
        days = 7
    elif period == "month":
        days = 30
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid period")

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    await ensure_stats_range(session, user.id, start_date, end_date)
    await session.commit()

    result = await session.execute(
        select(DailyStat).where(
            DailyStat.user_id == user.id,
            DailyStat.date >= start_date,
            DailyStat.date <= end_date,
        )
    )
    stats = result.scalars().all()
    total = sum(stat.total_tasks for stat in stats)
    completed = sum(stat.completed_tasks for stat in stats)
    pending = total - completed
    percent = round((completed / total) * 100) if total else 0

    stats_by_date = {stat.date: stat for stat in stats}
    streak = 0
    cursor = end_date
    while True:
        stat = stats_by_date.get(cursor)
        if not stat or stat.completed_tasks <= 0:
            break
        streak += 1
        cursor = cursor - timedelta(days=1)

    return {
        "completed": completed,
        "pending": pending,
        "percent": percent,
        "streak": streak,
    }


@router.post("/api/ideas")
async def create_idea(
    payload: IdeaCreatePayload,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    idea = Idea(user_id=user.id, text=payload.text, source=payload.source)
    session.add(idea)
    await session.commit()
    return {"status": "ok"}


@router.get("/api/ideas", response_model=list[IdeaRead])
async def list_ideas(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Idea]:
    result = await session.execute(
        select(Idea).where(Idea.user_id == user.id).order_by(Idea.created_at.desc())
    )
    return list(result.scalars().all())


@router.delete("/api/ideas/{idea_id}")
async def delete_idea(
    idea_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    result = await session.execute(
        select(Idea).where(Idea.id == idea_id, Idea.user_id == user.id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    session.delete(idea)
    await session.commit()
    return {"status": "ok"}


@router.get("/api/tasks", response_model=list[TaskRead])
async def list_tasks(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Task]:
    result = await session.execute(
        select(Task).where(Task.user_id == user.id).order_by(Task.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("/api/tasks", response_model=TaskRead)
async def create_task(
    payload: TaskCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Task:
    has_deadline = payload.has_deadline
    if payload.deadline is not None:
        has_deadline = True

    task = Task(
        user_id=user.id,
        title=payload.title,
        status=TaskStatus.inbox,
        has_deadline=has_deadline,
        deadline=payload.deadline,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.patch("/api/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    payload: TaskUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Task:
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    fields_set = getattr(payload, "model_fields_set", getattr(payload, "__fields_set__", set()))

    if "title" in fields_set and payload.title is not None:
        task.title = payload.title
    if "status" in fields_set and payload.status is not None:
        task.status = payload.status
    if "deadline" in fields_set:
        task.deadline = payload.deadline
        task.has_deadline = payload.deadline is not None

    await session.commit()
    await session.refresh(task)
    return task


@router.delete("/api/tasks/{task_id}")
async def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    session.delete(task)
    await session.commit()
    return {"status": "ok"}


@router.post("/api/tasks/from-idea/{idea_id}", response_model=TaskRead)
async def task_from_idea(
    idea_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Task:
    result = await session.execute(
        select(Idea).where(Idea.id == idea_id, Idea.user_id == user.id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    task = Task(
        user_id=user.id,
        title=idea.text,
        status=TaskStatus.inbox,
        has_deadline=False,
    )
    session.add(task)
    session.delete(idea)
    await session.commit()
    await session.refresh(task)
    return task


@router.post("/api/tg/auth")
async def auth_user() -> dict[str, bool]:
    return {"ok": True}


@router.post("/tg/webapp/auth")
async def webapp_auth(payload: WebAppAuthRequest) -> dict[str, object]:
    bot_token = os.getenv("BOT_TOKEN", "")
    if not bot_token:
        return {"ok": False, "error": "BOT_TOKEN is not configured"}

    ok, result = verify_init_data(payload.initData, bot_token)
    if not ok:
        return {"ok": False, "error": result}

    user = result.get("user") if isinstance(result, dict) else None
    return {"ok": True, "user": user}


@router.get("/api/tg/reminders/{reminder_type}")
async def get_reminders() -> dict[str, list]:
    return {"items": []}


from app.api.admin import router as admin_router
router.include_router(admin_router)

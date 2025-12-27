from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.db.session import get_session
from app.models import DailyStat, Idea, Task, TaskStatus, User
from app.schemas import IdeaCreate, UserCreate, UserRead
from app.services.webapp_auth import verify_init_data


router = APIRouter()


class WebAppAuthRequest(BaseModel):
    initData: str


@router.get("/api/tg/profile", response_model=UserRead)
async def get_profile(tg_id: int, session: AsyncSession = Depends(get_session)) -> User:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return profile


@router.post("/api/tg/profile", response_model=UserRead)
async def create_or_update_profile(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> User:
    result = await session.execute(select(User).where(User.tg_id == payload.tg_id))
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
        tg_id=payload.tg_id,
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


@router.get("/today")
async def get_today(tg_id: int, session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    result = await session.execute(select(Task).where(Task.user_id == user.id))
    tasks = result.scalars().all()

    done_count = sum(1 for task in tasks if task.status == TaskStatus.done)
    pending = [task for task in tasks if task.status != TaskStatus.done]
    without_deadline = [task for task in pending if not task.has_deadline]
    with_deadline = [task for task in pending if task.has_deadline]

    lines = [
        "📅 План на сегодня",
        "",
        f"✅ Выполнено: {done_count}",
        f"⏳ Не выполнено: {len(pending)}",
        "",
        "🟢 Без дедлайна",
    ]
    if without_deadline:
        lines.extend([f"• {task.title}" for task in without_deadline])
    else:
        lines.append("• Нет задач")

    lines.extend(["", "🔴 С дедлайном"])
    if with_deadline:
        for task in with_deadline:
            deadline_str = ""
            if task.deadline:
                deadline_str = f" (до {task.deadline:%H:%M})"
            lines.append(f"• {task.title}{deadline_str}")
    else:
        lines.append("• Нет задач")

    return {"text": "\n".join(lines)}


@router.get("/progress")
async def get_progress(
    tg_id: int,
    period: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    now = datetime.utcnow()
    if period == "week":
        start = now - timedelta(days=7)
        title = "неделю"
    elif period == "month":
        start = now - timedelta(days=30)
        title = "месяц"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid period")

    result = await session.execute(
        select(Task).where(Task.user_id == user.id, Task.created_at >= start)
    )
    tasks = result.scalars().all()
    done_count = sum(1 for task in tasks if task.status == TaskStatus.done)
    total_count = len(tasks)
    pending_count = total_count - done_count

    result = await session.execute(
        select(DailyStat).where(DailyStat.user_id == user.id, DailyStat.date >= start.date())
    )
    stats = {stat.date: stat for stat in result.scalars().all()}
    streak = 0
    cursor = now.date()
    while True:
        stat = stats.get(cursor)
        if not stat or stat.completed_tasks <= 0:
            break
        streak += 1
        cursor = cursor - timedelta(days=1)

    progress_percent = 0
    if total_count:
        progress_percent = round((done_count / total_count) * 100)

    lines = [
        f"📊 Прогресс за {title}",
        "",
        f"✅ Выполнено: {done_count}",
        f"⏳ Не выполнено: {pending_count}",
        f"🔥 Серия дней: {streak}",
        "",
        f"📈 Прогресс: {progress_percent}%",
    ]
    return {"text": "\n".join(lines)}


@router.post("/ideas")
async def create_idea(
    payload: IdeaCreate,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    result = await session.execute(select(User).where(User.tg_id == payload.tg_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    idea = Idea(user_id=user.id, text=payload.text, source=payload.source)
    session.add(idea)
    await session.commit()
    return {"text": "✅ Задумка сохранена"}


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

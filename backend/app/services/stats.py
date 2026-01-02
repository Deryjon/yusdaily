from datetime import date, datetime, timedelta, time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DailyStat, Task, TaskStatus


def get_day_bounds(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min)
    end = start + timedelta(days=1)
    return start, end


async def upsert_daily_stat(session: AsyncSession, user_id: int, day: date) -> DailyStat:
    day_start, day_end = get_day_bounds(day)
    result = await session.execute(
        select(Task).where(
            Task.user_id == user_id,
            Task.has_deadline.is_(True),
            Task.deadline >= day_start,
            Task.deadline < day_end,
        )
    )
    tasks = result.scalars().all()
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == TaskStatus.done)

    result = await session.execute(
        select(DailyStat).where(DailyStat.user_id == user_id, DailyStat.date == day)
    )
    stat = result.scalar_one_or_none()
    if stat:
        stat.total_tasks = total_tasks
        stat.completed_tasks = completed_tasks
    else:
        stat = DailyStat(
            user_id=user_id,
            date=day,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
        )
        session.add(stat)

    return stat


async def ensure_stats_range(
    session: AsyncSession,
    user_id: int,
    start_date: date,
    end_date: date,
) -> None:
    cursor = start_date
    while cursor <= end_date:
        await upsert_daily_stat(session, user_id, cursor)
        cursor = cursor + timedelta(days=1)

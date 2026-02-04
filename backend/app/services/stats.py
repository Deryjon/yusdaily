from __future__ import annotations

import calendar
from datetime import date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import DailyLog, Habit, HabitLog, User


def is_habit_done(done: bool, minutes: int, target_minutes: int | None) -> bool:
    if done:
        return True
    if target_minutes is None:
        return False
    return minutes >= target_minutes


async def get_summary(
    session: AsyncSession,
    user: User,
    from_date: date,
    to_date: date,
) -> dict[str, object]:
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="'from' must be <= 'to'")

    settings = get_settings()
    total_minutes_query = await session.execute(
        select(func.coalesce(func.sum(HabitLog.minutes), 0))
        .select_from(HabitLog)
        .join(DailyLog, HabitLog.daily_log_id == DailyLog.id)
        .where(DailyLog.user_id == user.id, DailyLog.date >= from_date, DailyLog.date <= to_date)
    )
    total_minutes = int(total_minutes_query.scalar_one())

    daily_totals_query = await session.execute(
        select(DailyLog.date, func.coalesce(func.sum(HabitLog.minutes), 0))
        .select_from(DailyLog)
        .outerjoin(HabitLog, HabitLog.daily_log_id == DailyLog.id)
        .where(DailyLog.user_id == user.id, DailyLog.date >= from_date, DailyLog.date <= to_date)
        .group_by(DailyLog.date)
    )
    done_days = sum(1 for _, minutes in daily_totals_query.all() if int(minutes or 0) >= settings.daily_done_minutes)

    habits_query = await session.execute(
        select(Habit)
        .where(Habit.user_id == user.id, Habit.active.is_(True))
        .order_by(Habit.sort_order.asc(), Habit.created_at.asc())
    )
    habits = habits_query.scalars().all()

    per_habit_query = await session.execute(
        select(
            HabitLog.habit_id,
            func.coalesce(func.sum(HabitLog.minutes), 0).label("minutes"),
        )
        .select_from(HabitLog)
        .join(DailyLog, HabitLog.daily_log_id == DailyLog.id)
        .where(DailyLog.user_id == user.id, DailyLog.date >= from_date, DailyLog.date <= to_date)
        .group_by(HabitLog.habit_id)
    )
    minutes_by_habit = {str(row.habit_id): int(row.minutes or 0) for row in per_habit_query}

    done_per_habit_query = await session.execute(
        select(HabitLog.habit_id, DailyLog.date, HabitLog.done, HabitLog.minutes)
        .select_from(HabitLog)
        .join(DailyLog, HabitLog.daily_log_id == DailyLog.id)
        .where(DailyLog.user_id == user.id, DailyLog.date >= from_date, DailyLog.date <= to_date)
    )
    done_days_map: dict[str, set[date]] = {}
    habits_map = {str(h.id): h for h in habits}
    for habit_id, day, done, minutes in done_per_habit_query:
        habit_key = str(habit_id)
        habit = habits_map.get(habit_key)
        if not habit:
            continue
        if is_habit_done(bool(done), int(minutes or 0), habit.target_minutes_per_day):
            done_days_map.setdefault(habit_key, set()).add(day)

    by_habit = [
        {
            "habit_id": str(habit.id),
            "key": habit.key,
            "minutes": minutes_by_habit.get(str(habit.id), 0),
            "done_days": len(done_days_map.get(str(habit.id), set())),
        }
        for habit in habits
    ]

    return {
        "range": {"from": from_date, "to": to_date},
        "total_minutes": total_minutes,
        "done_days": done_days,
        "by_habit": by_habit,
    }


async def get_calendar(session: AsyncSession, user: User, month: str) -> dict[str, object]:
    year, month_num = month.split("-")
    year_int = int(year)
    month_int = int(month_num)
    _, last_day = calendar.monthrange(year_int, month_int)
    start = date(year_int, month_int, 1)
    end = date(year_int, month_int, last_day)

    rows = await session.execute(
        select(DailyLog.date, func.coalesce(func.sum(HabitLog.minutes), 0).label("total_minutes"))
        .select_from(DailyLog)
        .outerjoin(HabitLog, HabitLog.daily_log_id == DailyLog.id)
        .where(DailyLog.user_id == user.id, DailyLog.date >= start, DailyLog.date <= end)
        .group_by(DailyLog.date)
    )
    totals = {row.date: int(row.total_minutes or 0) for row in rows}
    settings = get_settings()

    days = []
    for day_number in range(1, last_day + 1):
        day_date = date(year_int, month_int, day_number)
        total = totals.get(day_date, 0)
        days.append(
            {
                "date": day_date,
                "total_minutes": total,
                "done": total >= settings.daily_done_minutes,
            }
        )
    return {"month": month, "days": days}


async def get_streaks(session: AsyncSession, user: User) -> dict[str, object]:
    try:
        tz = ZoneInfo(user.timezone)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")
    today_local = datetime.now(tz).date()

    rows = await session.execute(
        select(DailyLog.date, func.coalesce(func.sum(HabitLog.minutes), 0).label("total_minutes"))
        .select_from(DailyLog)
        .outerjoin(HabitLog, HabitLog.daily_log_id == DailyLog.id)
        .where(DailyLog.user_id == user.id, DailyLog.date <= today_local)
        .group_by(DailyLog.date)
    )
    day_totals = {row.date: int(row.total_minutes or 0) for row in rows}

    settings = get_settings()
    overall = 0
    cursor = today_local
    while day_totals.get(cursor, 0) >= settings.daily_done_minutes:
        overall += 1
        cursor = date.fromordinal(cursor.toordinal() - 1)

    habits_result = await session.execute(
        select(Habit)
        .where(Habit.user_id == user.id, Habit.active.is_(True))
        .order_by(Habit.sort_order.asc(), Habit.created_at.asc())
    )
    habits = habits_result.scalars().all()
    habit_rows = await session.execute(
        select(HabitLog.habit_id, DailyLog.date, HabitLog.done, HabitLog.minutes)
        .select_from(HabitLog)
        .join(DailyLog, HabitLog.daily_log_id == DailyLog.id)
        .where(DailyLog.user_id == user.id, DailyLog.date <= today_local)
    )
    done_map: dict[str, set[date]] = {}
    habits_map = {str(h.id): h for h in habits}
    for habit_id, day, done, minutes in habit_rows:
        habit_key = str(habit_id)
        habit = habits_map.get(habit_key)
        if not habit:
            continue
        if is_habit_done(bool(done), int(minutes or 0), habit.target_minutes_per_day):
            done_map.setdefault(habit_key, set()).add(day)

    by_habit = []
    for habit in habits:
        streak = 0
        cursor = today_local
        done_days = done_map.get(str(habit.id), set())
        while cursor in done_days:
            streak += 1
            cursor = date.fromordinal(cursor.toordinal() - 1)
        by_habit.append({"habit_id": str(habit.id), "key": habit.key, "streak": streak})

    return {"overall": overall, "by_habit": by_habit}

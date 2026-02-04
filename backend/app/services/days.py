from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DailyLog, Habit, HabitLog, User
from app.schemas.day import DayHabitPatchRequest, DayUpsertRequest


def _habit_payload(habit: Habit, habit_log: HabitLog | None) -> dict[str, object]:
    return {
        "habit_id": str(habit.id),
        "key": habit.key,
        "title": habit.title,
        "done": bool(habit_log.done) if habit_log else False,
        "minutes": int(habit_log.minutes or 0) if habit_log else 0,
        "comment": habit_log.comment or "" if habit_log else "",
    }


async def _get_habits(session: AsyncSession, user: User) -> list[Habit]:
    result = await session.execute(
        select(Habit)
        .where(Habit.user_id == user.id, Habit.active.is_(True))
        .order_by(Habit.sort_order.asc(), Habit.created_at.asc())
    )
    return list(result.scalars().all())


async def _get_daily_log(session: AsyncSession, user: User, log_date: date) -> DailyLog | None:
    result = await session.execute(
        select(DailyLog).where(DailyLog.user_id == user.id, DailyLog.date == log_date)
    )
    return result.scalar_one_or_none()


async def get_day(session: AsyncSession, user: User, log_date: date) -> dict[str, object]:
    habits = await _get_habits(session, user)
    daily_log = await _get_daily_log(session, user, log_date)
    habit_logs_by_id: dict[str, HabitLog] = {}
    note = ""

    if daily_log:
        note = daily_log.note or ""
        logs_result = await session.execute(
            select(HabitLog).where(HabitLog.daily_log_id == daily_log.id)
        )
        habit_logs_by_id = {str(item.habit_id): item for item in logs_result.scalars().all()}

    habits_payload = [_habit_payload(habit, habit_logs_by_id.get(str(habit.id))) for habit in habits]
    total_minutes = sum(int(item["minutes"]) for item in habits_payload)

    return {
        "date": log_date,
        "note": note,
        "total_minutes": total_minutes,
        "habits": habits_payload,
    }


async def upsert_day(
    session: AsyncSession,
    user: User,
    log_date: date,
    payload: DayUpsertRequest,
) -> dict[str, object]:
    async with session.begin():
        daily_log = await _get_daily_log(session, user, log_date)
        if not daily_log:
            daily_log = DailyLog(user_id=user.id, date=log_date, note=payload.note or "")
            session.add(daily_log)
            await session.flush()
        else:
            daily_log.note = payload.note or ""

        if payload.habits:
            habit_ids = [item.habit_id for item in payload.habits]
            habits_result = await session.execute(
                select(Habit).where(Habit.user_id == user.id, Habit.id.in_(habit_ids))
            )
            habits_map = {str(h.id): h for h in habits_result.scalars().all()}
            if len(habits_map) != len(set(str(item.habit_id) for item in payload.habits)):
                raise HTTPException(status_code=400, detail="habit_id must belong to user")

            existing_result = await session.execute(
                select(HabitLog).where(
                    HabitLog.daily_log_id == daily_log.id,
                    HabitLog.habit_id.in_(habit_ids),
                )
            )
            existing_map = {str(log.habit_id): log for log in existing_result.scalars().all()}

            for item in payload.habits:
                row = existing_map.get(str(item.habit_id))
                if not row:
                    row = HabitLog(daily_log_id=daily_log.id, habit_id=item.habit_id)
                    session.add(row)
                row.done = item.done
                row.minutes = item.minutes
                row.comment = item.comment or ""

    return await get_day(session, user, log_date)


async def patch_day_habit(
    session: AsyncSession,
    user: User,
    log_date: date,
    habit_id: UUID,
    payload: DayHabitPatchRequest,
) -> dict[str, object]:
    async with session.begin():
        habit_result = await session.execute(
            select(Habit).where(Habit.id == habit_id, Habit.user_id == user.id)
        )
        habit = habit_result.scalar_one_or_none()
        if not habit:
            raise HTTPException(status_code=404, detail="Habit not found")

        daily_log = await _get_daily_log(session, user, log_date)
        if not daily_log:
            daily_log = DailyLog(user_id=user.id, date=log_date, note="")
            session.add(daily_log)
            await session.flush()

        row_result = await session.execute(
            select(HabitLog).where(
                and_(
                    HabitLog.daily_log_id == daily_log.id,
                    HabitLog.habit_id == habit.id,
                )
            )
        )
        row = row_result.scalar_one_or_none()
        if not row:
            row = HabitLog(daily_log_id=daily_log.id, habit_id=habit.id, done=False, minutes=0, comment="")
            session.add(row)
            await session.flush()

        if payload.done is not None:
            row.done = payload.done
        if payload.minutes_set is not None:
            row.minutes = max(0, payload.minutes_set)
        if payload.minutes_delta is not None:
            row.minutes = max(0, (row.minutes or 0) + payload.minutes_delta)
        if payload.comment is not None:
            row.comment = payload.comment

    return {
        "habit_id": row.habit_id,
        "done": row.done,
        "minutes": row.minutes,
        "comment": row.comment or "",
    }

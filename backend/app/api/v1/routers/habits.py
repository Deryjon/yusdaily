from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import Habit, User
from app.schemas.habit import HabitCreate, HabitPatch, HabitRead

router = APIRouter()


@router.get("", response_model=list[HabitRead])
async def list_habits(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Habit]:
    result = await session.execute(
        select(Habit)
        .where(Habit.user_id == user.id, Habit.active.is_(True))
        .order_by(Habit.sort_order.asc(), Habit.created_at.asc())
    )
    return list(result.scalars().all())


@router.post("", response_model=HabitRead)
async def create_habit(
    payload: HabitCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Habit:
    habit = Habit(
        user_id=user.id,
        key=payload.key,
        title=payload.title,
        type=payload.type.value,
        target_minutes_per_day=payload.target_minutes_per_day,
        sort_order=payload.sort_order,
        active=True,
    )
    session.add(habit)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Habit key must be unique") from exc
    await session.refresh(habit)
    return habit


@router.patch("/{habit_id}", response_model=HabitRead)
async def patch_habit(
    habit_id: UUID,
    payload: HabitPatch,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Habit:
    result = await session.execute(select(Habit).where(Habit.id == habit_id, Habit.user_id == user.id))
    habit = result.scalar_one_or_none()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if key == "type" and value is not None:
            setattr(habit, key, value.value)
        else:
            setattr(habit, key, value)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Habit key must be unique") from exc
    await session.refresh(habit)
    return habit


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Response:
    result = await session.execute(select(Habit).where(Habit.id == habit_id, Habit.user_id == user.id))
    habit = result.scalar_one_or_none()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    habit.active = False
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

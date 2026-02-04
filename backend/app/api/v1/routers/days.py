from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.day import DayHabitPatchRequest, DayHabitPatchResponse, DayRead, DayUpsertRequest
from app.services.days import get_day, patch_day_habit, upsert_day

router = APIRouter()


@router.get("/{day_date}", response_model=DayRead)
async def get_day_route(
    day_date: date,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return await get_day(session, user, day_date)


@router.put("/{day_date}", response_model=DayRead)
async def put_day_route(
    day_date: date,
    payload: DayUpsertRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return await upsert_day(session, user, day_date, payload)


@router.patch("/{day_date}/habit/{habit_id}", response_model=DayHabitPatchResponse)
async def patch_day_habit_route(
    day_date: date,
    habit_id: UUID,
    payload: DayHabitPatchRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return await patch_day_habit(session, user, day_date, habit_id, payload)

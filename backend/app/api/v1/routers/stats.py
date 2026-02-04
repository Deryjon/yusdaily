from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.stats import CalendarResponse, StatsSummaryResponse, StreaksResponse
from app.services.stats import get_calendar, get_streaks, get_summary

router = APIRouter()


@router.get("/summary", response_model=StatsSummaryResponse)
async def summary(
    from_date: date = Query(alias="from"),
    to_date: date = Query(alias="to"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return await get_summary(session, user, from_date, to_date)


@router.get("/calendar", response_model=CalendarResponse)
async def calendar_view(
    month: str = Query(pattern=r"^\d{4}-\d{2}$"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    try:
        return await get_calendar(session, user, month)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid month") from exc


@router.get("/streaks", response_model=StreaksResponse)
async def streaks(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return await get_streaks(session, user)

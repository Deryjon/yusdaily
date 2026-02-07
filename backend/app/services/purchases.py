from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Purchase, User


def _range_from_period(period: str) -> tuple[date, date]:
    today = date.today()
    if period == "week":
        return today - timedelta(days=6), today
    if period == "month":
        start = today.replace(day=1)
        return start, today
    raise HTTPException(status_code=400, detail="period must be 'week' or 'month'")


async def get_purchase_summary(
    session: AsyncSession,
    user: User,
    period: str,
) -> dict[str, object]:
    from_date, to_date = _range_from_period(period)

    total_query = await session.execute(
        select(func.coalesce(func.sum(Purchase.amount), 0))
        .select_from(Purchase)
        .where(
            Purchase.user_id == user.id,
            Purchase.purchase_date >= from_date,
            Purchase.purchase_date <= to_date,
        )
    )
    total = Decimal(total_query.scalar_one() or 0)

    by_day_query = await session.execute(
        select(Purchase.purchase_date, func.coalesce(func.sum(Purchase.amount), 0).label("total"))
        .where(
            Purchase.user_id == user.id,
            Purchase.purchase_date >= from_date,
            Purchase.purchase_date <= to_date,
        )
        .group_by(Purchase.purchase_date)
        .order_by(Purchase.purchase_date.asc())
    )
    by_day = [{"date": row.purchase_date, "total": Decimal(row.total or 0)} for row in by_day_query.all()]

    by_category_query = await session.execute(
        select(Purchase.category, func.coalesce(func.sum(Purchase.amount), 0).label("total"))
        .where(
            Purchase.user_id == user.id,
            Purchase.purchase_date >= from_date,
            Purchase.purchase_date <= to_date,
        )
        .group_by(Purchase.category)
        .order_by(func.coalesce(func.sum(Purchase.amount), 0).desc())
    )
    by_category = [{"category": row.category, "total": Decimal(row.total or 0)} for row in by_category_query.all()]

    return {
        "range": {"from": from_date, "to": to_date},
        "total": total,
        "by_day": by_day,
        "by_category": by_category,
    }

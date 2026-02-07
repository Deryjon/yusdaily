from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import Purchase, User
from app.schemas.purchase import (
    PurchaseCreate,
    PurchasePatch,
    PurchaseRead,
    PurchaseSummaryResponse,
)
from app.services.purchases import get_purchase_summary

router = APIRouter()


@router.get("", response_model=list[PurchaseRead])
async def list_purchases(
    from_date: date | None = None,
    to_date: date | None = None,
    category: str | None = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Purchase]:
    if from_date and to_date and from_date > to_date:
        raise HTTPException(status_code=400, detail="'from' must be <= 'to'")

    query = select(Purchase).where(Purchase.user_id == user.id)
    if from_date:
        query = query.where(Purchase.purchase_date >= from_date)
    if to_date:
        query = query.where(Purchase.purchase_date <= to_date)
    if category:
        query = query.where(Purchase.category == category)
    result = await session.execute(query.order_by(Purchase.purchase_date.desc(), Purchase.created_at.desc()))
    return list(result.scalars().all())


@router.post("", response_model=PurchaseRead, status_code=status.HTTP_201_CREATED)
async def create_purchase(
    payload: PurchaseCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Purchase:
    purchase = Purchase(
        user_id=user.id,
        amount=payload.amount,
        currency=payload.currency.upper(),
        category=payload.category,
        note=payload.note,
        purchase_date=payload.purchase_date,
    )
    session.add(purchase)
    await session.commit()
    await session.refresh(purchase)
    return purchase


@router.patch("/{purchase_id}", response_model=PurchaseRead)
async def patch_purchase(
    purchase_id: UUID,
    payload: PurchasePatch,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Purchase:
    result = await session.execute(
        select(Purchase).where(Purchase.id == purchase_id, Purchase.user_id == user.id)
    )
    purchase = result.scalar_one_or_none()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if key == "currency" and value is not None:
            setattr(purchase, key, value.upper())
        else:
            setattr(purchase, key, value)
    await session.commit()
    await session.refresh(purchase)
    return purchase


@router.delete("/{purchase_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase(
    purchase_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Response:
    result = await session.execute(
        select(Purchase).where(Purchase.id == purchase_id, Purchase.user_id == user.id)
    )
    purchase = result.scalar_one_or_none()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    await session.delete(purchase)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/summary", response_model=PurchaseSummaryResponse)
async def purchases_summary(
    period: str = "week",
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return await get_purchase_summary(session, user, period)

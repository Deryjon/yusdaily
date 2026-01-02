from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models import User


async def get_current_user(
    x_tg_id: int = Header(..., alias="X-TG-ID"),
    session: AsyncSession = Depends(get_session),
) -> User:
    result = await session.execute(select(User).where(User.tg_id == x_tg_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return user

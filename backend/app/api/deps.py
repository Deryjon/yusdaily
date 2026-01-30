from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models import User
async def get_current_user(
    x_phone: str | None = Header(default=None, alias="X-PHONE"),
    session: AsyncSession = Depends(get_session),
) -> User:
    if not x_phone:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing phone")

    result = await session.execute(select(User).where(User.phone == x_phone))

    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return user

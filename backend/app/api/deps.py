import os

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models import User
from app.services.webapp_auth import verify_init_data


async def get_current_user(
    x_tg_initdata: str | None = Header(default=None, alias="X-TG-INITDATA"),
    session: AsyncSession = Depends(get_session),
) -> User:
    bot_token = os.getenv("BOT_TOKEN", "")
    if not bot_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if not x_tg_initdata:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing init data")
    ok, result = verify_init_data(x_tg_initdata, bot_token)
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid init data")
    user_payload = result.get("user") if isinstance(result, dict) else None
    if not user_payload or user_payload.get("id") is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    tg_id = user_payload["id"]

    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return user

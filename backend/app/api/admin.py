from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin_token(
    authorization: str = Header(..., alias="Authorization"),
) -> None:
    settings = get_settings()
    api_token = getattr(settings, "api_token", None)
    if not api_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    expected = f"Bearer {api_token}"
    if authorization != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


@router.get("/users")
async def list_users(
    _: None = Depends(require_admin_token),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).order_by(User.id.desc()))
    users = result.scalars().all()
    return {"items": [
        {"id": u.id, "created_at": getattr(u, "created_at", None)}
        for u in users
    ]}

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users")
async def list_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).order_by(User.id.desc()))
    users = result.scalars().all()
    return {"items": [
        {"id": u.id, "tg_id": u.tg_id, "created_at": getattr(u, "created_at", None)}
        for u in users
    ]}

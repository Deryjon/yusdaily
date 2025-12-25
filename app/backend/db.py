from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.backend.config import get_backend_settings


def _build_engine():
    settings = get_backend_settings()
    return create_async_engine(settings.database_url, echo=False, future=True)


_engine = _build_engine()
_sessionmaker = async_sessionmaker(bind=_engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with _sessionmaker() as session:
        yield session

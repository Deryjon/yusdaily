from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Tashkent")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")
    habits: Mapped[list["Habit"]] = relationship(back_populates="user")
    daily_logs: Mapped[list["DailyLog"]] = relationship(back_populates="user")
    purchases: Mapped[list["Purchase"]] = relationship(back_populates="user")


from app.models.daily_log import DailyLog  # noqa: E402
from app.models.habit import Habit  # noqa: E402
from app.models.purchase import Purchase  # noqa: E402
from app.models.refresh_token import RefreshToken  # noqa: E402

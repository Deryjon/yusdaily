from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class HabitLog(Base):
    __tablename__ = "habit_logs"
    __table_args__ = (
        UniqueConstraint("daily_log_id", "habit_id", name="uq_habit_logs_daily_habit"),
        Index("ix_habit_logs_habit_daily", "habit_id", "daily_log_id"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    daily_log_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("daily_logs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    habit_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("habits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    comment: Mapped[str | None] = mapped_column(Text)

    daily_log: Mapped["DailyLog"] = relationship(back_populates="habit_logs")
    habit: Mapped["Habit"] = relationship(back_populates="habit_logs")


from app.models.daily_log import DailyLog  # noqa: E402
from app.models.habit import Habit  # noqa: E402

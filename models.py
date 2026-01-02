from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.app.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    has_deadline = Column(Boolean, default=False)
    deadline = Column(DateTime, nullable=True)
    status = Column(String, default="new")  # 'new', 'done', etc.
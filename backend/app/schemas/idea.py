from datetime import datetime
from pydantic import BaseModel, Field


class IdeaCreate(BaseModel):
    tg_id: int = Field(..., ge=1)
    text: str = Field(..., min_length=1, max_length=1000)
    source: str = Field(..., pattern="^(telegram|web)$")


class IdeaCreatePayload(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    source: str = Field(..., pattern="^(telegram|web)$")


class IdeaRead(BaseModel):
    id: int
    text: str
    source: str
    created_at: datetime

    class Config:
        from_attributes = True

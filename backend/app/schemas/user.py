from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    tg_id: int = Field(..., ge=1)
    username: str | None = Field(default=None, max_length=64)
    phone: str = Field(..., min_length=5, max_length=32)
    first_name: str = Field(..., min_length=1, max_length=64)
    last_name: str = Field(..., min_length=1, max_length=64)
    birth_year: int = Field(..., ge=1900, le=2100)
    gender: str = Field(..., pattern="^(male|female)$")


class UserRead(BaseModel):
    tg_id: int
    username: str | None
    phone: str
    first_name: str
    last_name: str
    birth_year: int
    gender: str

    class Config:
        from_attributes = True

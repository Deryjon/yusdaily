from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    timezone: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    timezone: str = Field(default="Asia/Tashkent", max_length=64)

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        return value.strip() or "Asia/Tashkent"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=16, max_length=4096)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=16, max_length=4096)


class AuthTokensResponse(BaseModel):
    user: UserPublic
    access_token: str
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str

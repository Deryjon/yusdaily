from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    compare_token_hash,
    create_access_token,
    create_refresh_token,
    get_token_subject,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models import Habit, RefreshToken, User
from app.schemas.auth import AuthTokensResponse, LoginRequest, RegisterRequest, UserPublic


DEFAULT_HABITS = (
    {"key": "ielts", "title": "IELTS", "type": "both", "target_minutes_per_day": 180, "sort_order": 0},
    {"key": "cert", "title": "Certificate", "type": "both", "target_minutes_per_day": 90, "sort_order": 1},
    {"key": "sport", "title": "Sport", "type": "checkbox", "target_minutes_per_day": None, "sort_order": 2},
)


def _validate_timezone(timezone_name: str) -> str:
    try:
        ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise HTTPException(status_code=400, detail="Invalid timezone") from exc
    return timezone_name


def _to_auth_response(user: User, access_token: str, refresh_token: str) -> AuthTokensResponse:
    return AuthTokensResponse(
        user=UserPublic(id=str(user.id), email=user.email, timezone=user.timezone),
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def register_user(session: AsyncSession, payload: RegisterRequest) -> AuthTokensResponse:
    timezone_name = _validate_timezone(payload.timezone)
    result = await session.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email is already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        timezone=timezone_name,
        is_active=True,
    )
    session.add(user)
    await session.flush()

    for habit_data in DEFAULT_HABITS:
        session.add(Habit(user_id=user.id, **habit_data))

    access_token = create_access_token(user.id)
    refresh_token, refresh_expires = create_refresh_token(user.id)
    session.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=refresh_expires,
        )
    )
    await session.commit()
    return _to_auth_response(user, access_token, refresh_token)


async def login_user(session: AsyncSession, payload: LoginRequest) -> AuthTokensResponse:
    result = await session.execute(select(User).where(User.email == payload.email, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(user.id)
    refresh_token, refresh_expires = create_refresh_token(user.id)
    session.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=refresh_expires,
        )
    )
    await session.commit()
    return _to_auth_response(user, access_token, refresh_token)


async def refresh_access_token(session: AsyncSession, refresh_token: str) -> str:
    try:
        user_id = get_token_subject(refresh_token, "refresh")
    except (ValueError, jwt.PyJWTError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
    )
    token_row = None
    for row in result.scalars().all():
        if compare_token_hash(refresh_token, row.token_hash):
            token_row = row
            break
    if not token_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if token_row.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    result = await session.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return create_access_token(user.id)


async def revoke_refresh_token(session: AsyncSession, refresh_token: str) -> None:
    try:
        user_id = get_token_subject(refresh_token, "refresh")
    except (ValueError, jwt.PyJWTError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
    )
    token_row = None
    for row in result.scalars().all():
        if compare_token_hash(refresh_token, row.token_hash):
            token_row = row
            break
    if not token_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_row.revoked_at = datetime.now(timezone.utc)
    await session.commit()

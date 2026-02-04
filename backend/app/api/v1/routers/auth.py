from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.auth import (
    AccessTokenResponse,
    AuthTokensResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
)
from app.services.auth import login_user, refresh_access_token, register_user, revoke_refresh_token

router = APIRouter()


@router.post("/register", response_model=AuthTokensResponse)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)) -> AuthTokensResponse:
    return await register_user(session, payload)


@router.post("/login", response_model=AuthTokensResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> AuthTokensResponse:
    return await login_user(session, payload)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(payload: RefreshRequest, session: AsyncSession = Depends(get_session)) -> AccessTokenResponse:
    access_token = await refresh_access_token(session, payload.refresh_token)
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest, session: AsyncSession = Depends(get_session)) -> Response:
    await revoke_refresh_token(session, payload.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

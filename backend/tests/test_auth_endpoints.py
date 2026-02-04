import os
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

class _DummySession:
    pass


async def _override_session():
    yield _DummySession()


class AuthEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
        os.environ.setdefault("JWT_SECRET", "test-secret")
        from app.core.config import get_settings
        from app.db.session import get_session
        from app.main import create_app

        get_settings.cache_clear()
        app = create_app()
        app.dependency_overrides[get_session] = _override_session
        cls.client = TestClient(app)

    @patch("app.api.v1.routers.auth.register_user", new_callable=AsyncMock)
    def test_register_happy_path(self, register_mock: AsyncMock) -> None:
        register_mock.return_value = {
            "user": {"id": "u1", "email": "u@test.com", "timezone": "Asia/Tashkent"},
            "access_token": "a",
            "refresh_token": "r",
        }
        response = self.client.post(
            "/api/v1/auth/register",
            json={"email": "u@test.com", "password": "password123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["email"], "u@test.com")

    @patch("app.api.v1.routers.auth.login_user", new_callable=AsyncMock)
    def test_login_invalid_credentials(self, login_mock: AsyncMock) -> None:
        login_mock.side_effect = HTTPException(status_code=401, detail="Invalid credentials")
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "u@test.com", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, 401)

    @patch("app.api.v1.routers.auth.refresh_access_token", new_callable=AsyncMock)
    def test_refresh_happy_path(self, refresh_mock: AsyncMock) -> None:
        refresh_mock.return_value = "new-access"
        response = self.client.post("/api/v1/auth/refresh", json={"refresh_token": "tokentokentokent1"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["access_token"], "new-access")

    @patch("app.api.v1.routers.auth.revoke_refresh_token", new_callable=AsyncMock)
    def test_logout_happy_path(self, revoke_mock: AsyncMock) -> None:
        revoke_mock.return_value = None
        response = self.client.post("/api/v1/auth/logout", json={"refresh_token": "tokentokentokent1"})
        self.assertEqual(response.status_code, 204)

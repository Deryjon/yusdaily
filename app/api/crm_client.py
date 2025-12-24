from typing import Any
import httpx


class CRMClient:
    def __init__(self, base_url: str, token: str | None = None) -> None:
        self._base_url = base_url
        self._token = token
        self._client = httpx.AsyncClient(timeout=10.0)

    def _headers(self) -> dict[str, str]:
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}

    async def close(self) -> None:
        await self._client.aclose()

    async def auth_user(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
    ) -> dict[str, Any]:
        payload = {
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
        }
        r = await self._client.post(
            f"{self._base_url}/api/tg/auth",
            json=payload,
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    async def get_today_plan(self, telegram_id: int) -> dict[str, Any]:
        r = await self._client.get(
            f"{self._base_url}/api/tg/plan/today",
            params={"telegram_id": telegram_id},
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    async def get_week_plan(self, telegram_id: int) -> dict[str, Any]:
        r = await self._client.get(
            f"{self._base_url}/api/tg/plan/week",
            params={"telegram_id": telegram_id},
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    async def mark_done(self, telegram_id: int) -> dict[str, Any]:
        r = await self._client.post(
            f"{self._base_url}/api/tg/done",
            json={"telegram_id": telegram_id},
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    async def get_settings(self, telegram_id: int) -> dict[str, Any]:
        r = await self._client.get(
            f"{self._base_url}/api/tg/settings",
            params={"telegram_id": telegram_id},
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    async def update_settings(self, telegram_id: int, settings: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post(
            f"{self._base_url}/api/tg/settings",
            json={"telegram_id": telegram_id, **settings},
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    async def get_reminder_batch(self, reminder_type: str) -> dict[str, Any]:
        r = await self._client.get(
            f"{self._base_url}/api/tg/reminders/{reminder_type}",
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

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

    async def get_profile(self, telegram_id: int) -> dict[str, Any] | None:
        r = await self._client.get(
            f"{self._base_url}/api/tg/profile",
            params={"tg_id": telegram_id},
            headers=self._headers(),
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    async def create_profile(self, payload: dict[str, Any]) -> dict[str, Any]:
        if "telegram_id" in payload:
            payload = {**payload, "tg_id": payload["telegram_id"]}
            payload.pop("telegram_id", None)
        r = await self._client.post(
            f"{self._base_url}/api/tg/profile",
            json=payload,
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    async def get_today(self, telegram_id: int) -> dict[str, Any]:
        r = await self._client.get(
            f"{self._base_url}/today",
            params={"tg_id": telegram_id},
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    async def get_progress(self, telegram_id: int, period: str) -> dict[str, Any]:
        r = await self._client.get(
            f"{self._base_url}/progress",
            params={"tg_id": telegram_id, "period": period},
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    async def create_idea(self, telegram_id: int, text: str, source: str) -> dict[str, Any]:
        r = await self._client.post(
            f"{self._base_url}/ideas",
            json={"tg_id": telegram_id, "text": text, "source": source},
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

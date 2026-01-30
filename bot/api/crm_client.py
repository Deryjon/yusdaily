from typing import Any
import httpx


class CRMClient:
    def __init__(self, base_url: str, token: str | None = None) -> None:
        self._base_url = base_url
        self._token = token
        self._client = httpx.AsyncClient(timeout=10.0)

    def _headers(self, token: str | None = None) -> dict[str, str]:
        actual = token or self._token
        if actual:
            return {"Authorization": f"Bearer {actual}"}
        return {}

    async def close(self) -> None:
        await self._client.aclose()

    async def login(self, phone: str) -> str | None:
        r = await self._client.post(
            f"{self._base_url}/api/auth/login",
            json={"phone": phone},
            headers=self._headers(),
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json().get("access_token")

    async def login_telegram(self, phone: str, init_data: str) -> str | None:
        r = await self._client.post(
            f"{self._base_url}/api/auth/telegram",
            json={"phone": phone, "initData": init_data},
            headers=self._headers(),
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json().get("access_token")

    async def get_profile(self, token: str) -> dict[str, Any]:
        r = await self._client.get(
            f"{self._base_url}/api/profile",
            headers=self._headers(token),
        )
        r.raise_for_status()
        return r.json()

    async def create_profile(self, payload: dict[str, Any]) -> dict[str, Any]:
        r = await self._client.post(
            f"{self._base_url}/api/tg/profile",
            json=payload,
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    async def get_today(self, token: str) -> dict[str, Any]:
        r = await self._client.get(
            f"{self._base_url}/api/today",
            headers=self._headers(token),
        )
        r.raise_for_status()
        return r.json()

    async def get_progress(self, token: str, period: str) -> dict[str, Any]:
        r = await self._client.get(
            f"{self._base_url}/api/progress",
            params={"period": period},
            headers=self._headers(token),
        )
        r.raise_for_status()
        return r.json()

    async def create_idea(self, token: str, text: str, source: str) -> dict[str, Any]:
        r = await self._client.post(
            f"{self._base_url}/api/ideas",
            json={"text": text, "source": source},
            headers=self._headers(token),
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

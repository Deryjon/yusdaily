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

    def _phone_headers(self, phone: str) -> dict[str, str]:
        headers = self._headers()
        headers["X-PHONE"] = phone
        return headers

    async def close(self) -> None:
        await self._client.aclose()

    async def get_profile(self, phone: str) -> dict[str, Any] | None:
        r = await self._client.get(
            f"{self._base_url}/api/tg/profile",
            params={"phone": phone},
            headers=self._headers(),
        )
        if r.status_code == 404:
            return None
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

    async def get_today(self, phone: str) -> dict[str, Any]:
        r = await self._client.get(
            f"{self._base_url}/api/today",
            headers=self._phone_headers(phone),
        )
        r.raise_for_status()
        return r.json()

    async def get_progress(self, phone: str, period: str) -> dict[str, Any]:
        r = await self._client.get(
            f"{self._base_url}/api/progress",
            params={"period": period},
            headers=self._phone_headers(phone),
        )
        r.raise_for_status()
        return r.json()

    async def create_idea(self, phone: str, text: str, source: str) -> dict[str, Any]:
        r = await self._client.post(
            f"{self._base_url}/api/ideas",
            json={"text": text, "source": source},
            headers=self._phone_headers(phone),
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

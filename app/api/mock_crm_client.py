from typing import Any


class MockCRMClient:
    async def close(self) -> None:
        return None

    async def auth_user(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
    ) -> dict[str, Any]:
        return {"ok": True}

    async def get_today_plan(self, telegram_id: int) -> dict[str, Any]:
        return {"text": "Mock: plan for today"}

    async def get_week_plan(self, telegram_id: int) -> dict[str, Any]:
        return {"text": "Mock: plan for the week"}

    async def mark_done(self, telegram_id: int) -> dict[str, Any]:
        return {"text": "Mock: step marked"}

    async def get_settings(self, telegram_id: int) -> dict[str, Any]:
        return {"text": "Mock: settings are not available"}

    async def update_settings(self, telegram_id: int, settings: dict[str, Any]) -> dict[str, Any]:
        return {"ok": True}

    async def get_reminder_batch(self, reminder_type: str) -> dict[str, Any]:
        return {"items": []}

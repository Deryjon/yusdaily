from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from bot.api.crm_client import CRMClient
from bot.locales import t


class ReminderService:
    def __init__(self, bot: Bot, crm: CRMClient, daily_cron: str, evening_cron: str) -> None:
        self._bot = bot
        self._crm = crm
        self._scheduler = AsyncIOScheduler()
        self._daily_cron = daily_cron
        self._evening_cron = evening_cron

    def start(self) -> None:
        self._scheduler.add_job(self._send_daily, CronTrigger.from_crontab(self._daily_cron))
        self._scheduler.add_job(self._send_evening, CronTrigger.from_crontab(self._evening_cron))
        self._scheduler.start()

    async def _send_daily(self) -> None:
        await self._send_batch("daily", fallback_text=t("daily_reminder", None))

    async def _send_evening(self) -> None:
        await self._send_batch("evening", fallback_text=t("evening_reminder", None))

    async def _send_batch(self, reminder_type: str, fallback_text: str) -> None:
        data = await self._crm.get_reminder_batch(reminder_type)
        items = data.get("items", [])
        for item in items:
            telegram_id = item.get("telegram_id")
            text = item.get("message") or fallback_text
            if telegram_id:
                await self._bot.send_message(telegram_id, text)

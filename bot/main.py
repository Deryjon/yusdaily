import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from bot.api.crm_client import CRMClient
from bot.config import get_settings
from bot.handlers import start, plan, menu
from bot.services.reminders import ReminderService


async def setup_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Start"),
        BotCommand(command="today", description="Plan for today"),
        BotCommand(command="app", description="Open CRM"),
    ]
    await bot.set_my_commands(commands, language_code="en")

    commands_ru = [
        BotCommand(command="start", description="Старт"),
        BotCommand(command="today", description="План на сегодня"),
    ]
    await bot.set_my_commands(commands_ru, language_code="ru")


async def main() -> None:
    cfg = get_settings()
    bot = Bot(token=cfg.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    crm = CRMClient(cfg.crm_base_url, cfg.crm_token)

    dp.include_router(start.router)
    dp.include_router(plan.router)
    dp.include_router(menu.router)

    await setup_commands(bot)

    reminder_service = ReminderService(bot, crm, cfg.daily_cron, cfg.evening_cron)
    reminder_service.start()

    try:
        await dp.start_polling(bot, crm=crm, webapp_url=cfg.webapp_url)
    finally:
        await crm.close()


if __name__ == "__main__":
    asyncio.run(main())

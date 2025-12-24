import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from app.api.crm_client import CRMClient
from app.api.mock_crm_client import MockCRMClient
from app.config import get_settings
from app.handlers import start, plan, done, settings, menu
from app.services.reminders import ReminderService


async def setup_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Start"),
        BotCommand(command="today", description="Plan for today"),
        BotCommand(command="week", description="Weekly plan"),
        BotCommand(command="done", description="Mark step done"),
        BotCommand(command="settings", description="Reminder settings"),
    ]
    await bot.set_my_commands(commands, language_code="en")

    commands_ru = [
        BotCommand(command="start", description="?????"),
        BotCommand(command="today", description="???? ?? ???????"),
        BotCommand(command="week", description="???? ??????"),
        BotCommand(command="done", description="???????? ???"),
        BotCommand(command="settings", description="?????????"),
    ]
    await bot.set_my_commands(commands_ru, language_code="ru")


async def main() -> None:
    cfg = get_settings()
    bot = Bot(token=cfg.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    crm = MockCRMClient() if cfg.mock_crm else CRMClient(cfg.crm_base_url, cfg.crm_token)

    dp.include_router(start.router)
    dp.include_router(plan.router)
    dp.include_router(done.router)
    dp.include_router(settings.router)
    dp.include_router(menu.router)

    await setup_commands(bot)

    reminder_service = ReminderService(bot, crm, cfg.daily_cron, cfg.evening_cron)
    reminder_service.start()

    try:
        await dp.start_polling(bot, crm=crm)
    finally:
        await crm.close()


if __name__ == "__main__":
    asyncio.run(main())

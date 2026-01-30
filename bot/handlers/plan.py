from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.api.crm_client import CRMClient
from bot.locales import t
from bot.handlers.menu import ensure_token, format_today_text

router = Router()


@router.message(Command("today"))
async def today_cmd(message: types.Message, crm: CRMClient, state: FSMContext) -> None:
    token = await ensure_token(state, crm, message, message.from_user.language_code)
    if not token:
        return
    data = await crm.get_today(token)
    text = format_today_text(data, message.from_user.language_code)
    await message.answer(text or t("today_empty", message.from_user.language_code))

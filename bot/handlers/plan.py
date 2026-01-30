from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.api.crm_client import CRMClient
from bot.locales import t
from bot.handlers.menu import ensure_phone, format_today_text

router = Router()


@router.message(Command("today"))
async def today_cmd(message: types.Message, crm: CRMClient, state: FSMContext) -> None:
    phone = await ensure_phone(state, message, message.from_user.language_code)
    if not phone:
        return
    data = await crm.get_today(phone)
    text = format_today_text(data, message.from_user.language_code)
    await message.answer(text or t("today_empty", message.from_user.language_code))

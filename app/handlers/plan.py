from aiogram import Router, types
from aiogram.filters import Command
from app.api.crm_client import CRMClient
from app.locales import t

router = Router()


@router.message(Command("today"))
async def today_cmd(message: types.Message, crm: CRMClient) -> None:
    data = await crm.get_today(message.from_user.id)
    text = data.get("text") or t("today_empty", message.from_user.language_code)
    await message.answer(text)

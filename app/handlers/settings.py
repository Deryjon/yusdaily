from aiogram import Router, types
from aiogram.filters import Command
from app.api.crm_client import CRMClient
from app.locales import t

router = Router()


@router.message(Command("settings"))
async def settings_cmd(message: types.Message, crm: CRMClient) -> None:
    data = await crm.get_settings(message.from_user.id)
    text = data.get("text") or t("settings_empty", message.from_user.language_code)
    await message.answer(text)

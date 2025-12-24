from aiogram import Router, types
from aiogram.filters import Command
from app.api.crm_client import CRMClient
from app.locales import t

router = Router()


@router.message(Command("done"))
async def done_cmd(message: types.Message, crm: CRMClient) -> None:
    data = await crm.mark_done(message.from_user.id)
    text = data.get("text") or t("done_ok", message.from_user.language_code)
    await message.answer(text)

from aiogram import Router, types
from aiogram.filters import Command
from app.api.crm_client import CRMClient
from app.keyboards import main_menu_kb
from app.locales import t

router = Router()


@router.message(Command("start"))
async def start_cmd(message: types.Message, crm: CRMClient) -> None:
    user = message.from_user
    await crm.auth_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    await message.answer(
        t("start_greeting", user.language_code),
        reply_markup=main_menu_kb(user.language_code),
    )

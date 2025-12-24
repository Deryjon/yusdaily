from aiogram import Router, types
from app.api.crm_client import CRMClient
from app.keyboards import main_menu_kb
from app.locales import t

router = Router()


@router.message()
async def menu_text_router(message: types.Message, crm: CRMClient) -> None:
    if not message.text:
        return

    lang = message.from_user.language_code
    text = message.text.strip()

    if text == t("menu_today", lang):
        data = await crm.get_today_plan(message.from_user.id)
        await message.answer(data.get("text") or t("today_empty", lang))
        return

    if text == t("menu_week", lang):
        data = await crm.get_week_plan(message.from_user.id)
        await message.answer(data.get("text") or t("week_empty", lang))
        return

    if text == t("menu_done", lang):
        data = await crm.mark_done(message.from_user.id)
        await message.answer(data.get("text") or t("done_ok", lang))
        return

    if text == t("menu_settings", lang):
        data = await crm.get_settings(message.from_user.id)
        await message.answer(data.get("text") or t("settings_empty", lang))
        return

    if text.lower() in {"/start", "/today", "/week", "/done", "/settings"}:
        return

    await message.answer(
        t("menu_title", lang),
        reply_markup=main_menu_kb(lang),
    )

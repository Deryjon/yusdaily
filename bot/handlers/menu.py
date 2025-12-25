from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from bot.api.crm_client import CRMClient
from bot.keyboards import main_menu_kb, progress_period_kb
from bot.locales import t

router = Router()


class IdeaState(StatesGroup):
    waiting_text = State()


@router.message(StateFilter(None))
async def menu_text_router(message: types.Message, crm: CRMClient, state: FSMContext) -> None:
    if not message.text:
        return

    lang = message.from_user.language_code
    text = message.text.strip()

    if text == t("menu_today", lang):
        data = await crm.get_today(message.from_user.id)
        await message.answer(data.get("text") or t("today_empty", lang))
        return

    if text == t("menu_progress", lang):
        await message.answer(
            t("progress_choose", lang),
            reply_markup=progress_period_kb(lang),
        )
        return

    if text == t("menu_ideas", lang):
        await state.set_state(IdeaState.waiting_text)
        await message.answer(
            t("idea_prompt", lang),
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    if text.lower() in {"/start", "/today"}:
        return

    await message.answer(
        t("menu_title", lang),
        reply_markup=main_menu_kb(lang),
    )


@router.message(IdeaState.waiting_text)
async def idea_text(message: types.Message, crm: CRMClient, state: FSMContext) -> None:
    lang = message.from_user.language_code
    if not message.text or not message.text.strip():
        await message.answer(t("idea_prompt", lang))
        return

    await crm.create_idea(message.from_user.id, message.text.strip(), "telegram")
    await state.clear()
    await message.answer(
        t("idea_saved", lang),
        reply_markup=main_menu_kb(lang),
    )


@router.callback_query(StateFilter(None))
async def progress_callback(query: types.CallbackQuery, crm: CRMClient) -> None:
    if not query.data or not query.data.startswith("progress:"):
        return

    period = query.data.split(":", 1)[1]
    data = await crm.get_progress(query.from_user.id, period)
    if query.message:
        await query.message.answer(data.get("text") or "")
    await query.answer()

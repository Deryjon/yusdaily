from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from bot.api.crm_client import CRMClient
from bot.handlers.start import RegistrationState
from bot.keyboards import main_menu_kb, phone_request_kb, profile_actions_kb, progress_period_kb
from bot.locales import t

router = Router()


class IdeaState(StatesGroup):
    waiting_text = State()


def format_profile_text(profile: dict, language_code: str | None) -> str:
    def value_or_empty(value: object | None) -> str:
        if value is None or value == "":
            return t("profile_empty", language_code)
        return str(value)

    gender_value = profile.get("gender")
    if gender_value == "male":
        gender_label = t("gender_male", language_code)
    elif gender_value == "female":
        gender_label = t("gender_female", language_code)
    else:
        gender_label = t("profile_empty", language_code)

    name_value = " ".join(
        part for part in [profile.get("first_name", ""), profile.get("last_name", "")] if part
    ).strip()
    if not name_value:
        name_value = t("profile_empty", language_code)

    lines = [
        t("profile_title", language_code),
        f'{t("profile_username", language_code)}: {value_or_empty(profile.get("username"))}',
        f'{t("profile_phone", language_code)}: {value_or_empty(profile.get("phone"))}',
        f'{t("profile_name", language_code)}: {name_value}',
        f'{t("profile_birth_year", language_code)}: {value_or_empty(profile.get("birth_year"))}',
        f'{t("profile_gender", language_code)}: {gender_label}',
    ]
    return "\n".join(lines)


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

    if text == t("menu_profile", lang):
        profile = await crm.get_profile(message.from_user.id)
        if not profile:
            await message.answer(
                t("profile_not_found", lang),
                reply_markup=main_menu_kb(lang),
            )
            return

        await message.answer(
            format_profile_text(profile, lang),
            reply_markup=profile_actions_kb(lang),
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


@router.callback_query(StateFilter(None))
async def profile_callback(
    query: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not query.data or not query.data.startswith("profile:"):
        return

    action = query.data.split(":", 1)[1]
    lang = query.from_user.language_code

    if action == "edit":
        await state.set_state(RegistrationState.phone)
        if query.message:
            await query.message.answer(
                t("ask_phone", lang),
                reply_markup=phone_request_kb(lang),
            )
        await query.answer()
        return

    if action == "back":
        if query.message:
            await query.message.answer(
                t("menu_title", lang),
                reply_markup=main_menu_kb(lang),
            )
        await query.answer()

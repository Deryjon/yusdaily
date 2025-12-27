from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from bot.api.crm_client import CRMClient
from bot.keyboards import gender_kb, main_menu_kb, phone_request_kb, webapp_fallback_kb, webapp_kb
from bot.locales import t
from datetime import datetime
import logging

router = Router()
logger = logging.getLogger(__name__)


class RegistrationState(StatesGroup):
    phone = State()
    first_name = State()
    last_name = State()
    birth_year = State()
    gender = State()


async def send_webapp_prompt(message: types.Message, webapp_url: str) -> None:
    user = message.from_user
    logger.info(
        "webapp_prompt user_id=%s username=%s ts=%s",
        user.id if user else None,
        user.username if user else None,
        datetime.utcnow().isoformat(),
    )
    await message.answer(
        "\u041e\u0442\u043a\u0440\u044b\u0442\u044c CRM",
        reply_markup=webapp_kb(webapp_url),
    )
    await message.answer(
        "\u0415\u0441\u043b\u0438 WebApp \u043d\u0435 \u043e\u0442\u043a\u0440\u044b\u0432\u0430\u0435\u0442\u0441\u044f, "
        "\u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435 \u0441\u0441\u044b\u043b\u043a\u0443:",
        reply_markup=webapp_fallback_kb(webapp_url),
    )


@router.message(Command("app"))
async def app_cmd(message: types.Message, webapp_url: str) -> None:
    await send_webapp_prompt(message, webapp_url)


@router.message(Command("start"))
async def start_cmd(
    message: types.Message,
    crm: CRMClient,
    state: FSMContext,
    webapp_url: str,
) -> None:
    await send_webapp_prompt(message, webapp_url)
    user = message.from_user
    lang = user.language_code
    profile = await crm.get_profile(user.id)
    if profile:
        await state.clear()
        await message.answer(
            t("profile_already_saved", lang),
            reply_markup=main_menu_kb(lang),
        )
        return

    await state.set_state(RegistrationState.phone)
    await message.answer(
        t("ask_phone", lang),
        reply_markup=phone_request_kb(lang),
    )


@router.message(RegistrationState.phone)
async def register_phone(message: types.Message, state: FSMContext) -> None:
    lang = message.from_user.language_code
    if not message.contact or message.contact.user_id != message.from_user.id:
        await message.answer(
            t("invalid_phone", lang),
            reply_markup=phone_request_kb(lang),
        )
        return

    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(RegistrationState.first_name)
    await message.answer(t("ask_first_name", lang), reply_markup=ReplyKeyboardRemove())


@router.message(RegistrationState.first_name)
async def register_first_name(message: types.Message, state: FSMContext) -> None:
    lang = message.from_user.language_code
    if not message.text or not message.text.strip():
        await message.answer(t("ask_first_name", lang))
        return

    await state.update_data(first_name=message.text.strip())
    await state.set_state(RegistrationState.last_name)
    await message.answer(t("ask_last_name", lang))


@router.message(RegistrationState.last_name)
async def register_last_name(message: types.Message, state: FSMContext) -> None:
    lang = message.from_user.language_code
    if not message.text or not message.text.strip():
        await message.answer(t("ask_last_name", lang))
        return

    await state.update_data(last_name=message.text.strip())
    await state.set_state(RegistrationState.birth_year)
    await message.answer(t("ask_birth_year", lang))


@router.message(RegistrationState.birth_year)
async def register_birth_year(message: types.Message, state: FSMContext) -> None:
    lang = message.from_user.language_code
    if not message.text or not message.text.strip().isdigit():
        await message.answer(t("invalid_birth_year", lang))
        return

    birth_year = int(message.text.strip())
    if birth_year < 1900 or birth_year > 2100:
        await message.answer(t("invalid_birth_year", lang))
        return

    await state.update_data(birth_year=birth_year)
    await state.set_state(RegistrationState.gender)
    await message.answer(t("ask_gender", lang), reply_markup=gender_kb(lang))


@router.message(RegistrationState.gender)
async def register_gender(message: types.Message, crm: CRMClient, state: FSMContext) -> None:
    lang = message.from_user.language_code
    if not message.text:
        await message.answer(t("ask_gender", lang), reply_markup=gender_kb(lang))
        return

    text = message.text.strip()
    if text == t("gender_male", lang):
        gender = "male"
    elif text == t("gender_female", lang):
        gender = "female"
    else:
        await message.answer(t("ask_gender", lang), reply_markup=gender_kb(lang))
        return

    data = await state.get_data()
    user = message.from_user
    payload = {
        "tg_id": user.id,
        "username": user.username,
        "phone": data["phone"],
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "birth_year": data["birth_year"],
        "gender": gender,
    }
    await crm.create_profile(payload)
    await state.clear()
    await message.answer(
        t("profile_saved", lang),
        reply_markup=main_menu_kb(lang),
    )

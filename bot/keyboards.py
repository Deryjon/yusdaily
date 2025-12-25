from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.locales import t


def main_menu_kb(language_code: str | None) -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text=t("menu_today", language_code)),
            ],
            [
                types.KeyboardButton(text=t("menu_progress", language_code)),
            ],
            [
                types.KeyboardButton(text=t("menu_profile", language_code)),
            ],
            [
                types.KeyboardButton(text=t("menu_ideas", language_code)),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder=t("menu_title", language_code),
    )


def phone_request_kb(language_code: str | None) -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(
                    text=t("share_phone", language_code),
                    request_contact=True,
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder=t("share_phone", language_code),
    )


def gender_kb(language_code: str | None) -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text=t("gender_male", language_code)),
                types.KeyboardButton(text=t("gender_female", language_code)),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder=t("ask_gender", language_code),
    )


def progress_period_kb(language_code: str | None) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("period_week", language_code), callback_data="progress:week")
    builder.button(text=t("period_month", language_code), callback_data="progress:month")
    builder.adjust(2)
    return builder.as_markup()


def profile_actions_kb(language_code: str | None) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("profile_edit", language_code), callback_data="profile:edit")
    builder.button(text=t("profile_back", language_code), callback_data="profile:back")
    builder.adjust(2)
    return builder.as_markup()

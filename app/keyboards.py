from aiogram import types
from app.locales import t


def main_menu_kb(language_code: str | None) -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text=t("menu_today", language_code)),
                types.KeyboardButton(text=t("menu_week", language_code)),
            ],
            [
                types.KeyboardButton(text=t("menu_done", language_code)),
                types.KeyboardButton(text=t("menu_settings", language_code)),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder=t("menu_title", language_code),
    )

from typing import Final


LOCALES: Final = {
    "ru": {
        "start_greeting": (
            "Привет! Я бот твоих шагов.\n\n"
            "Команды:\n"
            "/today — план на сегодня\n"
            "/week — план недели\n"
            "/done — отметить шаг\n"
            "/settings — настройки напоминаний"
        ),
        "menu_title": "Главное меню",
        "menu_today": "План на сегодня",
        "menu_week": "План недели",
        "menu_done": "Сделал шаг",
        "menu_settings": "Настройки",
        "today_empty": "Нет плана на сегодня",
        "week_empty": "Нет плана на неделю",
        "done_ok": "Отлично! Шаг отмечен.",
        "settings_empty": "Настройки недоступны",
        "daily_reminder": "Сделай один шаг",
        "evening_reminder": "Подведи итог дня",
    },
    "en": {
        "start_greeting": (
            "Hi! I'm your step bot.\n\n"
            "Commands:\n"
            "/today — today's plan\n"
            "/week — weekly plan\n"
            "/done — mark step done\n"
            "/settings — reminder settings"
        ),
        "menu_title": "Main menu",
        "menu_today": "Today's plan",
        "menu_week": "Weekly plan",
        "menu_done": "Step done",
        "menu_settings": "Settings",
        "today_empty": "No plan for today",
        "week_empty": "No plan for this week",
        "done_ok": "Nice! Step marked.",
        "settings_empty": "Settings are unavailable",
        "daily_reminder": "Make one step",
        "evening_reminder": "Summarize your day",
    },
}


def get_lang(language_code: str | None) -> str:
    if not language_code:
        return "ru"
    base = language_code.split("-", 1)[0].lower()
    return base if base in LOCALES else "ru"


def t(key: str, language_code: str | None) -> str:
    lang = get_lang(language_code)
    return LOCALES[lang].get(key, LOCALES["ru"].get(key, key))

from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    crm_base_url: str
    crm_token: str | None
    daily_cron: str
    evening_cron: str
    webapp_url: str


def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "")
    crm_base_url = os.getenv("CRM_BASE_URL", "")
    if not bot_token or not crm_base_url:
        raise RuntimeError("BOT_TOKEN and CRM_BASE_URL are required")

    return Settings(
        bot_token=bot_token,
        crm_base_url=crm_base_url.rstrip("/"),
        crm_token=os.getenv("CRM_TOKEN"),
        daily_cron=os.getenv("DAILY_CRON", "0 9 * * *"),
        evening_cron=os.getenv("EVENING_CRON", "0 20 * * *"),
        webapp_url=os.getenv("WEBAPP_URL", "https://yus-daily-crm.vercel.app/"),
    )

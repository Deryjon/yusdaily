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
    mock_crm: bool


def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "")
    crm_base_url = os.getenv("CRM_BASE_URL", "")
    mock_crm = os.getenv("MOCK_CRM", "0") in {"1", "true", "yes"}
    if not bot_token or (not crm_base_url and not mock_crm):
        raise RuntimeError("BOT_TOKEN and CRM_BASE_URL are required (unless MOCK_CRM=1)")

    return Settings(
        bot_token=bot_token,
        crm_base_url=crm_base_url.rstrip("/"),
        crm_token=os.getenv("CRM_TOKEN"),
        daily_cron=os.getenv("DAILY_CRON", "0 9 * * *"),
        evening_cron=os.getenv("EVENING_CRON", "0 20 * * *"),
        mock_crm=mock_crm,
    )

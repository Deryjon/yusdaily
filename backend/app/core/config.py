from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(alias="DATABASE_URL")
    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_access_expires_min: int = Field(default=15, alias="JWT_ACCESS_EXPIRES_MIN")
    jwt_refresh_expires_days: int = Field(default=30, alias="JWT_REFRESH_EXPIRES_DAYS")
    daily_done_minutes: int = Field(default=180, alias="DAILY_DONE_MINUTES")
    cors_origins: str = Field(default="", alias="CORS_ORIGINS")
    env: str = Field(default="dev", alias="ENV")
    api_token: str | None = Field(default=None, alias="API_TOKEN")
    auth_rate_limit_per_minute: int = 10

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

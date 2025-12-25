from dataclasses import dataclass
import os


@dataclass(frozen=True)
class BackendSettings:
    database_url: str
    api_token: str | None


def get_backend_settings() -> BackendSettings:
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required for backend API")

    return BackendSettings(
        database_url=database_url,
        api_token=os.getenv("API_TOKEN"),
    )

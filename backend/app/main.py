from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.rate_limit import AuthRateLimitMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Daily Tracker API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        AuthRateLimitMiddleware,
        max_requests=settings.auth_rate_limit_per_minute,
    )
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()

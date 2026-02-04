from fastapi import APIRouter

from app.api.v1.routers import auth, days, habits, stats

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(habits.router, prefix="/habits", tags=["habits"])
api_router.include_router(days.router, prefix="/days", tags=["days"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])

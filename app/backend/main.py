from fastapi import FastAPI

from app.backend.routes import router


app = FastAPI(title="TG Bot Backend")
app.include_router(router)

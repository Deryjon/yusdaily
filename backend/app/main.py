from fastapi import FastAPI

from backend.app.api.routes import router


app = FastAPI(title="TG Bot Backend")
app.include_router(router)

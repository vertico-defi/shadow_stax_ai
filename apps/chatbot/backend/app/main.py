from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import chat, health
from shared.config.settings import get_settings
from shared.logging.logger import get_logger

settings = get_settings()
logger = get_logger("chatbot-backend")

app = FastAPI(title="Shadow Stax AI Chatbot API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(chat.router, prefix="/chat", tags=["chat"])


@app.on_event("startup")
def startup_event() -> None:
    logger.info("backend_startup env=%s", settings.app_env)

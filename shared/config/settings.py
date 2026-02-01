from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_env: str
    backend_host: str
    backend_port: int
    frontend_port: int
    frontend_origin: str
    api_prefix: str
    llm_base_url: str
    llm_model: str
    llm_api_mode: str
    llm_max_tokens_default: int
    llm_concurrency_limit: int
    llm_request_timeout_seconds: int
    rate_limit_per_minute: int
    rate_limit_burst: int
    conversation_ttl_seconds: int
    safety_blocklist_enabled: bool


def get_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "local"),
        backend_host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        backend_port=int(os.getenv("BACKEND_PORT", "8000")),
        frontend_port=int(os.getenv("FRONTEND_PORT", "3000")),
        frontend_origin=os.getenv("FRONTEND_ORIGIN", "http://localhost:3000"),
        api_prefix=os.getenv("API_PREFIX", ""),
        llm_base_url=os.getenv("LLM_BASE_URL", "http://llm:8001/v1"),
        llm_model=os.getenv("LLM_MODEL", ""),
        llm_api_mode=os.getenv("LLM_API_MODE", "openai"),
        llm_max_tokens_default=int(os.getenv("LLM_MAX_TOKENS_DEFAULT", "512")),
        llm_concurrency_limit=int(os.getenv("LLM_CONCURRENCY_LIMIT", "8")),
        llm_request_timeout_seconds=int(os.getenv("LLM_REQUEST_TIMEOUT_SECONDS", "90")),
        rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "30")),
        rate_limit_burst=int(os.getenv("RATE_LIMIT_BURST", "10")),
        conversation_ttl_seconds=int(os.getenv("CONVERSATION_TTL_SECONDS", "0")),
        safety_blocklist_enabled=os.getenv("SAFETY_BLOCKLIST_ENABLED", "true").lower() == "true",
    )

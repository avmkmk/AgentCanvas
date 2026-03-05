"""
Application configuration — loaded from environment variables at startup.

Coding Standard 9: pydantic-settings validates all env vars.
The application raises a startup error if any required variable is missing
(fail-fast — no silent misconfiguration in production).
Coding Standard 10: no hardcoded secrets — all credentials come from .env.
"""
from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Extra env vars are ignored — not an error
        extra="ignore",
    )

    # ─── Database ──────────────────────────────────────────────────────────────
    database_url: str
    mongo_uri: str
    redis_url: str

    # ─── Security ──────────────────────────────────────────────────────────────
    api_key: str
    # Comma-separated list of allowed CORS origins
    allowed_origins: str = "http://localhost:3000"

    # ─── LLM ───────────────────────────────────────────────────────────────────
    anthropic_api_key: str
    max_llm_retries: int = 3
    llm_timeout_seconds: int = 60

    # ─── Runtime ───────────────────────────────────────────────────────────────
    log_level: str = "INFO"
    debug: bool = False

    @field_validator("log_level")
    @classmethod
    def log_level_must_be_valid(cls, value: str) -> str:
        """Reject unrecognised log levels — Python's logging module ignores them silently."""
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = value.upper()
        if upper not in valid:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(sorted(valid))}")
        return upper

    @field_validator("api_key")
    @classmethod
    def api_key_must_be_set(cls, value: str) -> str:
        """Reject placeholder values — catches copy-paste mistakes in .env."""
        if value in ("", "change-me", "your-api-key-here"):
            raise ValueError(
                "API_KEY is not set. Update your .env file before starting."
            )
        return value

    def get_allowed_origins_list(self) -> list[str]:
        """Split comma-separated ALLOWED_ORIGINS into a Python list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Module-level singleton — imported by all modules that need config.
# Pydantic raises ValidationError at import time if any required var is absent.
settings = Settings()

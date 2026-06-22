"""OmniFlow AI — Application Configuration."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────
    app_name: str = "OmniFlow AI"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"

    # ── Database ─────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./omniflow.db"

    # ── Redis ────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    redis_mode: Literal["redis", "memory"] = "memory"

    # ── Kafka ────────────────────────────────────
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_mode: Literal["kafka", "memory"] = "memory"

    # ── OpenAI / LLM ────────────────────────────
    openai_api_key: str = ""
    llm_mode: Literal["openai", "mock"] = "mock"
    openai_model: str = "gpt-4o-mini"

    # ── JWT Auth ─────────────────────────────────
    jwt_secret_key: str = "dev-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # ── External APIs ────────────────────────────
    weather_api_key: str = ""
    google_trends_api_key: str = ""

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.database_url


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()

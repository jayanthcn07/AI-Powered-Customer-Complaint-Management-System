"""
Application configuration, loaded from environment variables / .env file.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Database -----------------------------------------------------
    # Defaults to a local SQLite file so the app runs out-of-the-box for
    # demo purposes. Point DATABASE_URL at MySQL/Postgres for production,
    # e.g. postgresql+psycopg2://user:password@localhost:5432/complaints
    DATABASE_URL: str = "sqlite:///./complaints.db"

    # --- Groq / LLM -----------------------------------------------------
    GROQ_API_KEY: str = ""
    GROQ_PRIMARY_MODEL: str = "gemma2-9b-it"
    GROQ_CONTEXT_MODEL: str = "llama-3.3-70b-versatile"

    # --- App -----------------------------------------------------------
    APP_NAME: str = "Vigilon"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""Application configuration."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os


class Settings(BaseSettings):
    """Application settings."""

    # App
    APP_NAME: str = "Issue Tracker"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/issue_tracker.db"

    # File Storage
    ISSUES_DATA_DIR: str = "/app/data/issues"
    ATTACHMENTS_DIR: str = "/app/data/attachments"

    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS — stored as a raw comma-separated string so pydantic-settings reads
    # it directly from the environment variable without attempting JSON parsing.
    # Use get_cors_origins() to obtain the split list at runtime.
    # The default covers local dev; production origins should be supplied via
    # the CORS_ORIGINS environment variable.
    #
    # NOTE: "https://railway.com" and "https://railway.app" were intentionally
    # removed from the defaults — they are Railway's own marketing/dashboard
    # domains, not the deployed app origin, and were the root cause of the
    # wrong Access-Control-Allow-Origin header being echoed back to browsers.
    # Add your real production frontend URL via the FRONTEND_URL env var or by
    # extending CORS_ORIGINS in the deployment environment.
    CORS_ORIGINS: str = (
        "http://localhost:3000,"
        "http://localhost:5173,"
        "http://issue-tracker.zeabur.internal,"
        "https://issue-tracker.zeabur.internal"
    )

    # Frontend URL — when set, this origin is merged into CORS_ORIGINS so a
    # single env var is enough for simple deployments.
    FRONTEND_URL: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_cors_origins(self) -> List[str]:
        """Return the deduplicated list of allowed CORS origins.

        Splits the comma-separated CORS_ORIGINS string and merges in
        FRONTEND_URL so callers only need to consult one place.
        """
        origins = [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        return origins


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()


settings = get_settings()

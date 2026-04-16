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

    # CORS — accepts a comma-separated string via env var (pydantic-settings
    # will split on commas automatically when the field type is List[str]).
    # The default covers local dev; production origins should be supplied via
    # the CORS_ORIGINS environment variable.
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://railway.com",
        "https://railway.app",
    ]

    # Frontend URL — when set, this origin is merged into CORS_ORIGINS so a
    # single env var is enough for simple deployments.
    FRONTEND_URL: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_cors_origins(self) -> List[str]:
        """Return the deduplicated list of allowed CORS origins.

        Merges FRONTEND_URL into CORS_ORIGINS so callers only need to
        consult one place.
        """
        origins = list(self.CORS_ORIGINS)
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        return origins


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()


settings = get_settings()

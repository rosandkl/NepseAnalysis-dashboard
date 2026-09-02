"""
Central configuration for the NEPSE dashboard.

All settings are read from environment variables (loaded from a .env file
via python-dotenv). Nothing here is hardcoded so the same codebase can run
against different databases/users without code changes.

Per the project's own rule (handover manual, Section 25.G/H):
- Use a READ-ONLY database user for the dashboard connection.
- Never put real credentials in this file or in source control — only in .env.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get_env(key: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(key, default)
    if required and not value:
        raise RuntimeError(
            f"Missing required environment variable: {key}. "
            f"Copy .env.example to .env and fill it in."
        )
    return value


@dataclass(frozen=True)
class DBConfig:
    host: str
    port: int
    database: str
    user: str
    password: str
    schema: str  # default schema to search (stock_dashboard)
    pool_size: int
    max_overflow: int
    pool_recycle_seconds: int

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


def load_db_config() -> DBConfig:
    return DBConfig(
        host=_get_env("DB_HOST", "localhost"),
        port=int(_get_env("DB_PORT", "5432")),
        database=_get_env("DB_NAME", required=True),
        user=_get_env("DB_USER", required=True),
        password=_get_env("DB_PASSWORD", required=True),
        schema=_get_env("DB_SCHEMA", "stock_dashboard"),
        pool_size=int(_get_env("DB_POOL_SIZE", "5")),
        max_overflow=int(_get_env("DB_MAX_OVERFLOW", "10")),
        pool_recycle_seconds=int(_get_env("DB_POOL_RECYCLE_SECONDS", "1800")),
    )


# App-level settings (non-DB), also extensible via env vars as new pages are added.
APP_TITLE = _get_env("APP_TITLE", "NEPSE Analysis & Stock Dashboard")
DEFAULT_CACHE_TTL_SECONDS = int(_get_env("DEFAULT_CACHE_TTL_SECONDS", "300"))

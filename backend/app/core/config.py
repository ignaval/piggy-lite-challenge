"""Application settings, loaded from the environment (with sensible defaults).

Everything here is plain configuration — no secrets are required to run the
starter. Override any value via a `.env` file (see `.env.example`) or real
environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Project metadata
    PROJECT_NAME: str = "Piggy Lite"
    API_V1_PREFIX: str = "/api/v1"

    # Database — SQLite file by default; zero setup required. The Docker setup
    # overrides this with a Postgres URL (closer to the real Piggy stack).
    DATABASE_URL: str = "sqlite:///./piggy_lite.db"

    # Create tables on startup (convenient for the zero-setup SQLite path).
    # Docker sets this false and runs Alembic migrations on boot instead.
    CREATE_TABLES_ON_STARTUP: bool = True

    # Secret guarding the /e2e/* helper routes. Fine to keep the default
    # locally; override it anywhere it actually matters.
    E2E_SECRET: str = "dev-e2e-secret"

    # CORS — the Next.js frontend dev server.
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()

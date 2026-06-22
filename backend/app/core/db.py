"""Database engine and session plumbing.

`create_db_and_tables()` is called on app startup so the app runs with zero
migration steps (SQLite file is created on first boot). Alembic is *also*
configured for the realistic "add a model + migration" workflow — see
`backend/README.md`.
"""

from collections.abc import Generator
from pathlib import Path
from typing import Annotated

from alembic.command import stamp
from alembic.config import Config
from fastapi import Depends
from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

# `check_same_thread=False` is required for SQLite + FastAPI/TestClient, which
# may touch the connection from different threads.
connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# Alembic setup paths, resolved absolutely so stamping works regardless of the
# process's working directory. db.py lives at backend/app/core/.
_BACKEND_DIR = Path(__file__).resolve().parents[2]
_ALEMBIC_INI = _BACKEND_DIR / "alembic.ini"
_ALEMBIC_DIR = _BACKEND_DIR / "alembic"


def create_db_and_tables() -> None:
    """Create all tables that don't yet exist, then stamp Alembic to head.
    Idempotent.

    ``create_all`` builds the schema directly, so Alembic otherwise has no
    ``alembic_version`` row and ``alembic upgrade head`` would try to re-create
    existing tables. Stamping keeps the documented migration workflow working on
    the zero-setup SQLite path. See ``_stamp_alembic_head_if_unversioned``.
    """
    # Importing models registers them on SQLModel.metadata.
    import app.models  # noqa: F401

    SQLModel.metadata.create_all(engine)
    _stamp_alembic_head_if_unversioned()


def _stamp_alembic_head_if_unversioned() -> None:
    """Stamp the DB to Alembic head if it has no version row yet.

    No-op when the DB is already versioned (e.g. the Docker path, which runs
    real migrations). Never fatal — if stamping can't run, we warn and continue
    so the app/seed still starts.
    """
    if inspect(engine).has_table("alembic_version"):
        return
    try:
        cfg = Config(str(_ALEMBIC_INI))
        cfg.set_main_option("script_location", str(_ALEMBIC_DIR))
        stamp(cfg, "head")
    except Exception as exc:  # pragma: no cover - convenience only, never fatal
        print(
            f"⚠️  Could not stamp Alembic head ({exc}). If you plan to add "
            "migrations, run `alembic stamp head` once before autogenerate."
        )


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

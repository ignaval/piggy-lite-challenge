"""Database engine and session plumbing.

`create_db_and_tables()` is called on app startup so the app runs with zero
migration steps (SQLite file is created on first boot). Alembic is *also*
configured for the realistic "add a model + migration" workflow — see
`backend/README.md`.
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

# `check_same_thread=False` is required for SQLite + FastAPI/TestClient, which
# may touch the connection from different threads.
connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)


def create_db_and_tables() -> None:
    """Create all tables that don't yet exist. Idempotent."""
    # Importing models registers them on SQLModel.metadata.
    import app.models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

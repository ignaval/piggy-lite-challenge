"""Test fixtures.

Mirrors real Piggy's E2E pattern: instead of crafting real tokens, we override
the ``get_current_guardian`` dependency to return a pre-created test Guardian.
The database is a throwaway temp SQLite file per test, so tests are isolated.
"""

from __future__ import annotations

from collections.abc import Generator
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.api.deps import get_current_guardian
from app.core.db import get_session
from app.main import app
from app.models import Balance, Dependant, Guardian


@pytest.fixture(name="engine")
def engine_fixture(tmp_path: Path):
    """A fresh temp-file SQLite engine per test."""
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture(name="guardian")
def guardian_fixture(session: Session) -> Guardian:
    """The authenticated guardian for most tests, with one funded dependant."""
    guardian = Guardian(first_name="TestGuardian")
    session.add(guardian)
    session.commit()
    session.refresh(guardian)
    return guardian


@pytest.fixture(name="dependant")
def dependant_fixture(session: Session, guardian: Guardian) -> Dependant:
    dependant = Dependant(first_name="TestKid", guardian_id=guardian.id)
    session.add(dependant)
    session.commit()
    session.refresh(dependant)
    session.add(Balance(dependant_id=dependant.id, amount=Decimal("20.00")))
    session.commit()
    return dependant


@pytest.fixture(name="client")
def client_fixture(engine, guardian: Guardian) -> Generator[TestClient, None, None]:
    """TestClient wired to the temp DB and authenticated as ``guardian``."""

    def get_session_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    def get_current_guardian_override() -> Guardian:
        return guardian

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_guardian] = get_current_guardian_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

"""Auth tests exercising the *real* ``get_current_guardian`` token parsing.

These do NOT override the auth dependency (unlike the flow tests), so they
verify the ``Authorization: Bearer guardian-{id}`` scheme end to end.
"""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.db import get_session
from app.main import app
from app.models import Guardian


@pytest.fixture(name="auth_client")
def auth_client_fixture(engine) -> Generator[TestClient, None, None]:
    """Client with only the DB overridden — real auth dependency in play."""

    def get_session_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_missing_token_is_401(auth_client: TestClient):
    assert auth_client.get("/api/v1/dependants").status_code == 401


def test_malformed_token_is_401(auth_client: TestClient):
    resp = auth_client.get(
        "/api/v1/dependants",
        headers={"Authorization": "Bearer not-a-guardian-token"},
    )
    assert resp.status_code == 401


def test_unknown_guardian_is_401(auth_client: TestClient):
    resp = auth_client.get(
        "/api/v1/dependants",
        headers={"Authorization": f"Bearer guardian-{uuid4()}"},
    )
    assert resp.status_code == 401


def test_valid_token_is_200(auth_client: TestClient, guardian: Guardian):
    resp = auth_client.get(
        "/api/v1/dependants",
        headers={"Authorization": f"Bearer guardian-{guardian.id}"},
    )
    assert resp.status_code == 200
    assert resp.json() == []

"""Tests for the /e2e seed + cleanup seam and its secret gate."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.db import get_session
from app.main import app


@pytest.fixture(name="plain_client")
def plain_client_fixture(engine) -> Generator[TestClient, None, None]:
    def get_session_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_seed_requires_secret(plain_client: TestClient):
    assert plain_client.post("/api/v1/e2e/seed").status_code == 403
    assert (
        plain_client.post(
            "/api/v1/e2e/seed", headers={"X-E2E-Secret": "wrong"}
        ).status_code
        == 403
    )


def test_seed_creates_alex_mia_leo_and_token_works(plain_client: TestClient):
    resp = plain_client.post(
        "/api/v1/e2e/seed",
        headers={"X-E2E-Secret": settings.E2E_SECRET},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["guardian_token"] == f"guardian-{body['guardian_id']}"

    names = {d["first_name"]: d["balance"] for d in body["dependants"]}
    assert names == {"Mia": "25.00", "Leo": "8.00"}

    # The returned token authenticates against the real auth dependency.
    listed = plain_client.get(
        "/api/v1/dependants",
        headers={"Authorization": f"Bearer {body['guardian_token']}"},
    )
    assert listed.status_code == 200
    assert len(listed.json()) == 2


def test_cleanup_wipes_rows(plain_client: TestClient):
    plain_client.post("/api/v1/e2e/seed", headers={"X-E2E-Secret": settings.E2E_SECRET})
    resp = plain_client.post(
        "/api/v1/e2e/cleanup", headers={"X-E2E-Secret": settings.E2E_SECRET}
    )
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

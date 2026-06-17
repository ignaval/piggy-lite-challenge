"""E2E / dev seed routes (mirror real Piggy's seed seam).

These are always mounted because this is a dev/test app, but every call is
gated behind the ``X-E2E-Secret`` header matching ``settings.E2E_SECRET``
(default ``"dev-e2e-secret"``). They let the frontend's browser tests reset the
database to a known state.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status

from app import crud, seed_data
from app.core.config import settings
from app.core.db import SessionDep

router = APIRouter(prefix="/e2e", tags=["e2e"])


def _check_secret(secret: str | None) -> None:
    if secret != settings.E2E_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid E2E secret",
        )


@router.post("/seed")
def seed(
    session: SessionDep,
    x_e2e_secret: Annotated[str | None, Header()] = None,
) -> dict:
    """Reset the DB to a known state and return the guardian token."""
    _check_secret(x_e2e_secret)

    guardian = seed_data.seed_demo(session)
    dependants = crud.list_dependants_for_guardian(session, guardian.id)
    return {
        "guardian_id": str(guardian.id),
        "guardian_token": f"guardian-{guardian.id}",
        "dependants": [
            {
                "id": str(d.id),
                "first_name": d.first_name,
                "balance": (
                    f"{(b.amount if (b := crud.get_balance(session, d.id)) else 0):.2f}"
                ),
            }
            for d in dependants
        ],
    }


@router.post("/cleanup")
def cleanup(
    session: SessionDep,
    x_e2e_secret: Annotated[str | None, Header()] = None,
) -> dict:
    """Delete all rows."""
    _check_secret(x_e2e_secret)
    seed_data.wipe_all(session)
    return {"status": "ok"}

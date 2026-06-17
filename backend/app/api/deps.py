"""Auth dependency.

Token scheme (dev/E2E seam — mirrors real Piggy's ``get_current_guardian``,
simplified): the client sends ``Authorization: Bearer guardian-{guardian_id}``.
We parse the id, load the Guardian, and 401 if anything is missing, malformed,
or unknown.

There are no passwords or sessions — the token *is* the guardian id. That keeps
the starter focused on the domain while leaving an obvious place to slot in real
auth later.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status

from app import crud
from app.core.db import SessionDep
from app.models import Guardian

_TOKEN_PREFIX = "guardian-"


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authorization token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_guardian(
    session: SessionDep,
    authorization: Annotated[str | None, Header()] = None,
) -> Guardian:
    if not authorization:
        raise _unauthorized()

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.startswith(_TOKEN_PREFIX):
        raise _unauthorized()

    raw_id = token[len(_TOKEN_PREFIX) :]
    try:
        guardian_id = UUID(raw_id)
    except ValueError:
        raise _unauthorized() from None

    guardian = crud.get_guardian(session, guardian_id)
    if guardian is None:
        raise _unauthorized()
    return guardian


CurrentGuardian = Annotated[Guardian, Depends(get_current_guardian)]

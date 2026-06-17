"""Small data-access helpers.

Thin wrappers around SQLModel queries so the routes and service layer read
clearly. No business rules live here — those belong in
``app/services/transfer_service.py``.
"""

from __future__ import annotations

from uuid import UUID

from sqlmodel import Session, select

from app.models import (
    Balance,
    Dependant,
    Guardian,
    LedgerTransaction,
)


def get_guardian(session: Session, guardian_id: UUID) -> Guardian | None:
    return session.get(Guardian, guardian_id)


def list_dependants_for_guardian(
    session: Session, guardian_id: UUID
) -> list[Dependant]:
    statement = (
        select(Dependant)
        .where(Dependant.guardian_id == guardian_id)
        .order_by(Dependant.created_at)
    )
    return list(session.exec(statement).all())


def get_dependant_for_guardian(
    session: Session, guardian_id: UUID, dependant_id: UUID
) -> Dependant | None:
    """Return the dependant only if it belongs to this guardian, else None."""
    dependant = session.get(Dependant, dependant_id)
    if dependant is None or dependant.guardian_id != guardian_id:
        return None
    return dependant


def get_balance(session: Session, dependant_id: UUID) -> Balance | None:
    return session.get(Balance, dependant_id)


def get_or_create_balance(session: Session, dependant_id: UUID) -> Balance:
    balance = session.get(Balance, dependant_id)
    if balance is None:
        balance = Balance(dependant_id=dependant_id)
        session.add(balance)
    return balance


def recent_transactions(
    session: Session, dependant_id: UUID, limit: int = 20
) -> list[LedgerTransaction]:
    statement = (
        select(LedgerTransaction)
        .where(LedgerTransaction.dependant_id == dependant_id)
        .order_by(LedgerTransaction.created_at.desc())
        .limit(limit)
    )
    return list(session.exec(statement).all())

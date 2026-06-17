"""Shared seed/reset logic used by both the ``/e2e`` routes and ``app.seed``.

Keeping the actual row creation in one place means the standalone dev seeder and
the test/E2E seed endpoint can't drift apart.
"""

from __future__ import annotations

from decimal import Decimal

from sqlmodel import Session, delete

from app.models import (
    Balance,
    Dependant,
    Guardian,
    LedgerTransaction,
    TransactionType,
)


def wipe_all(session: Session) -> None:
    """Delete every row. Children first to respect foreign keys."""
    session.exec(delete(LedgerTransaction))
    session.exec(delete(Balance))
    session.exec(delete(Dependant))
    session.exec(delete(Guardian))
    session.commit()


def seed_demo(session: Session) -> Guardian:
    """Wipe, then create guardian Alex with dependants Mia (25.00) & Leo (8.00).

    Each dependant gets a couple of ledger entries so history views aren't
    empty. Returns the created guardian.
    """
    wipe_all(session)

    guardian = Guardian(first_name="Alex")
    session.add(guardian)
    session.flush()  # assign guardian.id

    mia = Dependant(first_name="Mia", guardian_id=guardian.id)
    leo = Dependant(first_name="Leo", guardian_id=guardian.id)
    session.add(mia)
    session.add(leo)
    session.flush()  # assign dependant ids

    session.add(Balance(dependant_id=mia.id, amount=Decimal("25.00")))
    session.add(Balance(dependant_id=leo.id, amount=Decimal("8.00")))

    # A small, plausible history. Amounts here are illustrative and do not need
    # to reconcile exactly with the starting balances above.
    session.add_all(
        [
            LedgerTransaction(
                dependant_id=mia.id,
                type=TransactionType.FUNDING,
                amount=Decimal("30.00"),
                note="Weekly allowance",
            ),
            LedgerTransaction(
                dependant_id=mia.id,
                type=TransactionType.SPEND,
                amount=Decimal("5.00"),
                note="Snacks",
            ),
            LedgerTransaction(
                dependant_id=leo.id,
                type=TransactionType.FUNDING,
                amount=Decimal("10.00"),
                note="Birthday gift",
            ),
            LedgerTransaction(
                dependant_id=leo.id,
                type=TransactionType.SPEND,
                amount=Decimal("2.00"),
                note="Comic book",
            ),
        ]
    )

    session.commit()
    session.refresh(guardian)
    return guardian

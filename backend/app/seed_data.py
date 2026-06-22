"""Shared seed/reset logic used by both the ``/e2e`` routes and ``app.seed``.

Keeping the actual row creation in one place means the standalone dev seeder and
the test/E2E seed endpoint can't drift apart.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
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

    Mia's seeded history is intentionally shaped for the spending-limits
    feature: two SPEND entries inside the last 7 days and one older spend (10
    days ago). A weekly "usage this period" view therefore has data immediately,
    and the older spend lets a candidate verify the window excludes it.

    The ledger **reconciles** with the starting balance: Mia's entries net to
    exactly 25.00 (35.00 funded - 4.00 - 3.50 - 2.50 spent) and Leo's to 8.00,
    so "balance" and "sum of the ledger" agree — the invariant a real finance
    system must hold.

    Returns the created guardian.
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

    now = datetime.now(UTC)
    # Amounts net to each dependant's starting balance (see docstring): Mia ends
    # at 25.00, Leo at 8.00. Each funding predates that dependant's spends, so
    # the running balance is valid at every step (never negative), not just at
    # the end. Mia has spends inside *and* outside the last 7 days, so a weekly
    # usage window has data to show — and a boundary to exclude.
    session.add_all(
        [
            LedgerTransaction(
                dependant_id=mia.id,
                type=TransactionType.FUNDING,
                amount=Decimal("35.00"),
                note="Allowance",
                created_at=now - timedelta(days=14),
            ),
            LedgerTransaction(
                dependant_id=mia.id,
                type=TransactionType.SPEND,
                amount=Decimal("4.00"),
                note="Snacks",
                created_at=now - timedelta(days=1),
            ),
            LedgerTransaction(
                dependant_id=mia.id,
                type=TransactionType.SPEND,
                amount=Decimal("3.50"),
                note="Bus fare",
                created_at=now - timedelta(days=3),
            ),
            LedgerTransaction(
                dependant_id=mia.id,
                type=TransactionType.SPEND,
                amount=Decimal("2.50"),
                note="Older toy (outside the last 7 days)",
                created_at=now - timedelta(days=10),
            ),
            LedgerTransaction(
                dependant_id=leo.id,
                type=TransactionType.FUNDING,
                amount=Decimal("10.00"),
                note="Birthday gift",
                created_at=now - timedelta(days=4),
            ),
            LedgerTransaction(
                dependant_id=leo.id,
                type=TransactionType.SPEND,
                amount=Decimal("2.00"),
                note="Comic book",
                created_at=now - timedelta(days=2),
            ),
        ]
    )

    session.commit()
    session.refresh(guardian)
    return guardian

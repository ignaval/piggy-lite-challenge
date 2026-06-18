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
    feature: she has two SPEND entries inside the last 7 days and one older
    spend (10 days ago). Once a candidate builds limits, a weekly "usage this
    period" view has data immediately, and the older spend lets them verify that
    a period window excludes it. (Transaction amounts are illustrative history
    and do not need to reconcile exactly with the starting balances above.)

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
    session.add_all(
        [
            LedgerTransaction(
                dependant_id=mia.id,
                type=TransactionType.FUNDING,
                amount=Decimal("30.00"),
                note="Weekly allowance",
                created_at=now - timedelta(days=6),
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
                amount=Decimal("6.00"),
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

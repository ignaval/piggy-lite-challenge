"""Transfer service — funding and spending logic.

The HTTP routes are thin: they parse input and delegate to ``fund_dependant`` /
``spend``.

Each operation:
  1. resolves + authorizes the dependant (404 if not this guardian's),
  2. validates the amount: finite, > 0, at most 2 decimal places (400 otherwise),
  3. (spend only) validates sufficient balance (400 otherwise),
  4. updates the Balance and writes a LedgerTransaction atomically.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud
from app.models import Dependant, Guardian, LedgerTransaction, TransactionType

_CENTS = Decimal("0.01")


def _resolve_dependant(
    session: Session, guardian: Guardian, dependant_id: UUID
) -> Dependant:
    """Return the guardian's dependant or raise 404.

    We return 404 (not 403) for dependants that exist but belong to someone
    else, so the API never reveals whether another guardian's dependant id is
    real.
    """
    dependant = crud.get_dependant_for_guardian(session, guardian.id, dependant_id)
    if dependant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependant not found",
        )
    return dependant


def _validate_amount(amount: Decimal) -> Decimal:
    """Validate a money amount and return it normalized to 2 decimal places.

    Enforces the repo-wide "2-decimal money" rule at the boundary so a direct
    API call can't move a balance by a sub-cent amount that would then render as
    ``"0.00"``. Rejects non-positive and >2-decimal-place values as a clean 400.
    (Non-finite amounts arriving over HTTP are normally rejected earlier, by the
    schema's ``MoneyStr`` validator, as a 422; the ``is_finite`` guard here is
    defense-in-depth for direct service calls.)
    """
    if not amount.is_finite():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="amount must be a finite number",
        )
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="amount must be greater than 0",
        )
    # Reject anything finer than cent scale — including a trailing-zero "1.230"
    # (value 1.23) — so the 2-decimal-string contract matches the frontend
    # exactly. ``exponent`` is a plain int here (non-finite is rejected above);
    # a value-based check (``!= quantize``) would let "1.230" slip through.
    if amount.as_tuple().exponent < -2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="amount cannot have more than 2 decimal places",
        )
    return amount.quantize(_CENTS, rounding=ROUND_HALF_UP)


def fund_dependant(
    *,
    session: Session,
    guardian: Guardian,
    dependant_id: UUID,
    amount: Decimal,
    note: str | None = None,
) -> LedgerTransaction:
    """Credit a dependant's balance and record a FUNDING transaction."""
    _resolve_dependant(session, guardian, dependant_id)
    amount = _validate_amount(amount)

    balance = crud.get_or_create_balance(session, dependant_id)
    balance.amount = balance.amount + amount

    transaction = LedgerTransaction(
        dependant_id=dependant_id,
        type=TransactionType.FUNDING,
        amount=amount,
        note=note,
    )
    session.add(balance)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


def spend(
    *,
    session: Session,
    guardian: Guardian,
    dependant_id: UUID,
    amount: Decimal,
    note: str | None = None,
) -> LedgerTransaction:
    """Debit a dependant's balance and record a SPEND transaction.

    Raises 400 on a non-positive / mis-scaled amount or insufficient funds.
    """
    _resolve_dependant(session, guardian, dependant_id)
    amount = _validate_amount(amount)

    balance = crud.get_or_create_balance(session, dependant_id)
    if amount > balance.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance",
        )

    balance.amount = balance.amount - amount

    transaction = LedgerTransaction(
        dependant_id=dependant_id,
        type=TransactionType.SPEND,
        amount=amount,
        note=note,
    )
    session.add(balance)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

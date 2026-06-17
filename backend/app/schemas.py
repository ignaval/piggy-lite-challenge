"""Request/response models for the HTTP API.

All money crosses the wire as a **2-decimal string** (e.g. ``"10.00"``). Inputs
are parsed as ``Decimal`` and quantized; outputs are serialized via a shared
annotated type so every amount looks identical.
"""

from __future__ import annotations

from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer

from app.models import TransactionType

_CENTS = Decimal("0.01")


def _quantize(value: Decimal) -> Decimal:
    """Round to 2 decimal places (banker-friendly half-up)."""
    return value.quantize(_CENTS, rounding=ROUND_HALF_UP)


def _to_decimal(value: object) -> Decimal:
    """Coerce incoming JSON (string or number) into a Decimal.

    Strings are preferred (no float imprecision). We deliberately do NOT clamp
    sign here — ``amount > 0`` is enforced in the service layer so the API can
    return a clean 400 with a helpful message.
    """
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (ArithmeticError, ValueError) as exc:  # pragma: no cover - defensive
        raise ValueError("amount must be a valid decimal number") from exc


# Decimal that accepts string/number input and always renders as "0.00".
MoneyStr = Annotated[
    Decimal,
    BeforeValidator(_to_decimal),
    PlainSerializer(lambda v: f"{_quantize(v):.2f}", return_type=str),
]


# ---------- Requests ----------


class TransferRequest(BaseModel):
    """Body for both fund and spend."""

    amount: MoneyStr
    note: str | None = None


# ---------- Responses ----------


class DependantSummary(BaseModel):
    id: UUID
    first_name: str
    balance: MoneyStr


class TransactionRead(BaseModel):
    # from_attributes lets us build this straight from a LedgerTransaction ORM row.
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: TransactionType
    amount: MoneyStr
    note: str | None
    created_at: datetime


class DependantDetail(BaseModel):
    id: UUID
    first_name: str
    balance: MoneyStr
    transactions: list[TransactionRead]


class TransferResponse(BaseModel):
    transaction: TransactionRead
    balance: MoneyStr

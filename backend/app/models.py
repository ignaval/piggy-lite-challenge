"""SQLModel table definitions and enums.

The domain graph is intentionally tiny:

    Guardian 1──* Dependant 1──1 Balance
                          └──* LedgerTransaction

One implicit currency. Money is stored as ``Decimal`` and serialized to JSON as
a 2-decimal string at the schema layer (see ``app/schemas.py``).

NOTE: we deliberately do *not* use ``from __future__ import annotations`` here,
and relationship attributes use ``Optional["X"]`` (not ``"X" | None``).
SQLModel/SQLAlchemy resolves relationship targets from these annotations at
mapper-config time; stringified ``X | None`` forward refs fail that lookup.
That's why ruff's ``UP045`` is disabled for this file in ``pyproject.toml``.
"""

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC)


class TransactionType(StrEnum):
    """A ledger entry is either money coming in or money going out."""

    FUNDING = "FUNDING"
    SPEND = "SPEND"


class Guardian(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    first_name: str
    created_at: datetime = Field(default_factory=_utcnow)

    dependants: list["Dependant"] = Relationship(back_populates="guardian")


class Dependant(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    first_name: str
    guardian_id: UUID = Field(foreign_key="guardian.id", index=True)
    created_at: datetime = Field(default_factory=_utcnow)

    guardian: Optional["Guardian"] = Relationship(back_populates="dependants")
    balance: Optional["Balance"] = Relationship(
        back_populates="dependant",
        sa_relationship_kwargs={"uselist": False},
    )
    transactions: list["LedgerTransaction"] = Relationship(back_populates="dependant")


class Balance(SQLModel, table=True):
    # 1:1 with Dependant — the dependant id *is* the primary key.
    dependant_id: UUID = Field(foreign_key="dependant.id", primary_key=True)
    amount: Decimal = Field(default=Decimal("0"), max_digits=18, decimal_places=2)

    dependant: Optional["Dependant"] = Relationship(back_populates="balance")


class LedgerTransaction(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    dependant_id: UUID = Field(foreign_key="dependant.id", index=True)
    type: TransactionType
    amount: Decimal = Field(max_digits=18, decimal_places=2)
    note: str | None = None
    created_at: datetime = Field(default_factory=_utcnow, index=True)

    dependant: Optional["Dependant"] = Relationship(back_populates="transactions")

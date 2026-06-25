"""Dependant routes.

Deliberately thin: read endpoints query via ``crud``; the fund/spend write
endpoints delegate all rules to ``app.services.transfer_service``.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app import crud
from app.api.deps import CurrentGuardian
from app.core.db import SessionDep
from app.schemas import (
    DependantDetail,
    DependantSummary,
    TransactionRead,
    TransferRequest,
    TransferResponse,
)
from app.services import transfer_service

router = APIRouter(prefix="/dependants", tags=["dependants"])


@router.get("", response_model=list[DependantSummary])
def list_dependants(
    guardian: CurrentGuardian,
    session: SessionDep,
) -> list[DependantSummary]:
    """List the current guardian's dependants with their balances."""
    dependants = crud.list_dependants_for_guardian(session, guardian.id)
    summaries: list[DependantSummary] = []
    for dependant in dependants:
        balance = crud.get_balance(session, dependant.id)
        summaries.append(
            DependantSummary(
                id=dependant.id,
                first_name=dependant.first_name,
                balance=balance.amount if balance else 0,
            )
        )
    return summaries


@router.get("/{dependant_id}", response_model=DependantDetail)
def get_dependant(
    dependant_id: UUID,
    guardian: CurrentGuardian,
    session: SessionDep,
) -> DependantDetail:
    """Balance + most-recent transactions (newest first, last ~20)."""
    dependant = crud.get_dependant_for_guardian(session, guardian.id, dependant_id)
    if dependant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependant not found",
        )

    balance = crud.get_balance(session, dependant.id)
    transactions = crud.recent_transactions(session, dependant.id, limit=20)
    return DependantDetail(
        id=dependant.id,
        first_name=dependant.first_name,
        balance=balance.amount if balance else 0,
        transactions=[TransactionRead.model_validate(t) for t in transactions],
    )


@router.post("/{dependant_id}/fund", response_model=TransferResponse)
def fund_dependant(
    dependant_id: UUID,
    body: TransferRequest,
    guardian: CurrentGuardian,
    session: SessionDep,
) -> TransferResponse:
    """Credit a dependant's balance (creates a FUNDING transaction)."""
    transaction = transfer_service.fund_dependant(
        session=session,
        guardian=guardian,
        dependant_id=dependant_id,
        amount=body.amount,
        note=body.note,
    )
    balance = crud.get_balance(session, dependant_id)
    return TransferResponse(
        transaction=TransactionRead.model_validate(transaction),
        balance=balance.amount if balance else 0,
    )


@router.post("/{dependant_id}/spend", response_model=TransferResponse)
def spend(
    dependant_id: UUID,
    body: TransferRequest,
    guardian: CurrentGuardian,
    session: SessionDep,
) -> TransferResponse:
    """Debit a dependant's balance (creates a SPEND transaction).

    Returns 400 on a non-positive amount or insufficient balance.
    """
    transaction = transfer_service.spend(
        session=session,
        guardian=guardian,
        dependant_id=dependant_id,
        amount=body.amount,
        note=body.note,
    )
    balance = crud.get_balance(session, dependant_id)
    return TransferResponse(
        transaction=TransactionRead.model_validate(transaction),
        balance=balance.amount if balance else 0,
    )

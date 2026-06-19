"""End-to-end-ish tests for the fund/spend flow.

Covers the four required cases:
  * fund increases balance
  * spend decreases balance
  * spend with insufficient balance → 400
  * acting on another guardian's dependant → 404

Plus a couple of input-validation guards so bad input never 500s.
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Dependant, Guardian


def test_list_dependants_returns_string_balance(
    client: TestClient, dependant: Dependant
):
    resp = client.get("/api/v1/dependants")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["id"] == str(dependant.id)
    assert body[0]["first_name"] == "TestKid"
    # Money is a 2-decimal string, not a number.
    assert body[0]["balance"] == "20.00"


def test_fund_increases_balance(client: TestClient, dependant: Dependant):
    resp = client.post(
        f"/api/v1/dependants/{dependant.id}/fund",
        json={"amount": "10.00", "note": "allowance"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["balance"] == "30.00"
    assert body["transaction"]["type"] == "FUNDING"
    assert body["transaction"]["amount"] == "10.00"
    assert body["transaction"]["note"] == "allowance"


def test_spend_decreases_balance(client: TestClient, dependant: Dependant):
    resp = client.post(
        f"/api/v1/dependants/{dependant.id}/spend",
        json={"amount": "5.00", "note": "candy"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["balance"] == "15.00"
    assert body["transaction"]["type"] == "SPEND"
    assert body["transaction"]["amount"] == "5.00"


def test_spend_insufficient_balance_returns_400(
    client: TestClient, dependant: Dependant
):
    resp = client.post(
        f"/api/v1/dependants/{dependant.id}/spend",
        json={"amount": "999.00"},
    )
    assert resp.status_code == 400
    assert "insufficient" in resp.json()["detail"].lower()


def test_spend_does_not_partially_apply_on_failure(
    client: TestClient, dependant: Dependant, session: Session
):
    """A rejected spend must not move the balance."""
    client.post(
        f"/api/v1/dependants/{dependant.id}/spend",
        json={"amount": "999.00"},
    )
    detail = client.get(f"/api/v1/dependants/{dependant.id}").json()
    assert detail["balance"] == "20.00"


def test_other_guardians_dependant_returns_404(client: TestClient, session: Session):
    """A dependant that exists but isn't ours is 404, not 403."""
    other_guardian = Guardian(first_name="Stranger")
    session.add(other_guardian)
    session.commit()
    session.refresh(other_guardian)
    other_dependant = Dependant(first_name="NotMine", guardian_id=other_guardian.id)
    session.add(other_dependant)
    session.commit()
    session.refresh(other_dependant)

    # Read
    assert client.get(f"/api/v1/dependants/{other_dependant.id}").status_code == 404
    # Fund
    assert (
        client.post(
            f"/api/v1/dependants/{other_dependant.id}/fund",
            json={"amount": "5.00"},
        ).status_code
        == 404
    )
    # Spend
    assert (
        client.post(
            f"/api/v1/dependants/{other_dependant.id}/spend",
            json={"amount": "5.00"},
        ).status_code
        == 404
    )


def test_fund_non_positive_amount_returns_400(client: TestClient, dependant: Dependant):
    for bad in ("0", "-5.00"):
        resp = client.post(
            f"/api/v1/dependants/{dependant.id}/fund",
            json={"amount": bad},
        )
        assert resp.status_code == 400


def test_detail_lists_transactions_newest_first(
    client: TestClient, dependant: Dependant
):
    client.post(f"/api/v1/dependants/{dependant.id}/fund", json={"amount": "10.00"})
    client.post(f"/api/v1/dependants/{dependant.id}/spend", json={"amount": "3.00"})
    detail = client.get(f"/api/v1/dependants/{dependant.id}").json()
    txns = detail["transactions"]
    assert len(txns) == 2
    # Most recent (the spend) comes first.
    assert txns[0]["type"] == "SPEND"
    assert txns[1]["type"] == "FUNDING"


def test_fund_rejects_more_than_two_decimals(
    client: TestClient, dependant: Dependant
):
    """A sub-cent amount must be rejected, not silently rounded to 0.00."""
    resp = client.post(
        f"/api/v1/dependants/{dependant.id}/fund",
        json={"amount": "0.001"},
    )
    assert resp.status_code == 400
    assert "decimal" in resp.json()["detail"].lower()
    # Balance is untouched.
    detail = client.get(f"/api/v1/dependants/{dependant.id}").json()
    assert detail["balance"] == "20.00"


def test_spend_rejects_more_than_two_decimals(
    client: TestClient, dependant: Dependant
):
    resp = client.post(
        f"/api/v1/dependants/{dependant.id}/spend",
        json={"amount": "1.005"},
    )
    assert resp.status_code == 400
    assert "decimal" in resp.json()["detail"].lower()


def test_rejects_trailing_zero_sub_cent_amount(
    client: TestClient, dependant: Dependant
):
    """A 3-decimal string whose value is 2 dp (e.g. "1.230") is still rejected,
    matching the frontend: the contract is 2-decimal *strings*, not just
    2-decimal *values*."""
    resp = client.post(
        f"/api/v1/dependants/{dependant.id}/fund",
        json={"amount": "1.230"},
    )
    assert resp.status_code == 400
    assert "decimal" in resp.json()["detail"].lower()
    # Balance is untouched.
    detail = client.get(f"/api/v1/dependants/{dependant.id}").json()
    assert detail["balance"] == "20.00"


def test_rejects_non_finite_amount(client: TestClient, dependant: Dependant):
    """NaN/Infinity must be rejected (4xx), never applied or 500."""
    for bad in ("NaN", "Infinity"):
        resp = client.post(
            f"/api/v1/dependants/{dependant.id}/fund",
            json={"amount": bad},
        )
        assert resp.status_code in (400, 422), f"{bad} -> {resp.status_code}"


def test_amount_is_normalized_to_two_decimals(
    client: TestClient, dependant: Dependant
):
    resp = client.post(
        f"/api/v1/dependants/{dependant.id}/fund",
        json={"amount": "10.5"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["transaction"]["amount"] == "10.50"
    assert body["balance"] == "30.50"

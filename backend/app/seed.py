"""Standalone dev seeder: ``python -m app.seed``.

Creates tables (if needed), resets the dev database to guardian **Alex** with
dependants **Mia** (25.00) and **Leo** (8.00), and prints the guardian token to
paste into the frontend login.
"""

from __future__ import annotations

from sqlmodel import Session

from app.core.db import create_db_and_tables, engine
from app.crud import get_balance, list_dependants_for_guardian
from app.seed_data import seed_demo


def main() -> None:
    create_db_and_tables()

    with Session(engine) as session:
        guardian = seed_demo(session)
        dependants = list_dependants_for_guardian(session, guardian.id)

        print("\n✅ Seeded the dev database.\n")
        print(f"Guardian: {guardian.first_name} ({guardian.id})")
        print("Dependants:")
        for dependant in dependants:
            balance = get_balance(session, dependant.id)
            amount = balance.amount if balance else 0
            print(f"  - {dependant.first_name}: {amount:.2f}")

        token = f"guardian-{guardian.id}"
        print("\n👉 Guardian token (paste into the frontend /login):\n")
        print(f"    {token}\n")


if __name__ == "__main__":
    main()

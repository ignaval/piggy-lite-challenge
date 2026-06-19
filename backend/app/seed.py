"""Standalone dev seeder: ``python -m app.seed``.

Resets the dev database to guardian **Alex** with dependants **Mia** (25.00) and
**Leo** (8.00), and prints the guardian token to paste into the frontend login.

Table creation mirrors the app's startup behavior: when
``CREATE_TABLES_ON_STARTUP`` is set (bare-metal/SQLite, the default) the seeder
creates tables for zero setup; under Docker/Postgres the flag is off, so the
seeder relies on the Alembic-migrated schema. That keeps a forgotten migration
(e.g. a new spending-limit table) from being silently papered over by
``create_all`` here and making the feature look like it works.
"""

from __future__ import annotations

from sqlmodel import Session

from app.core.config import settings
from app.core.db import create_db_and_tables, engine
from app.crud import get_balance, list_dependants_for_guardian
from app.seed_data import seed_demo


def main() -> None:
    # Mirror app startup: only create_all when configured to (see module docstring).
    if settings.CREATE_TABLES_ON_STARTUP:
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

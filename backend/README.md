# Piggy Lite — Backend

A small, idiomatic **FastAPI + SQLModel** service: guardians fund their
dependants, and dependants spend from their own balance. SQLite by default, so
it runs with zero setup.

> This is a starter for a take-home. It ships the **fund / spend** flow only —
> adding **spending limits** is the candidate's task. Read *How a spend flows
> today* below to get oriented.

---

## Stack

- Python 3.11+
- FastAPI · SQLModel · Uvicorn
- pytest · httpx (via Starlette's `TestClient`)
- Alembic (one initial migration; tables are also created on startup)
- SQLite (file `piggy_lite.db`)

## Install

### With `uv` (recommended)

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
# or, if you prefer a lockfile-driven flow:
# uv sync --extra dev
```

### With pip

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optionally copy the env file (everything has working defaults, so this is not
required):

```bash
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload
```

- API base: `http://localhost:8000/api/v1`
- Health check: `GET http://localhost:8000/health`
- Interactive docs: `http://localhost:8000/docs`

Tables are created automatically on startup, so no migration step is needed to
run locally.

## Seed demo data

```bash
python -m app.seed
```

This resets the dev DB to guardian **Alex** with dependants **Mia** (25.00) and
**Leo** (8.00) plus a little transaction history, then prints a token like:

```
    guardian-3f2c1b6e-...-...
```

Paste that into the frontend `/login` to see data immediately.

## Test

```bash
pytest -q
```

Tests use a throwaway temp-SQLite database per test and override the
`get_current_guardian` dependency with a pre-created test guardian — the same
seam real Piggy uses for its E2E tests. `test_auth.py` exercises the real token
parsing without the override.

## Migrations (Alembic)

The app creates tables on startup, so you don't need Alembic just to run. It's
configured for the realistic "add a model + migration" workflow you'll use when
adding the spending-limits model:

```bash
# after editing app/models.py
alembic revision --autogenerate -m "add spending limit"
alembic upgrade head
```

`alembic/env.py` pulls the DB URL from `app.core.config.settings` and the target
metadata from `SQLModel.metadata`, so autogenerate sees your models. The initial
migration lives at `alembic/versions/0001_initial_schema.py`.

On the local SQLite path the app **stamps** the freshly `create_all`'d database
to the latest revision, so `alembic upgrade head` is a clean no-op rather than a
"table already exists" error. When you add the spending-limits model, run
`alembic revision --autogenerate` **before** you next start the app or reseed —
otherwise `create_all` will have already created the new table and autogenerate
will see nothing to do. (The Docker path sidesteps this: it runs migrations and
never `create_all`s.)

---

## HTTP API

All amounts are decimal **strings** (e.g. `"10.00"`). Auth is
`Authorization: Bearer guardian-{guardian_id}`.

| Method & path | Body | Success | Notes |
| --- | --- | --- | --- |
| `GET /api/v1/dependants` | — | `200 [{ id, first_name, balance }]` | current guardian's dependants |
| `GET /api/v1/dependants/{id}` | — | `200 { id, first_name, balance, transactions[] }` | newest-first, last ~20; `404` if not yours |
| `POST /api/v1/dependants/{id}/fund` | `{ amount, note? }` | `200 { transaction, balance }` | `400` on invalid amount (≤ 0 or > 2 decimal places); `422` if non-finite/non-numeric |
| `POST /api/v1/dependants/{id}/spend` | `{ amount, note? }` | `200 { transaction, balance }` | `400` on invalid amount (as above) or insufficient balance |

A `transaction` is `{ id, type: "FUNDING"|"SPEND", amount, note, created_at }`.

### E2E / dev seed routes (gated by `X-E2E-Secret`)

- `POST /api/v1/e2e/seed` — wipe + reseed Alex/Mia/Leo; returns
  `{ guardian_id, guardian_token, dependants[] }`.
- `POST /api/v1/e2e/cleanup` — delete all rows.

Both require header `X-E2E-Secret: <settings.E2E_SECRET>` (default
`dev-e2e-secret`).

### Quick smoke test with curl

```bash
TOKEN=$(curl -s -X POST localhost:8000/api/v1/e2e/seed \
  -H "X-E2E-Secret: dev-e2e-secret" | python -c "import sys,json;print(json.load(sys.stdin)['guardian_token'])")

curl -s localhost:8000/api/v1/dependants -H "Authorization: Bearer $TOKEN"
```

---

## How a spend flows today

This is the path to read first.

1. **Route** — `app/api/routes/dependants.py` → `spend()`. It parses the request
   (`amount` as a `Decimal`, optional `note`) and the authenticated guardian,
   then **delegates** to the service. Routes hold no business rules.
2. **Service** — `app/services/transfer_service.py` → `spend(...)`. It runs the
   rules for the operation:
   - resolve + authorize the dependant (404 if it isn't this guardian's),
   - validate the amount — finite, `> 0`, at most 2 decimal places (400 otherwise),
   - validate **sufficient balance** (400 `"Insufficient balance"` otherwise),
   - decrement `Balance` and append a `SPEND` `LedgerTransaction`, committed
     together.
3. **Response** — the route returns `{ transaction, balance }` with money as
   2-decimal strings (`app/schemas.py`).

Funding mirrors this via `fund_dependant(...)` (credits the balance, writes a
`FUNDING` transaction).

## Layout

```
backend/
  app/
    main.py                  # FastAPI app: CORS, startup table-create, routers
    core/config.py           # pydantic-settings (DB url, E2E secret, CORS)
    core/db.py               # engine + get_session (SessionDep)
    api/deps.py              # get_current_guardian (Bearer guardian-{id})
    api/routes/dependants.py # GET/POST dependant endpoints (thin)
    api/routes/e2e.py        # seed/cleanup (secret-gated)
    models.py                # SQLModel tables + TransactionType enum
    schemas.py               # request/response models (money as strings)
    crud.py                  # small data-access helpers
    services/transfer_service.py  # fund/spend business rules
    seed_data.py             # shared seed/reset logic
    seed.py                  # `python -m app.seed`
  tests/
    conftest.py              # temp SQLite, TestClient, auth override, fixtures
    test_transfer_flow.py    # fund↑, spend↓, insufficient→400, ownership→404
    test_auth.py             # real Bearer token parsing
    test_e2e_seed.py         # seed/cleanup + secret gate
  alembic/ + alembic.ini     # 0001_initial migration
  pyproject.toml             # uv-friendly
  requirements.txt           # pip alternative
  .env.example
```

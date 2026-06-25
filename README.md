# Piggy Lite

A small, intentionally-trimmed slice of **Piggy Wallet**, a family finance app.
**Guardians** fund their kids (**Dependants**); kids spend from their own
balance. This repo is the starting point for an engineering take-home.

> 📋 **Your task is in [`CHALLENGE.md`](./CHALLENGE.md). Read it first.**
> This README is the technical orientation: how to run the app and how it's put
> together.

## What's here

| | Stack | Path |
|---|---|---|
| **Backend** | FastAPI · SQLModel · SQLite · Alembic · pytest | [`backend/`](./backend) |
| **Frontend** | Next.js (app router) · React 19 · React Query · next-intl | [`frontend/`](./frontend) |

Each app has its own `README.md` with the full details. Quick start below.

## Quick start

Two ways to run it. **Docker is the easy path** — no local Python/Node/uv
needed, and it matches the real Piggy stack (docker-compose + Postgres).

### Option A — Docker (recommended)

Requires Docker Desktop. From the repo root:

```bash
docker compose up --build      # Postgres + backend (:8000) + frontend (:3000)
```

Then, in a second terminal, seed demo data (prints a login token):

```bash
docker compose exec backend python -m app.seed
```

Open http://localhost:3000 and paste the printed `guardian-…` token at
`/login`. Run the suites inside the containers:

```bash
docker compose exec backend pytest -q
docker compose exec frontend npm run test
```

Tear down (add `-v` to also drop the Postgres volume):

```bash
docker compose down
```

> Docker runs **Postgres** (like real Piggy); running locally (Option B) uses
> **SQLite** for zero setup. Same code — only `DATABASE_URL` differs.

### Option B — run locally (no Docker)

Run the **backend first** (the frontend talks to it), then the frontend.

#### 1. Backend → http://localhost:8000

```bash
cd backend

# install (uv recommended)
uv venv && source .venv/bin/activate && uv pip install -e ".[dev]"
#   …or with pip:
#   python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# seed the dev database — prints a guardian token you'll paste into the frontend
python -m app.seed

# run
uvicorn app.main:app --reload
```

`python -m app.seed` creates guardian **Alex** with two dependants — **Mia**
($25.00) and **Leo** ($8.00) — and prints a token like
`guardian-3f2a…`. Copy it. Interactive API docs live at http://localhost:8000/docs.

Mia's seeded history includes spends both inside and outside the last 7 days, so
once you build limits you can eyeball a weekly usage window (and its reset)
right away.

#### 2. Frontend → http://localhost:3000

```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL defaults to http://localhost:8000
npm run dev
```

Open http://localhost:3000, you'll land on **`/login`** — paste the
`guardian-…` token from the seed step, and you're in. You'll see Mia and Leo,
and you can fund and spend.

## How a spend flows today

This is the path you'll be extending. Follow it before you write anything:

```
Frontend  components/SpendButton + TransferForm
            └─ hooks/useDependants.ts  →  useSpend()  (React Query mutation)
                 └─ hooks/useAuthenticatedAPI.ts  →  POST /api/v1/dependants/{id}/spend
                                                       (Authorization: Bearer guardian-{id})
Backend   app/api/routes/dependants.py   ← thin route, just parses + delegates
            └─ app/services/transfer_service.py  →  spend(...)
                 └─ app/crud.py  →  balance + LedgerTransaction (atomic commit)
```

## Conventions worth knowing

- **Money is a 2-decimal string** end to end (`"25.00"`), in every request and
  response. Parse to a precise type on the backend; never use floats for money.
- **Auth** is a dev seam: `Authorization: Bearer guardian-{guardian_id}`. A
  guardian may only act on their own dependants (otherwise `404`). The frontend
  stores the token in `localStorage` under `piggy_token`.
- **i18n is mandatory.** All user-facing text comes from
  `frontend/i18n/locales/en.json` + `es.json` via `useTranslations`.
  **Never hardcode user-facing strings** — add a key to **both** locale files.
- **Timestamps are UTC.** `created_at` is timezone-aware UTC; compute any time
  windows (e.g. a spending-limit period) in UTC.
- The backend auto-creates tables on startup, **and** ships Alembic so you can
  do the real "add a model → generate a migration" workflow
  (`alembic revision --autogenerate -m "…"`).

## Testing

```bash
# backend
cd backend && pytest -q

# frontend
cd frontend
npm run test        # Vitest unit tests
npm run typecheck   # tsc --noEmit
npm run lint
npm run test:e2e    # Playwright E2E — host-only (see note below)
```

> **Playwright E2E runs on the host, not inside the Docker container.** It drives
> the published `:3000`/`:8000` ports — so it works whether the stack is up via
> Docker (Option A) or running locally (Option B) — but the lean frontend image
> ships no browser. One-time host setup: `cd frontend && npm install && npx
> playwright install`, then `npm run test:e2e`. (Even Docker-path users need this
> single local install for E2E, though running the app itself needs no local Node.)

There's an end-to-end test seam mirroring the real product: the backend exposes
`POST /api/v1/e2e/seed` and `/cleanup` (header `X-E2E-Secret: dev-e2e-secret`),
and the Playwright suite uses it to set up data. Reuse it for your own tests.

Happy building. 🐷

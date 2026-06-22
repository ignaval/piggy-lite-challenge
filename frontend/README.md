# Piggy Lite — Frontend

A small Next.js (App Router) + React + TypeScript app for the Piggy Lite
take-home. It's a guardian-facing UI: log in with a dev token, see your
dependants and their balances, **send funds**, and open a dependant to view
their **transaction history** and **record a spend**.

> This is a starter. There is intentionally **no spending-limits feature** — that
> is the candidate's task.

## Stack

- **Next.js 15** (App Router) + **React 19** + **TypeScript**
- **@tanstack/react-query** for server state
- **next-intl** for i18n (English + Spanish)
- **Tailwind CSS** for minimal styling
- **Vitest** (unit) + **Playwright** (browser E2E)

No Privy, wagmi, viem, or blockchain — the only auth is a dev token (below).

## Prerequisites

- Node.js 18.18+ (Node 20/22 recommended)
- The **backend** running and seeded — see `../backend/README.md`.

## Install & run

```bash
npm install
cp .env.local.example .env.local   # then edit if your backend isn't on :8000
npm run dev                        # http://localhost:3000
```

### Environment

| Variable              | Default                 | Purpose                                  |
| --------------------- | ----------------------- | ---------------------------------------- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend base URL. The app adds `/api/v1`. |

## Logging in (dev token seam)

There is no real auth. Authentication is a token stored in `localStorage` under
the key **`piggy_token`** with the value **`guardian-{id}`** — mirroring real
Piggy's `/test-login` dev seam.

1. Seed the backend so there's data and a token to use:
   ```bash
   cd ../backend && python -m app.seed
   ```
   It prints a guardian token like `guardian-1a2b3c...`.
2. Open <http://localhost:3000/login>, paste that token (you can also paste just
   the guardian **id** — the app prefixes `guardian-` for you), and continue.
3. You'll land on the dashboard with dependants **Mia** and **Leo**.

## What you can do

- **Dashboard (`/`)** — list of dependants with balances; **Send funds** to any
  of them (records a `FUNDING` transaction).
- **Dependant detail (`/dependants/[id]`)** — current balance, recent
  transaction history, and a **Spend** action (records a `SPEND`). Backend
  errors (e.g. _insufficient balance_) are shown inline.

## API contract consumed

All amounts are decimal **strings** (e.g. `"10.00"`).

| Method & path                       | Response                                                             |
| ----------------------------------- | ------------------------------------------------------------------- |
| `GET /dependants`                   | `[{ id, first_name, balance }]`                                     |
| `GET /dependants/{id}`              | `{ id, first_name, balance, transactions: [...] }`                  |
| `POST /dependants/{id}/fund`        | body `{ amount, note? }` → `{ transaction, balance }`               |
| `POST /dependants/{id}/spend`       | body `{ amount, note? }` → `{ transaction, balance }`               |

The request layer lives in `hooks/useAuthenticatedAPI.ts` (reads
`NEXT_PUBLIC_API_URL`, prefixes `/api/v1`, attaches
`Authorization: Bearer {piggy_token}`, returns `{ data, error }`). React Query
hooks (`useDependants`, `useDependant`, `useFund`, `useSpend`) wrap it in
`hooks/useDependants.ts`.

## Internationalization (i18n) — please read

**Never hardcode user-facing text. Add keys to `i18n/locales/en.json` and
`i18n/locales/es.json`** and render them with the `useTranslations` hook from
`next-intl`. Both locale files must stay in sync. There is a language switcher
in the header (EN/ES) backed by a `PIGGY_LOCALE` cookie.

This convention is graded — any new UI you add (including the spending-limits
feature) must follow it.

The starter surfaces the backend's existing error `detail` strings (e.g.
_insufficient balance_) verbatim, as a dev-facing simplification. Any **new**
user-facing error you introduce — like a "limit exceeded" message — must be
localized too: return a stable error **code** from the backend and map it to an
i18n key on the client, rather than rendering a hardcoded English string inside
the Spanish UI.

## Testing

```bash
npm run test        # Vitest unit tests (e.g. the money formatter)
npm run test:unit   # same, single run
npm run test:e2e    # Playwright browser E2E — run on the host (needs the backend running + seedable)
```

Run E2E from the host, not inside the Docker container. One-time host setup:
`npm install` (local deps) + `npx playwright install` (the browser). It then
drives the published `:3000` / `:8000` ports, which the Docker stack or a local
backend+frontend both expose. (Docker-path candidates need this local install
even though running the app itself needs no local Node.)

The Playwright spec (`e2e/tests/login.spec.ts`) seeds the backend via
`POST /api/v1/e2e/seed` (header `X-E2E-Secret`, default `dev-e2e-secret`), logs
in with the returned token, and asserts the dashboard shows the seeded
dependants. Point it at a non-default backend with:

```bash
E2E_API_URL=http://localhost:8000 E2E_SECRET=dev-e2e-secret npm run test:e2e
```

## Scripts

| Script             | Does                                |
| ------------------ | ----------------------------------- |
| `npm run dev`      | Start the dev server (port 3000)    |
| `npm run build`    | Production build                    |
| `npm run start`    | Serve the production build          |
| `npm run lint`     | ESLint (`next lint`)                |
| `npm run typecheck`| `tsc --noEmit`                      |
| `npm run test`     | Vitest unit tests                   |
| `npm run test:e2e` | Playwright E2E                      |

## Project structure

```
frontend/
  app/
    layout.tsx                 # root layout: NextIntlClientProvider + React Query
    providers.tsx              # React Query client
    globals.css
    page.tsx                   # guardian dashboard (/)
    login/page.tsx             # dev token entry (/login)
    dependants/[id]/page.tsx   # dependant detail (/dependants/[id])
  components/
    AuthGuard.tsx  Header.tsx  Modal.tsx  Button.tsx  Money.tsx
    LanguageSwitcher.tsx
    DashboardClient.tsx  FundButton.tsx
    DependantDetailClient.tsx  SpendButton.tsx
    TransferForm.tsx  TransactionList.tsx
  hooks/
    useAuthenticatedAPI.ts     # fetch wrapper -> { data, error }
    useDependants.ts           # React Query hooks (list/detail/fund/spend)
  lib/
    auth.ts                    # piggy_token localStorage helpers
    money.ts                   # formatMoney / normalizeAmount
    types.ts                   # API contract types
  i18n/
    config.ts  request.ts
    locales/en.json  locales/es.json
  __tests__/money.test.ts      # Vitest unit test
  e2e/tests/login.spec.ts      # Playwright E2E
```

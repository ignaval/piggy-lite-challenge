# Piggy Wallet — Engineering Take-Home: Spending Limits

Welcome, and thanks for taking the time. This challenge is a small but real
full-stack feature. We care more about **how you work and decide** than about
finishing 100% of it.

## TL;DR

- **Time:** aim for **3–6 focused hours**. The scope is deliberately larger than
  that — **prioritize, and tell us what you cut and why.**
- **You will use AI coding tools** (Claude Code, Codex, Cursor, etc.). We
  encourage it, and we ask you to **save your session transcripts** (see
  _What to submit_).
- **Deliverables:** a pull request + your AI transcripts + a short reflection.
- After you submit, we do a **~45-minute live review** together.

## The app

Piggy Wallet is a family finance app. **Guardians** fund their kids
(**Dependants**), and kids spend from their own balance.

You're working in `piggy-lite-challenge` — a trimmed-down but working slice of
the product:

- **`backend/`** — FastAPI + SQLModel. Models for `Guardian`, `Dependant`, a
  per-dependant `Balance`, and a `LedgerTransaction`. Two working actions:
  **fund a dependant** and **record a dependant's spend**. There's a service
  layer, a simple token auth dependency, and an end-to-end test seam.
- **`frontend/`** — Next.js + React Query. A guardian dashboard (dependants +
  balances), a "send funds" flow, a dependant detail view (balance + history),
  and an i18n setup (`en` / `es`).

👉 **Start by getting it running and reading how a transaction flows
end-to-end today.** The quickest way to boot the whole stack is
`docker compose up` (see the root `README.md`); there's also a no-Docker path.
Each app's `README.md` has run/seed/test instructions, and the root
`README.md` points you at the spend path.

## Your task: add Spending Limits

Let a guardian cap how much a dependant spends over a period.

### Must have (the core)

1. A guardian can **set a spending limit** for a dependant: an amount + a period
   (e.g. weekly or monthly).
2. The limit is **enforced** when a dependant spends — a spend that would exceed
   it is handled appropriately (you decide how; see below).
3. A guardian and/or dependant can **see current usage vs. the limit**
   (e.g. "$30 of $50 used this week").
4. It's **full-stack**: backend (model + migration + endpoints + enforcement)
   and frontend (set the limit + see usage), with **tests**, and **all new UI
   text in i18n** (no hardcoded strings — note the existing convention).

   _The backend's existing error `detail` strings (e.g. "Insufficient balance")
   are developer-facing — the starter surfaces them to the user verbatim as a
   deliberate simplification, and you don't need to retrofit i18n onto them. But
   any **new** user-facing message you introduce — including a "limit exceeded"
   error — must be localized. If you surface it from the backend, return a stable
   error **code** (or otherwise make it machine-readable) and map it to an i18n
   key on the client; don't render a hardcoded English `detail` inside the
   Spanish UI._

**Scope notes (so you don't over-build).** Piggy Lite is **single-currency** —
one implicit 2-decimal currency — and has **no dependant-facing UI or login**: a
guardian records spends on a dependant's behalf, so "enforced when a dependant
spends" means the spend flow/endpoint, not a separate kid app. And **the
smallest complete slice**, if time is tight, is one period type (e.g. a rolling
7-day window), block-only enforcement, and a usage indicator on the existing
guardian dependant view — with a migration and tests. Ship that end-to-end
before touching anything under _Nice to have_.

### The spec is intentionally incomplete

Part of what we're evaluating is the decisions you make on the open questions.
Among them:

- What does the **period** mean — a rolling 7/30 days, or a calendar
  week/month? When and how does usage reset?
- When a spend would cross the limit, do you **block it, allow up to the
  remaining amount, warn, or require guardian approval?**
- Does incoming money (a guardian funding the kid) affect usage, or is usage
  purely the sum of spends in the period?
- Where does enforcement belong so it **can't be bypassed?**

Make reasonable calls, keep them consistent, and be ready to defend them.
There's no single right answer — we want your judgment.

### Cases worth thinking about

We'll look at how your solution behaves (and how you test it) for cases like:
no limit set; updating or removing a limit; a spend exactly **at** the limit vs.
just **over** it; usage at a period boundary / reset; and what happens when a
spend fails **both** the balance check and the limit check (which error wins?).
You don't have to handle every one — but show you considered them.

### Nice to have (only if time allows — don't sacrifice the core)

Per-category limits; a soft warning at e.g. 80%; concurrency safety; richer
tests; polished UX.

### We may dig into these in the live review

You won't build these, but be ready to talk through them:

- In the real Piggy, a dependant's money leaves through **several** transfer
  paths (internal spends, external withdrawals, …), not a single `spend()`.
  Where would a spending-limit rule live so it covers **all** of them, and which
  transfer types should count toward "spend"?
- Piggy Lite is single-currency; in production, balances are per
  **asset/ticker** at higher precision. How would you model and enforce limits
  **per asset**?
- The starter's `spend()` reads the balance, checks, then writes. Under real
  concurrency, what breaks — and how would you make the check-and-debit atomic?

## What to submit

You'll work in a **private** GitHub repo we set up for you (generated from this
template) — your code and transcripts stay private to you and the hiring team,
not visible to other candidates. Please don't fork this public repo or open a PR
against it.

1. **A pull request in your private repo** (base its `main`). Write the
   description like a real one: what you built, the decisions you made and the
   alternatives you rejected, what you'd do with more time, and how to test it.
   (The repo ships a PR template to start from.)
2. **Your AI session transcripts**, committed to your private repo (e.g. an
   `/ai-transcripts` folder) or linked. _Start capturing before you write any
   code — it's easy to forget to hit record._ Claude Code: the session
   transcript / `.jsonl` or a copy-paste is fine. Cursor/Codex: export or
   screenshots. **Messy, exploratory prompting is fine** — we want your real
   process, not a cleaned-up version. Your repo is private, but still **redact
   any secrets, API keys, tokens, or personal information** before committing.
3. **A short reflection** — fill in the `REFLECTION.md` stub in this repo (½–1
   page):
   - How did you use AI tools — what did you delegate vs. write/decide yourself?
   - Where did the AI suggest something you **overrode or corrected**, and why?
   - Which open decision above did you find hardest, and how did you resolve it?
   - What did you cut for time, and what would you do next?

## How we'll evaluate

Engineering judgment on the open decisions; how effectively and **critically**
you use AI tools; correctness and testing; fit with the existing code's
conventions; and clear communication. In the live review you'll walk us through
your PR, explain a couple of specific pieces, and make a small change with us.

## Ground rules

- Use any AI tools and any docs. Don't have another person do it for you.
- If something in the starter repo is genuinely broken or blocking, email us —
  getting unblocked well is also a signal.
- Have fun with it. 🐷

## What I built

<!-- A short tour of the feature and the key files you touched. -->

## Decisions & rejected alternatives

<!-- The open questions you faced (period semantics & reset; block vs. partial vs.
warn vs. require-approval; does funding affect usage; where enforcement lives;
which error wins) — what you chose and what you turned down, and why. -->

## How to test it

<!-- Steps to exercise it by hand, plus the automated tests you added. -->

## With more time

<!-- What you'd do next, and anything you knowingly cut. -->

## Checklist

- [ ] `backend`: `pytest -q` passes
- [ ] `backend`: a schema change ships an Alembic migration (`alembic upgrade head`; `alembic check` clean) — not just `create_all`
- [ ] `frontend`: `npm run typecheck`, `npm run lint`, and `npm run test` pass
- [ ] New user-facing strings are in **both** `en.json` and `es.json` (no hardcoded text; **new** surfaced backend errors localized too — existing starter errors like `Insufficient balance` are fine as-is)
- [ ] `REFLECTION.md` filled in, and AI transcripts attached (secrets redacted)

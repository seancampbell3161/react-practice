# Interview Prep Lab

A lab bench, not an app. Every failure mode from the study guide exists here as
code you can toggle between its broken and its fixed form — so you can *watch*
the failure rather than read about it.

The rule the whole repo follows: a `# BUG:` comment always has a `# FIX:` a few
lines away. `git grep "BUG:"` is a tour of the syllabus, and
[`TOUR.md`](TOUR.md) is the index.

**Stack.** FastAPI · SQLAlchemy 2.0 (async) · Pydantic v2 · Alembic · Postgres 16
· React 18 · Vite · TypeScript · TanStack Query. Postgres and Redis run in
Docker. Deliberately not SQLite: several exercises (`SELECT FOR UPDATE`, real
constraint behaviour, deep-offset cost) only behave honestly on Postgres.

---

## Quick start

```bash
# 1. infrastructure  (Postgres on :5435, Redis on :6380)
docker compose up -d

# 2. backend
cd backend
uv sync
uv run alembic upgrade head
uv run python -m app.seed              # 20 reports; --reports 50000 when you want it to hurt
uv run fastapi dev app/main.py --port 8000

# 3. frontend, in a second terminal
cd frontend
npm install
npm run dev                            # http://localhost:5173
```

Ports are deliberately non-default (Postgres `5435`, Redis `6380`) so this stack
never fights something you already run locally.

## The instrument

Everything in this lab is measured with one number: **`X-Query-Count`**, a
response header carrying the count of SQL statements that request issued.

```bash
curl -si localhost:8000/health | grep -i x-query-count          # 1
curl -si 'localhost:8000/reports?limit=100' | grep -i x-query-count  # 2, at any limit
```

The frontend shows the same number as a badge, so a page and its endpoint tell
you the same story. In tests it is the `assert_max_queries(n)` fixture:

```python
with assert_max_queries(2):
    await client.get("/reports?limit=100")
```

Transaction bookkeeping (`BEGIN`/`COMMIT`/`SAVEPOINT`) is excluded, so the number
means the same thing in dev and under pytest.

Need to know *which* queries, not just how many? `LAB_ECHO_SQL=true`.

## Commands

```bash
# backend/
uv run pytest                    # tests, against a real Postgres (lab_test)
uv run ruff check . && uv run ruff format --check .
uv run mypy app tests
uv run python -m app.seed --reports 50000

# frontend/
npm run build                    # tsc -b && vite build
npm run lint

# repo root
docker compose up -d
docker compose down              # add -v to wipe the volumes
```

Phase 9 adds a `Makefile` wrapping these.

## Layout

```
backend/
  app/
    main.py          app factory
    settings.py      pydantic-settings, all LAB_-prefixed
    db.py            async engine + session-per-request
    models.py        Org -> User -> Report
    query_count.py   the instrument
    middleware.py    X-Query-Count header
    seed.py          python -m app.seed --reports N
    routers/
  alembic/           async env.py, wired to app.settings
  tests/             conftest.py holds assert_max_queries
frontend/
  src/api.ts         fetch wrapper that surfaces X-Query-Count
  src/pages/
docker-compose.yml   Postgres 16 + Redis 7, healthchecked
TOUR.md              the index of every BUG:/FIX: pair
```

## Domain

`Org → User → Report`, multi-tenant on purpose — two orgs is what makes the
authorization exercises real rather than hypothetical.

`Report.cost_cents` and `Report.internal_notes` are sensitive by construction. If
either ever appears in a client response, that is the bug being taught.

Seeded users are `ada|brice|cleo|dev|esme @ acme.test` and the same five
`@globex.test`; `ada` is the admin in each org. The seed prints every id, so
cross-org curls are copy-paste.

## Build status

| Phase | Topic | Status |
|-------|-------|--------|
| 0 | Scaffold & harness | ✅ done |
| 1 | ORM failure families (N+1, materialization) | next |
| 2 | Validation boundary & mass assignment | |
| 3 | Broken object-level authorization | |
| 4 | Async correctness & the blocking event loop | |
| 5 | Transactions, idempotency & the outbox | |
| 6 | Pagination & a lost-update race | |
| 7 | Auth hardening & JWT pitfalls | |
| 8 | React failure modes | |
| 9 | Testing patterns | |
| 10 | Migration drill & TOUR finalize | |

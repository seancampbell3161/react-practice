# TOUR — the index of every BUG:/FIX: pair

The map from this repo back to the study guide. Each row is a pair of code paths
that differ by roughly one line: hit the broken one, watch it fail, then hit the
fixed one and watch the number change.

`git grep -n "BUG:"` walks the same list from the command line.

> **Status:** Phase 0 complete. The table below fills in phase by phase.

---

## 0 · The instrument

No BUG/FIX pair — this phase builds the thing the rest of the lab is measured
with, so it is worth knowing before you go further.

| What | Where |
|------|-------|
| Query counter (`after_cursor_execute` listener) | `backend/app/query_count.py` |
| `X-Query-Count` response header | `backend/app/middleware.py` |
| `assert_max_queries(n)` pytest fixture | `backend/tests/conftest.py` |
| Per-test Postgres transaction + rollback | `backend/tests/conftest.py` |
| Seed, incl. `--reports 50000` | `backend/app/seed.py` |

Two details in there are worth reading rather than skimming, because both are
the kind of thing an interviewer can push on:

1. **The counter lives in a `ContextVar` holding a mutable object.** With the
   async engine, the SQLAlchemy listener does not run in your coroutine — it runs
   in a greenlet driving the sync DBAPI layer. Reading a ContextVar across that
   boundary is reliable; writing one is not. So the listener mutates a counter
   object in place instead of calling `.set()`. (`app/query_count.py`)

2. **The middleware is raw ASGI, not `BaseHTTPMiddleware`.** Raw ASGI middleware
   runs in the same task as the endpoint, so it and the endpoint unambiguously
   share a context. `BaseHTTPMiddleware` spawns the endpoint in a child task,
   which *copies* the context — it happens to work here, but "happens to work" is
   not what you want from your measuring instrument. (`app/middleware.py`)

**Try it:**

```bash
curl -si localhost:8000/health              | grep -i x-query-count   # 1
curl -si 'localhost:8000/reports?limit=5'   | grep -i x-query-count   # 2
curl -si 'localhost:8000/reports?limit=200' | grep -i x-query-count   # still 2
```

Two queries at any row count is what `selectinload` buys you. Phase 1 puts the
endpoint that *doesn't* do that right next to it.

---

## 1 · The ORM failure families

*Guide: Day 2 — "The ORM: N+1 and materialization."*

_Not built yet._

## 2 · Validation boundary & mass assignment

*Guide: Day 2 — "Validation at the boundary"; Day 3 — mass assignment.*

_Not built yet._

## 3 · Broken object-level authorization

*Guide: Day 3 — "Broken object-level authorization."*

_Not built yet._

## 4 · Async correctness & the blocking event loop

*Guide: Day 2 — "Async, the event loop, and the GIL."*

_Not built yet._

## 5 · Transactions, idempotency & the outbox

*Guide: Day 2 — "Sessions / transaction boundaries", "Background jobs and idempotency."*

_Not built yet._

## 6 · Pagination & a lost-update race

*Guide: Day 2 — "Pagination"; Day 3 — "Concurrency, races, and consistency."*

_Not built yet._

## 7 · Auth hardening & JWT pitfalls

*Guide: Day 3 — "AuthN/AuthZ", "JWT pitfalls."*

_Not built yet._

## 8 · React failure modes

*Guide: Day 1 — high-priority sections.*

_Not built yet._

## 9 · Testing patterns

*Guide: Day 1 — "Testing React"; Day 2 — "Testing the backend."*

Partially built: the backend harness (real Postgres, per-test transaction,
`dependency_overrides`, `httpx.AsyncClient` + `ASGITransport`,
`assert_max_queries`) landed in Phase 0. Frontend testing and the `Makefile` come
in Phase 9 proper.

## 10 · Migration drill

*Guide: Day 2 — "Migrations and zero-downtime schema change."*

_Not built yet._

---

## 90-minute self-quiz

_Assembled in Phase 10, once every pair exists. The shape: for each pair, hit the
broken version, **write down your prediction of how it fails**, then read the
fix. The prediction is the part that does the teaching._

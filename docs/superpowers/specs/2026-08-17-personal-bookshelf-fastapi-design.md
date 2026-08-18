# App 2 — Personal Bookshelf, with a Python Backend — Design

Date: 2026-08-17
Status: Approved

## Purpose

Scaffold app 2 of the React practice curriculum, and change the backend stack from
Node + Express + TypeScript to Python + FastAPI.

The stack change carries a second, larger change: the division of labor. In app 1,
Claude built the entire API and the user built the entire frontend. From app 2 on,
the user implements most of the backend as well, so the repo doubles as Python
practice. Claude's remaining job on the backend is the tedium — project config, seed
data, test plumbing — plus one worked endpoint as a reference pattern.

The user knows Python the language; FastAPI, pydantic, and pytest are the new
territory. Scaffolding is calibrated to that: no explaining comprehensions, but the
framework idioms get shown once before being expected.

## Scope of the Stack Change

- **App 1 (National Parks Explorer) is not touched.** It is complete and stays
  Express. Rewriting a finished project to match a later convention churns working
  code for consistency's sake.
- **Apps 2 and 3 use FastAPI.** App 3's design in the curriculum spec keeps its
  endpoints and behavior; only the implementing stack changes.
- The curriculum spec (`2026-08-07-react-practice-curriculum-design.md`) gets an
  amendment noting the change, its date, and its reason, rather than being rewritten
  in place — the original records what was true when app 1 was built.

## Toolchain

- **Python:** 3.11+ (3.11.7 is on the machine).
- **Package manager:** `uv`, already installed. Manages the interpreter and venv;
  `pyproject.toml` + `uv.lock` are committed. No venv to activate by hand.
- **Framework:** FastAPI with `fastapi dev` for auto-reload — the analogue of app 1's
  `tsx watch`, no build step.
- **Testing:** `pytest` + `pytest-asyncio` with `httpx.AsyncClient` over an
  `ASGITransport`, driving the app in-process with no live server. This is the direct
  analogue of app 1's supertest setup. `asyncio_mode = "auto"` is set in
  `pyproject.toml`, so async tests need no per-test marker.
- **Storage:** an in-memory list, as with every app in the curriculum. No database.
- **Ports:** API on `4002` (the `400N` convention), web on Vite's `5173`. CORS is
  enabled for local dev, as in app 1.

Daily commands, for the app README:

```bash
cd api
uv sync
uv run fastapi dev app/main.py
uv run pytest
```

## Repo Layout

```
02-personal-bookshelf/
  api/
    pyproject.toml       fastapi, uvicorn, pytest,
                         pytest-asyncio, httpx                     [Claude]
    uv.lock                                                        [Claude]
    app/
      __init__.py
      main.py            FastAPI() + CORS + router registration    [Claude]
      data.py            15 seeded books + reset_books()           [Claude]
      models.py          Book, BookStatus [Claude]
                         BookCreate, BookUpdate [user]
      routes/
        __init__.py
        books.py         GET /api/books [Claude]
                         the other four endpoints [user]
    tests/
      conftest.py        client fixture + autouse store reset      [Claude]
      test_books.py      all five endpoints; 11 fail and 2 pass
                         at scaffold time                         [Claude]
  web/                   Vite + React + TS shell, react-router
                         installed, no routing code                [Claude]
  README.md              Part 1 (Python) + Part 2 (React)          [Claude]
```

Each app folder stays fully self-contained, per the curriculum spec — no shared
tooling, no monorepo wiring, and now no shared backend language either.

## Implementation Split

Claude scaffolds:

- All project config: `pyproject.toml`, `uv.lock`, package `__init__.py` files.
- `data.py` — 15 seeded books with varied statuses and ratings, plus `reset_books()`
  for test isolation. Inventing seed data is tedium, not practice.
- `main.py` — app construction, CORS middleware, router registration.
- `models.py` — `BookStatus` (a `str` enum) and `Book` (the response model). These
  two define the shape the frontend was specced against, so they are given rather
  than derived.
- `routes/books.py` — `GET /api/books` only, as the worked example: router setup,
  an `async def` handler, `response_model`, and reading from the data module. It
  demonstrates the wiring without giving away path params, request bodies, status
  codes, or error handling.
- The full test suite and its fixtures.

The user implements:

- `BookCreate` and `BookUpdate` in `models.py`.
- `GET /api/books/{id}`, `POST /api/books`, `PUT /api/books/{id}`, and
  `DELETE /api/books/{id}` in `routes/books.py`.
- The entire React frontend.

## API Contract

Book shape, unchanged from the curriculum spec:
`{ id, title, author, status, rating? }`, where `status` is one of
`"want"`, `"reading"`, `"read"`.

| Method | Path | Request body | Success | Unknown id |
|---|---|---|---|---|
| GET | `/api/books` | — | 200, `Book[]` | — |
| GET | `/api/books/{id}` | — | 200, `Book` | 404 |
| POST | `/api/books` | `BookCreate` | 201, `Book` | — |
| PUT | `/api/books/{id}` | `BookUpdate` | 200, `Book` | 404 |
| DELETE | `/api/books/{id}` | — | 204, empty body | 404 |

Field rules:

- `id` — a server-generated uuid4 hex string. Never accepted from the client; a
  client-supplied `id` in a POST or PUT body is ignored.
- `title`, `author` — required, non-empty strings (`min_length=1`).
- `status` — a `BookStatus` enum value, defaulting to `"want"` on create.
- `rating` — optional integer, `Field(ge=1, le=5)`. Absent means unrated.

Invalid request bodies return **422 automatically** from pydantic validation. The
user writes no manual validation code; the test suite pins this with a case
asserting an out-of-range rating is rejected.

### Decision: error envelope is `{"detail": "..."}`

App 1's Express API returned `{"error": "..."}`. FastAPI's `HTTPException` natively
emits `{"detail": "..."}`, and app 2 adopts that rather than reshaping responses for
cosmetic parity with an app whose stack it no longer shares. Consequence: app 2's
frontend reads `detail` where app 1's read `error`. This is intentional and is called
out in the app README so the difference reads as a decision, not an inconsistency.

### Decision: PUT is a partial update

`BookUpdate` declares every field optional, and only fields present in the request
body are applied; absent fields are left untouched. This departs from strict REST,
where PUT replaces a whole resource.

Two reasons, both pedagogical. It forces the user into `model_dump(exclude_unset=True)`
and the question of how pydantic distinguishes an absent field from one explicitly set
to null — a real pydantic idiom, where full-replacement is a dict overwrite that
teaches nothing. And it makes the frontend's inline status-change action a one-field
`PUT {"status": "read"}` rather than resending an entire book object.

### Decision: handlers are `async def`

Every route handler is `async def`, matching FastAPI's documentation convention and
what production services look like. Nothing in this app actually awaits — the store is
an in-memory list — so the `async` is, strictly speaking, unnecessary here.

It is in scope anyway. Learning FastAPI from docs written entirely in `async def`
while writing `def` is a friction tax on every page read, and the user already knows
async, so the concept costs nothing to carry. It also sets up the one lesson that does
bite in production: a blocking call inside an `async def` handler stalls the event
loop for every concurrent request, where FastAPI would have run a plain `def` handler
in a threadpool and been fine. The app README names this hazard explicitly, since an
app with nothing to await cannot demonstrate it.

## Testing

`tests/conftest.py` provides two fixtures: an `httpx.AsyncClient` bound to the app's
ASGI transport, and an autouse fixture restoring the seeded books before each test.
The reset matters because the store is mutable for the first time in this curriculum —
a `DELETE` test would otherwise poison whatever runs after it. Tests are `async def`
and await their requests, mirroring the handlers under test.

`tests/test_books.py` covers, in thirteen tests:

- `GET /api/books` returns the seeded list, and a companion test asserting the
  store is reset between tests. **These two are the only tests passing at scaffold
  time**; the suite ships at exactly 11 failed, 2 passed.
- `GET /api/books/{id}` for a known id, and 404 for an unknown one.
- `POST /api/books` returns 201 with a server-generated id, and the created book
  then appears in `GET /api/books`.
- `POST /api/books` with an out-of-range rating returns 422.
- `POST /api/books` without a status defaults it to `"want"`.
- `PUT /api/books/{id}` changing only `status` leaves other fields untouched, and
  404 for an unknown id.
- `DELETE /api/books/{id}` returns 204 and removes the book, and 404 for an
  unknown id.

The suite is the assignment's definition of done, not a sample to imitate. `uv run
pytest` going green is the gate between Part 1 and Part 2: at that point the API
provably satisfies the contract the frontend was specced against.

Frontend testing follows app 1's pattern — nothing pre-written, with the README
suggesting an RTL + Vitest test of the add-book form submission.

## Frontend Assignment

Unchanged from the curriculum spec; the backend switch does not touch it.

- Routes: `/` (list, filterable by status), `/books/new` (add form),
  `/books/:id/edit` (edit form, pre-filled).
- Inline delete and status-change actions from the list.
- A `ToastContext` via `useContext`, providing a global notification banner
  consumable from any page.
- Encouraged: a `useBooks()` custom hook sharing fetch/CRUD logic across pages.
- Stretch goals: optimistic delete (remove immediately, roll back on failure);
  sort by rating.

`react-router` ships in `package.json` with no routing code written — the dependency
is tedium, the routing is the lesson.

## README Structure

`02-personal-bookshelf/README.md` holds two assignments in sequence:

**Part 1 — Build the API.** The contract above, what is stubbed versus given, the
`uv` commands, `uv run pytest` as the gate, and a "Python concepts to practice"
list: pydantic models and validation, `str` enums, type hints on handlers,
`async def` handlers and when async actually buys anything, `HTTPException` and status
codes, `response_model`, and `model_dump(exclude_unset=True)`.

**Part 2 — Build the Frontend.** The React assignment above, in the shape app 1's
README used: goal, functional requirements, API contract reference, React concepts
to practice, stretch goals, suggested test.

Root `README.md` changes: app 2's row moves to "Ready to build", and the "Running an
app" section is rewritten — it currently assumes npm on both sides for every app,
which stops being true here.

## Out of Scope

- Porting app 1 to FastAPI.
- Databases or persistence beyond the in-memory list.
- Auth of any kind — that arrives in app 3, and is fake even there.
- Styling frameworks; plain CSS only, per the curriculum spec.
- Pre-written frontend implementations, and pre-written backend implementations
  beyond the one worked endpoint.

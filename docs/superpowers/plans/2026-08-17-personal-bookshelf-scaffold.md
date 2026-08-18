# Personal Bookshelf Scaffold — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold App 2 of the React practice curriculum — "Personal Bookshelf" — as a FastAPI backend that is deliberately half-built and a bare Vite + React + TypeScript frontend shell, so the user implements four of the five endpoints and the entire React app themselves.

**Architecture:** Two independent projects under `02-personal-bookshelf/`: `api/` (FastAPI, uv-managed, in-memory store, one worked endpoint plus a full pytest suite that ships red) and `web/` (Vite React-TS template trimmed to a placeholder, with `react-router` and the Vitest + RTL toolchain installed but no application code). No shared code, no database.

**Tech Stack:** Python 3.11+, FastAPI 0.141, pydantic 2.13, uv, pytest 9 + pytest-asyncio 1.4 + httpx 0.28, Vite, React 19, TypeScript, Vitest, React Testing Library, npm.

**Spec:** `docs/superpowers/specs/2026-08-17-personal-bookshelf-fastapi-design.md`

## Global Constraints

- **The API ships deliberately incomplete.** Only `GET /api/books` is implemented. `GET /api/books/{id}`, `POST`, `PUT`, and `DELETE` are the user's assignment and MUST NOT be implemented by the executor of this plan. Neither may `BookCreate` or `BookUpdate`.
- **The test suite ships red, and that is the deliverable.** After Task 4 the expected state is exactly `11 failed, 2 passed`. An executing agent's instinct will be to make the suite green — doing so destroys the assignment. Red is correct. Verify the count; do not fix the failures.
- **No pre-written frontend code.** `web/` ships as a placeholder page. All components, hooks, routing, and state are the user's work.
- Python 3.11+, managed by `uv`. `pyproject.toml` and `uv.lock` are committed; no `requirements.txt`, no hand-managed venv.
- All route handlers are `async def`, per the spec's async decision.
- Error responses use FastAPI's native `{"detail": "..."}` envelope, never app 1's `{"error": "..."}`.
- `PUT` is a partial update: only fields present in the request body are applied.
- `id` is server-generated and never accepted from a client body.
- In-memory storage only — no database, no persistence across restarts.
- API on port `4002`; web on Vite's `5173`; CORS enabled on the API.
- Plain CSS only on the frontend; plain `fetch()` for HTTP, no axios or query libraries.
- App 1 is not touched by this plan.

## File Structure

```
02-personal-bookshelf/
  api/
    pyproject.toml       deps + pytest config              Task 1
    uv.lock              resolved lockfile                 Task 1
    app/
      __init__.py                                          Task 1
      models.py          BookStatus, Book (+ user stubs)   Task 2
      data.py            15 seeded books, reset_books()    Task 2
      main.py            app, CORS, router registration    Task 3
      routes/
        __init__.py                                        Task 1
        books.py         GET /api/books only               Task 3
    tests/
      conftest.py        async client + store reset        Task 3
      test_books.py      2 green tests                     Task 3
                         + 11 red tests                    Task 4
  web/                   Vite shell, react-router, Vitest  Task 5
  README.md              Part 1 (Python) + Part 2 (React)  Task 6
```

Responsibilities split so each file has one job: `models.py` owns shape and validation, `data.py` owns the store and its reset, `routes/books.py` owns HTTP, `main.py` owns composition. The user's work lands inside two of these files rather than in new ones, so the split has to be clear before they start.

---

### Task 1: API project scaffold

**Files:**
- Create: `02-personal-bookshelf/api/pyproject.toml`
- Create: `02-personal-bookshelf/api/uv.lock` (generated)
- Create: `02-personal-bookshelf/api/app/__init__.py` (empty)
- Create: `02-personal-bookshelf/api/app/routes/__init__.py` (empty)

**Interfaces:**
- Produces: a `uv`-managed project where `uv run pytest` executes and `import app...` resolves from the project root. Tasks 2–4 depend on `asyncio_mode = "auto"` and `pythonpath = ["."]` being set here.

- [ ] **Step 1: Create the directory tree**

```bash
mkdir -p 02-personal-bookshelf/api/app/routes 02-personal-bookshelf/api/tests
touch 02-personal-bookshelf/api/app/__init__.py 02-personal-bookshelf/api/app/routes/__init__.py
```

- [ ] **Step 2: Write `02-personal-bookshelf/api/pyproject.toml`**

```toml
[project]
name = "api"
version = "0.1.0"
description = "Personal Bookshelf API"
requires-python = ">=3.11"
dependencies = [
    "fastapi[standard]>=0.141.1",
]

[dependency-groups]
dev = [
    "pytest>=9.1.1",
    "pytest-asyncio>=1.4.0",
    "httpx>=0.28.1",
]

[tool.pytest.ini_options]
# "auto" treats every `async def test_` as an asyncio test, so individual
# tests need no @pytest.mark.asyncio decorator.
asyncio_mode = "auto"
# Makes `app` importable from the tests without installing the project.
pythonpath = ["."]
```

- [ ] **Step 3: Resolve and install dependencies**

```bash
cd 02-personal-bookshelf/api && uv sync
```

- [ ] **Step 4: Verify the toolchain resolves**

Run: `cd 02-personal-bookshelf/api && uv run python -c "import fastapi, httpx, pytest; print(fastapi.__version__)"`
Expected: prints `0.141.1` or newer. A `ModuleNotFoundError` means `uv sync` did not run in the `api/` directory.

- [ ] **Step 5: Commit**

```bash
git add 02-personal-bookshelf/api/pyproject.toml 02-personal-bookshelf/api/uv.lock 02-personal-bookshelf/api/app
git commit -m "scaffold personal bookshelf api project"
```

---

### Task 2: Domain models and seed data

**Files:**
- Create: `02-personal-bookshelf/api/app/models.py`
- Create: `02-personal-bookshelf/api/app/data.py`

**Interfaces:**
- Consumes: the project layout from Task 1.
- Produces: `BookStatus` (str enum: `WANT`/`READING`/`READ` with values `"want"`/`"reading"`/`"read"`), `Book(id: str, title: str, author: str, status: BookStatus, rating: int | None)`, `SEED: list[Book]`, `BOOKS: list[Book]`, and `reset_books() -> None`. Task 3's routes and conftest import all of these.

- [ ] **Step 1: Write `app/models.py`**

Ships `BookStatus` and `Book` only. The trailing comment block marks where the user's two models go — leave it in place and do not implement them.

```python
from enum import Enum

from pydantic import BaseModel


class BookStatus(str, Enum):
    WANT = "want"
    READING = "reading"
    READ = "read"


class Book(BaseModel):
    """The shape every endpoint returns. The frontend is specced against this."""

    id: str
    title: str
    author: str
    status: BookStatus
    rating: int | None = None


# --- Your turn --------------------------------------------------------------
# Define BookCreate (the POST body) and BookUpdate (the PUT body) here.
# README.md Part 1 has the field rules; tests/test_books.py has the behavior
# they must satisfy. Both are pydantic models, like Book above.
```

- [ ] **Step 2: Write `app/data.py`**

```python
from app.models import Book, BookStatus

# Seed ids are readable slugs so they are pleasant to curl by hand. Books
# created through POST get a uuid4 hex instead - ids are opaque strings, so
# mixing the two formats is fine.
SEED: list[Book] = [
    Book(id="dune", title="Dune", author="Frank Herbert", status=BookStatus.READ, rating=5),
    Book(id="piranesi", title="Piranesi", author="Susanna Clarke", status=BookStatus.READING),
    Book(id="station-eleven", title="Station Eleven", author="Emily St. John Mandel", status=BookStatus.READ, rating=4),
    Book(id="left-hand-of-darkness", title="The Left Hand of Darkness", author="Ursula K. Le Guin", status=BookStatus.READ, rating=5),
    Book(id="project-hail-mary", title="Project Hail Mary", author="Andy Weir", status=BookStatus.WANT),
    Book(id="klara-and-the-sun", title="Klara and the Sun", author="Kazuo Ishiguro", status=BookStatus.READ, rating=3),
    Book(id="the-overstory", title="The Overstory", author="Richard Powers", status=BookStatus.READING),
    Book(id="solaris", title="Solaris", author="Stanislaw Lem", status=BookStatus.WANT),
    Book(id="a-memory-called-empire", title="A Memory Called Empire", author="Arkady Martine", status=BookStatus.READ, rating=4),
    Book(id="the-dispossessed", title="The Dispossessed", author="Ursula K. Le Guin", status=BookStatus.WANT),
    Book(id="never-let-me-go", title="Never Let Me Go", author="Kazuo Ishiguro", status=BookStatus.READ, rating=4),
    Book(id="annihilation", title="Annihilation", author="Jeff VanderMeer", status=BookStatus.READ, rating=3),
    Book(id="three-body-problem", title="The Three-Body Problem", author="Liu Cixin", status=BookStatus.READING),
    Book(id="exhalation", title="Exhalation", author="Ted Chiang", status=BookStatus.READ, rating=5),
    Book(id="sea-of-tranquility", title="Sea of Tranquility", author="Emily St. John Mandel", status=BookStatus.WANT),
]

# The live store. Mutable - POST/PUT/DELETE change it, and it resets on restart.
BOOKS: list[Book] = []


def reset_books() -> None:
    """Restore BOOKS to the seeded set. Called on import and before each test."""
    BOOKS.clear()
    BOOKS.extend(book.model_copy(deep=True) for book in SEED)


reset_books()
```

- [ ] **Step 3: Verify the store loads**

Run: `cd 02-personal-bookshelf/api && uv run python -c "from app.data import BOOKS; print(len(BOOKS), BOOKS[0].title)"`
Expected: `15 Dune`

- [ ] **Step 4: Verify the reset restores mutations**

Run: `cd 02-personal-bookshelf/api && uv run python -c "from app.data import BOOKS, reset_books; BOOKS.clear(); reset_books(); print(len(BOOKS))"`
Expected: `15`

- [ ] **Step 5: Commit**

```bash
git add 02-personal-bookshelf/api/app/models.py 02-personal-bookshelf/api/app/data.py
git commit -m "add book model and seed data"
```

---

### Task 3: App wiring, worked endpoint, and test harness

**Files:**
- Create: `02-personal-bookshelf/api/app/main.py`
- Create: `02-personal-bookshelf/api/app/routes/books.py`
- Create: `02-personal-bookshelf/api/tests/conftest.py`
- Create: `02-personal-bookshelf/api/tests/test_books.py`

**Interfaces:**
- Consumes: `Book`, `BookStatus` from `app.models`; `BOOKS`, `reset_books` from `app.data`.
- Produces: `app` (the `FastAPI` instance) importable from `app.main`; `router` from `app.routes.books`, mounted at prefix `/api/books`; a `client` fixture yielding an `httpx.AsyncClient` and an autouse `fresh_books` fixture. Task 4 appends to `tests/test_books.py` and relies on the `client` fixture.

This task is normal TDD: the two tests written here are expected to go green.

- [ ] **Step 1: Write `tests/conftest.py`**

```python
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.data import reset_books
from app.main import app


@pytest.fixture(autouse=True)
def fresh_books() -> None:
    reset_books()


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
```

- [ ] **Step 2: Write `tests/test_books.py` with the two tests the scaffold satisfies**

```python
from httpx import AsyncClient

from app.data import SEED


async def test_list_books_returns_seeded_books(client: AsyncClient) -> None:
    res = await client.get("/api/books")
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body, list)
    assert len(body) == len(SEED)
    assert set(body[0]) == {"id", "title", "author", "status", "rating"}


async def test_store_is_reset_between_tests(client: AsyncClient) -> None:
    body = (await client.get("/api/books")).json()
    assert len(body) == len(SEED)
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `cd 02-personal-bookshelf/api && uv run pytest -q`
Expected: FAIL during collection — `ModuleNotFoundError: No module named 'app.main'`. Nothing has been wired yet.

- [ ] **Step 4: Write `app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.books import router as books_router

app = FastAPI(title="Personal Bookshelf API")

# The frontend runs on http://localhost:5173, a different origin, so the
# browser needs CORS headers to let it call this API. Wide open is fine for
# local practice; a real service would name its allowed origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books_router, prefix="/api/books")
```

- [ ] **Step 5: Write `app/routes/books.py` — the worked example**

Only `list_books`. The trailing comment block is the user's assignment marker; leave it and implement nothing below it.

```python
from fastapi import APIRouter

from app.data import BOOKS
from app.models import Book

router = APIRouter()


@router.get("", response_model=list[Book])
async def list_books() -> list[Book]:
    """Return every book in the store.

    The worked example. Note the three pieces you will reuse below: the
    decorator naming the method and path (relative to the /api/books prefix
    set in main.py), `response_model` telling FastAPI the shape to serialize
    and document, and `async def`.
    """
    return BOOKS


# --- Your turn --------------------------------------------------------------
# Implement the other four endpoints:
#
#   GET    /{book_id}   -> 200 Book, or 404
#   POST   ""           -> 201 Book, id generated server-side
#   PUT    /{book_id}   -> 200 Book, applying only the fields that were sent
#   DELETE /{book_id}   -> 204 with an empty body, or 404
#
# README.md Part 1 has the full contract. tests/test_books.py is the spec -
# run `uv run pytest` and work until it is green.
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `cd 02-personal-bookshelf/api && uv run pytest -q`
Expected: `2 passed`

- [ ] **Step 7: Smoke-test the running server**

```bash
cd 02-personal-bookshelf/api
uv run fastapi dev app/main.py --port 4002 &
sleep 4
curl -s http://localhost:4002/api/books | head -c 120
kill %1
```

Expected: a JSON array beginning with Dune's record. If the port is in use, nothing else in this curriculum should be on 4002 — check for a stray process rather than changing the port.

- [ ] **Step 8: Commit**

```bash
git add 02-personal-bookshelf/api/app 02-personal-bookshelf/api/tests
git commit -m "add app wiring, worked list endpoint, and test harness"
```

---

### Task 4: The assignment test suite (ships red)

**Files:**
- Modify: `02-personal-bookshelf/api/tests/test_books.py` (append)

**Interfaces:**
- Consumes: the `client` and `fresh_books` fixtures from Task 3.
- Produces: the user-facing definition of done for Part 1 of the assignment.

> **Do not make these tests pass.** They describe the four endpoints the user
> implements. Appending them and confirming they fail *is* the deliverable. If
> the suite ends this task green, the assignment has been destroyed and the
> endpoint implementations must be reverted.

- [ ] **Step 1: Append the eleven failing tests to `tests/test_books.py`**

Append below the two tests from Task 3, keeping the existing `from httpx import AsyncClient` import at the top of the file.

```python
async def test_get_book_returns_one_book(client: AsyncClient) -> None:
    listed = (await client.get("/api/books")).json()[0]
    res = await client.get(f"/api/books/{listed['id']}")
    assert res.status_code == 200
    assert res.json() == listed


async def test_get_book_unknown_id_returns_404(client: AsyncClient) -> None:
    res = await client.get("/api/books/nope")
    assert res.status_code == 404
    assert res.json() == {"detail": "Book not found"}


async def test_create_book_returns_201_with_generated_id(client: AsyncClient) -> None:
    res = await client.post("/api/books", json={"title": "Piranesi", "author": "Susanna Clarke", "status": "reading"})
    assert res.status_code == 201
    body = res.json()
    assert body["id"]
    assert body["title"] == "Piranesi"
    assert body["status"] == "reading"


async def test_created_book_appears_in_list(client: AsyncClient) -> None:
    before = len((await client.get("/api/books")).json())
    created = (await client.post("/api/books", json={"title": "Solaris", "author": "Stanislaw Lem"})).json()
    after = (await client.get("/api/books")).json()
    assert len(after) == before + 1
    assert any(b["id"] == created["id"] for b in after)


async def test_create_book_defaults_status_to_want(client: AsyncClient) -> None:
    res = await client.post("/api/books", json={"title": "Solaris", "author": "Stanislaw Lem"})
    assert res.status_code == 201
    assert res.json()["status"] == "want"


async def test_create_book_rejects_out_of_range_rating(client: AsyncClient) -> None:
    res = await client.post("/api/books", json={"title": "Solaris", "author": "Stanislaw Lem", "rating": 9})
    assert res.status_code == 422


async def test_create_book_ignores_client_supplied_id(client: AsyncClient) -> None:
    res = await client.post("/api/books", json={"id": "hacked", "title": "Solaris", "author": "Stanislaw Lem"})
    assert res.status_code == 201
    assert res.json()["id"] != "hacked"


async def test_update_book_changes_only_provided_fields(client: AsyncClient) -> None:
    original = (await client.get("/api/books")).json()[0]
    res = await client.put(f"/api/books/{original['id']}", json={"status": "read"})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "read"
    assert body["title"] == original["title"]
    assert body["author"] == original["author"]
    assert body["rating"] == original["rating"]


async def test_update_book_unknown_id_returns_404(client: AsyncClient) -> None:
    res = await client.put("/api/books/nope", json={"status": "read"})
    assert res.status_code == 404
    assert res.json() == {"detail": "Book not found"}


async def test_delete_book_returns_204_and_removes_it(client: AsyncClient) -> None:
    target = (await client.get("/api/books")).json()[0]
    res = await client.delete(f"/api/books/{target['id']}")
    assert res.status_code == 204
    assert res.content == b""
    remaining = (await client.get("/api/books")).json()
    assert all(b["id"] != target["id"] for b in remaining)


async def test_delete_book_unknown_id_returns_404(client: AsyncClient) -> None:
    res = await client.delete("/api/books/nope")
    assert res.status_code == 404
    assert res.json() == {"detail": "Book not found"}
```

- [ ] **Step 2: Run the suite and verify the exact red state**

Run: `cd 02-personal-bookshelf/api && uv run pytest -q 2>&1 | tail -3`
Expected: `11 failed, 2 passed`.

The two passing tests are `test_list_books_returns_seeded_books` and `test_store_is_reset_between_tests` — both exercise only the worked endpoint. Every other test fails because its endpoint does not exist yet: `POST`/`PUT`/`DELETE` return 405, and `GET /api/books/{id}` returns FastAPI's default `{"detail": "Not Found"}` rather than the contract's `{"detail": "Book not found"}`.

A count other than `11 failed, 2 passed` means something is wrong: fewer failures suggests an endpoint was implemented; a collection error suggests the append broke the file's imports.

- [ ] **Step 3: Commit**

```bash
git add 02-personal-bookshelf/api/tests/test_books.py
git commit -m "add failing test suite defining the api assignment"
```

---

### Task 5: Frontend shell

**Files:**
- Create: `02-personal-bookshelf/web/` (Vite React-TS project)
- Modify: `02-personal-bookshelf/web/package.json`
- Modify: `02-personal-bookshelf/web/vite.config.ts`
- Create: `02-personal-bookshelf/web/src/setupTests.ts`
- Modify: `02-personal-bookshelf/web/src/App.tsx`
- Modify: `02-personal-bookshelf/web/src/index.css`

**Interfaces:**
- Produces: a runnable `npm run dev` shell on port 5173 with `react-router` installed and `npm test` wired to Vitest + React Testing Library. No application code — the user writes every component.

Note: app 1's `web/` shipped without test tooling and the user added it by hand. App 2 ships it configured, per the curriculum spec's intent that `npm test` work out of the box.

- [ ] **Step 1: Create the Vite project**

```bash
cd 02-personal-bookshelf
npm create vite@latest web -- --template react-ts
cd web && npm install
```

- [ ] **Step 2: Install `react-router` and the test toolchain**

```bash
cd 02-personal-bookshelf/web
npm install react-router
npm install -D vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

- [ ] **Step 3: Add the `test` script to `package.json`**

Add one entry to the existing `"scripts"` object, leaving the rest untouched:

```json
"test": "vitest run"
```

- [ ] **Step 4: Replace `vite.config.ts` with a Vitest-aware config**

```ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
    passWithNoTests: true,
  },
})
```

`passWithNoTests` matters: the project ships with zero tests, and `npm test` should report success rather than erroring on an empty suite.

- [ ] **Step 5: Create `src/setupTests.ts`**

```ts
import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

afterEach(() => {
  cleanup();
});
```

- [ ] **Step 6: Replace `src/App.tsx` with a placeholder**

```tsx
function App() {
  return (
    <main>
      <h1>Personal Bookshelf</h1>
      <p>Your app goes here. See README.md, Part 2.</p>
    </main>
  );
}

export default App;
```

- [ ] **Step 7: Empty `src/index.css` and delete the template leftovers**

```bash
cd 02-personal-bookshelf/web
: > src/index.css
rm -f src/App.css src/assets/react.svg public/vite.svg
```

The Vite template's default styling would fight whatever CSS the user writes, so it goes.

- [ ] **Step 8: Verify the build, the test runner, and the dev server**

```bash
cd 02-personal-bookshelf/web
npm run build
npm test
```

Expected: the build succeeds, and `npm test` reports no tests without failing. If the build errors on a missing `./App.css` import, Step 7 removed the file but `App.tsx` still references it — Step 6's replacement drops that import.

- [ ] **Step 9: Commit**

```bash
git add 02-personal-bookshelf/web
git commit -m "scaffold personal bookshelf frontend shell"
```

---

### Task 6: The assignment README

**Files:**
- Create: `02-personal-bookshelf/README.md`

**Interfaces:**
- Consumes: the contract implemented across Tasks 1–4.
- Produces: the user-facing assignment. Task 7 links to it from the root README.

- [ ] **Step 1: Write `02-personal-bookshelf/README.md`**

Write the file with exactly this content:

````markdown
# Personal Bookshelf

App 2 of the curriculum, and the first with a Python backend. It comes in two
parts: build the API, then build the React app that consumes it.

Part 1 is deliberately half-built. `GET /api/books` is implemented as a worked
example; the other four endpoints are yours. `uv run pytest` is your spec — it
ships with 11 failing tests, and green means your API satisfies the contract
Part 2 was written against.

## Running it

```bash
# terminal 1
cd api
uv sync
uv run fastapi dev app/main.py --port 4002   # http://localhost:4002

# terminal 2
cd web
npm install
npm run dev                                   # http://localhost:5173
```

`uv sync` creates the virtualenv and installs everything on first run; there is
no venv to activate. FastAPI serves interactive docs at
<http://localhost:4002/docs> — useful for poking at endpoints before the
frontend exists.

---

# Part 1 — Build the API

## What is already there

- `app/models.py` — `BookStatus` and `Book`, the response shape.
- `app/data.py` — 15 seeded books, the mutable `BOOKS` store, and `reset_books()`.
- `app/main.py` — the app, CORS, and router registration.
- `app/routes/books.py` — `GET /api/books`, the worked example.
- `tests/` — the full suite and its fixtures.

## What you implement

In `app/models.py`: `BookCreate` and `BookUpdate`.
In `app/routes/books.py`: the four remaining endpoints.

## The contract

Book shape: `{ id, title, author, status, rating? }` where `status` is one of
`"want"`, `"reading"`, `"read"`.

| Method | Path | Body | Success | Unknown id |
|---|---|---|---|---|
| GET | `/api/books` | — | 200, `Book[]` | — |
| GET | `/api/books/{id}` | — | 200, `Book` | 404 |
| POST | `/api/books` | `BookCreate` | 201, `Book` | — |
| PUT | `/api/books/{id}` | `BookUpdate` | 200, `Book` | 404 |
| DELETE | `/api/books/{id}` | — | 204, empty body | 404 |

Field rules:

- `id` — generated server-side with `uuid4().hex`. Never taken from the request
  body; a client that sends one is ignored.
- `title`, `author` — required, non-empty (`min_length=1`).
- `status` — defaults to `"want"` when a POST omits it.
- `rating` — optional, an integer from 1 to 5 (`Field(ge=1, le=5)`).

Errors use FastAPI's native envelope, `{"detail": "..."}`. A missing book is
`{"detail": "Book not found"}` with status 404 — raise `HTTPException` and
FastAPI shapes the response for you. (App 1 returned `{"error": ...}`; this is
a deliberate change, since `detail` is what the framework emits natively.)

**PUT is a partial update.** Only the fields present in the request body change;
everything else is left alone. `PUT {"status": "read"}` changes the status and
nothing else. This is what makes the frontend's inline status toggle a one-field
request, and it is the interesting half of the exercise — look up
`model_dump(exclude_unset=True)` and think about how pydantic tells "field
absent" apart from "field explicitly null".

Validation is not your job to write. Declare the rules on the model and pydantic
returns 422 on violations by itself.

## Working the assignment

```bash
cd api
uv run pytest          # 11 failing, 2 passing on day one
uv run pytest -x       # stop at the first failure while you work
uv run pytest -k post  # just the POST tests
```

Take the endpoints in the order the tests list them. `list_books` in
`routes/books.py` is the pattern for the decorator, `response_model`, and the
`async def` signature.

## Python concepts to practice

- **pydantic models** — declaring shape and validation as types, and how
  `BookCreate` (what a client may send) differs from `Book` (what you return).
- **`Field` constraints** — `min_length`, `ge`, `le`, and the automatic 422.
- **`str` enums** — `BookStatus` as both a Python enum and a JSON string.
- **`HTTPException`** and explicit status codes (`201`, `204`).
- **`response_model`** — how FastAPI serializes and documents the return shape.
- **`model_dump(exclude_unset=True)`** — the crux of the partial update.
- **`async def` handlers** — every handler here is async, matching FastAPI's
  docs and production services. Nothing in this app actually awaits, so the
  async buys you nothing *here*. It is worth internalizing anyway, along with
  the hazard it comes with: a blocking call (a `requests.get`, a `time.sleep`,
  a synchronous DB driver) inside an `async def` handler stalls the event loop
  for every concurrent request, where FastAPI would have run a plain `def`
  handler in a threadpool and been fine.

---

# Part 2 — Build the Frontend

Start once `uv run pytest` is green. The API then provably matches what this
half was specced against.

## Functional requirements

- **Routes**, via `react-router` (already installed, no routing code written):
  - `/` — the book list, filterable by status.
  - `/books/new` — a form to add a book.
  - `/books/:id/edit` — an edit form, pre-filled from the existing book.
- Inline **delete** and **status-change** actions on each list row. The status
  change is a one-field `PUT`, per the contract above.
- A **`ToastContext`** via `useContext`, providing a notification banner any
  page can trigger — "Book added", "Book deleted". This is the point of the
  exercise: state that several unrelated pages reach without prop-drilling.
- Encouraged: extract a **`useBooks()` custom hook** so the fetch and CRUD logic
  is written once rather than in each page.

Fetch the full URL — `fetch('http://localhost:4002/api/books')` — since the
frontend runs on a different origin. Plain `fetch`, no axios or query library.

## React concepts to practice

- React Router: routes, links, `useParams`, and programmatic navigation after a
  successful write.
- Controlled form inputs, and the pre-filled edit form as a two-step problem —
  fetch the book, then seed form state from it.
- `useContext` for cross-page state, and why the toast is a better fit for it
  than the book list is.
- Custom hooks as the way to share stateful logic between components.
- Loading and error states on writes, not just reads — a failed `POST` needs to
  say so.

## Stretch goals

- **Optimistic delete** — remove the row immediately, restore it if the request
  fails.
- **Sort by rating**, with unrated books handled deliberately rather than
  accidentally.

## Suggested test

`npm test` is wired to Vitest + React Testing Library with no tests written.
Try one covering the add-book form: render it, type a title and author, submit,
and assert the expected `POST` fired with the right body. Mock `fetch` rather
than hitting the real API.
````

- [ ] **Step 2: Verify the README's commands are real**

Run: `cd 02-personal-bookshelf/api && uv run pytest -q 2>&1 | tail -1`
Expected: `11 failed, 2 passed` — matching the count the README promises on day one.

- [ ] **Step 3: Commit**

```bash
git add 02-personal-bookshelf/README.md
git commit -m "add personal bookshelf assignment readme"
```

---

### Task 7: Root README and curriculum spec amendment

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-08-07-react-practice-curriculum-design.md`

**Interfaces:**
- Consumes: the finished app 2 scaffold.
- Produces: an accurate repo index. Nothing depends on this task.

- [ ] **Step 1: Update app 2's row in the root README table**

Change the app 2 row to link the folder and read "Ready to build":

```markdown
| 2 | [Personal Bookshelf](02-personal-bookshelf/) | React Router, forms, CRUD, `useContext` | Ready to build |
```

- [ ] **Step 2: Replace the root README's "Running an app" section**

It currently claims npm on both sides of every app, which stopped being true with app 2. Replace the whole section with:

````markdown
## Running an app

Each app has an independent API and frontend, run in separate terminals from
the app's folder. App 1's API is Node + Express; app 2 onward is Python +
FastAPI, so check the app's own README for its commands.

```bash
# app 1 — Express API
cd 01-national-parks-explorer/api && npm install && npm run dev

# app 2 onward — FastAPI
cd 02-personal-bookshelf/api && uv sync && uv run fastapi dev app/main.py --port 4002

# the frontend, in every app
cd <app>/web && npm install && npm run dev
```

Each app's own `README.md` has the assignment: what to build, the API contract,
and which concepts it exercises. From app 2 on, the backend is part of the
assignment too.
````

- [ ] **Step 3: Append the stack-change amendment to the curriculum spec**

Add at the end of `docs/superpowers/specs/2026-08-07-react-practice-curriculum-design.md`:

```markdown
## Amendment — 2026-08-17: backend stack change

As of App 2, the backend stack is Python + FastAPI rather than Node + Express +
TypeScript, and the division of labor changes with it: the user implements most
of the backend, not just the frontend. The motivation is practicing Python
alongside React. App 1 is unchanged and stays on Express — rewriting a finished
app to match a later convention churns working code for consistency's sake.

The "Tooling" and "App 2"/"App 3" sections above describe the original Express
plan and are superseded for those apps by
`2026-08-17-personal-bookshelf-fastapi-design.md`. Everything else — the
curriculum framing, the concept progression, in-memory storage, plain CSS,
plain `fetch()`, per-app independence — is unaffected.
```

- [ ] **Step 4: Verify the root README's links resolve**

Run: `ls 02-personal-bookshelf/README.md && grep -n "02-personal-bookshelf" README.md`
Expected: the file exists and the table row links to it.

- [ ] **Step 5: Commit**

```bash
git add README.md docs/superpowers/specs/2026-08-07-react-practice-curriculum-design.md
git commit -m "index app 2 and amend curriculum spec for the stack change"
```

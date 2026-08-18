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
absent" apart from "field explicitly null". Concretely: a field you omit keeps
its current value, and a field you send as null is cleared — which is exactly
the distinction `exclude_unset` preserves and `exclude_none` throws away.

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

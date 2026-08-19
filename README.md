# Project Practice

A collection of small, self-contained full-stack apps for practicing React and backend API development. App 1 ships with a pre-built Express API so the focus stays purely on the frontend. From app 2 on, the backend is Python + FastAPI and building it is part of the assignment, not just the React app on top of it.

See [`docs/superpowers/specs/2026-08-07-react-practice-curriculum-design.md`](docs/superpowers/specs/2026-08-07-react-practice-curriculum-design.md) for the full curriculum design, and its [2026-08-17 amendment](docs/superpowers/specs/2026-08-07-react-practice-curriculum-design.md#amendment--2026-08-17-backend-stack-change) for why the stack changed.

## Apps

| # | App | Backend | Focus | Status |
|---|-----|---------|-------|--------|
| 1 | [National Parks Explorer](01-national-parks-explorer/) | Express (built for you) | `useState`, `useEffect`, fetching, list rendering | Complete |
| 2 | [Personal Bookshelf](02-personal-bookshelf/) | FastAPI (you build it) | pydantic models, CRUD, React Router, forms, `useContext` | Ready to build |
| 3 | Team Kanban Board | FastAPI (you build it) | `useReducer`, `useMemo`/`useCallback`, auth patterns | Planned |

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

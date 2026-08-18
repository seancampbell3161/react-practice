# React Practice

A collection of small, self-contained full-stack apps for practicing React. Each app has an Express + TypeScript API already built and a bare Vite + React + TypeScript frontend shell — you build the actual React app on top of it.

See [`docs/superpowers/specs/2026-08-07-react-practice-curriculum-design.md`](docs/superpowers/specs/2026-08-07-react-practice-curriculum-design.md) for the full curriculum design.

## Apps

| # | App | Focus | Status |
|---|-----|-------|--------|
| 1 | [National Parks Explorer](01-national-parks-explorer/) | `useState`, `useEffect`, fetching, list rendering | Complete |
| 2 | [Personal Bookshelf](02-personal-bookshelf/) | React Router, forms, CRUD, `useContext` | Ready to build |
| 3 | Team Kanban Board | `useReducer`, `useMemo`/`useCallback`, auth patterns | Planned |

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

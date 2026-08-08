# React Practice

A collection of small, self-contained full-stack apps for practicing React. Each app has an Express + TypeScript API already built and a bare Vite + React + TypeScript frontend shell — you build the actual React app on top of it.

See [`docs/superpowers/specs/2026-08-07-react-practice-curriculum-design.md`](docs/superpowers/specs/2026-08-07-react-practice-curriculum-design.md) for the full curriculum design.

## Apps

| # | App | Focus | Status |
|---|-----|-------|--------|
| 1 | [National Parks Explorer](01-national-parks-explorer/) | `useState`, `useEffect`, fetching, list rendering | Ready to build |
| 2 | Personal Bookshelf | React Router, forms, CRUD, `useContext` | Planned |
| 3 | Team Kanban Board | `useReducer`, `useMemo`/`useCallback`, auth patterns | Planned |

## Running an app

Each app has an independent API and frontend. From the app's folder, run both in separate terminals:

```bash
cd 01-national-parks-explorer/api
npm install
npm run dev   # starts the API

cd 01-national-parks-explorer/web
npm install
npm run dev   # starts the frontend
```

Each app's own `README.md` has the assignment: what to build, the API contract, and which React concepts it's meant to exercise.

# React Practice Curriculum — Design

Date: 2026-08-07
Status: Approved

## Purpose

This repo is a personal React learning environment. It hosts a series of small, independent full-stack apps of increasing complexity. For each app, Claude scaffolds a working backend API and a bare (unstyled, unbuilt) frontend project shell, plus a README describing what to build. The user — a React beginner — writes all the actual React code (components, hooks, state, data fetching) themselves, using the README as a spec/assignment.

Claude's job per app is scaffolding + spec, never the feature implementation.

## Repo Structure

```
react-practice/
  01-national-parks-explorer/
    api/
      src/
        server.ts
        routes/
        data.ts
      package.json
      tsconfig.json
    web/
      src/
        App.tsx
        main.tsx
      package.json
      tsconfig.json
      index.html
    README.md
  02-personal-bookshelf/
    api/ ...
    web/ ...
    README.md
  03-team-kanban-board/
    api/ ...
    web/ ...
    README.md
  README.md
  docs/superpowers/specs/
    2026-08-07-react-practice-curriculum-design.md
```

- Each numbered app folder is **fully self-contained**: its own `api/` and `web/` projects, own `package.json`, own `node_modules`, own git history (as commits, not submodules). Nothing is shared between apps — no monorepo tooling, no shared component library. This keeps each app a clean, isolated sandbox and avoids adding workspace-tooling concepts on top of React itself.
- The root `README.md` is an index: how to run any given app (`cd 0N-app/api && npm install && npm run dev`, `cd 0N-app/web && npm install && npm run dev`, in two terminals), and a one-paragraph summary of the curriculum/progression.
- Each app's own `README.md` is the "assignment": goals, functional requirements, the API contract, a list of React concepts/hooks it's meant to exercise, and optional stretch goals. It does not contain solution code.

## Tooling (same across all apps)

- **Frontend:** Vite + React + TypeScript (the `react-ts` template), trimmed to a blank placeholder page. Plain CSS for styling — no Tailwind/CSS-in-JS, to keep focus on React/JS rather than a styling system.
- **Backend:** Node + Express + TypeScript, run via `tsx watch src/server.ts` (no build step, auto-restart on save). Data is stored in an in-memory array per app (no database) — keeps focus on the frontend/client-server boundary rather than persistence.
- **HTTP calls:** plain `fetch()`, no axios or query library — one less concept for a beginner, and it's the primitive every other approach builds on.
- **Package manager:** npm (ships with Node, no global install needed, simplest default for independent per-app folders).
- **Testing:** Vitest on both sides — React Testing Library on the frontend, supertest on the backend. Each app ships with `npm test` working out of the box in both `api/` and `web/`, and **one worked example test already written** as a pattern to learn from (see per-app sections below). Tests for the actual UI/features the user builds are part of the practice, not pre-written; each README suggests a concrete test worth attempting.
- **Version control:** the repo is git-initialized by Claude. Each app's scaffold is committed separately so there's a clean history to look back on.
- **Dev ports & CORS:** each app's `api/` runs on a fixed port (`400N`, e.g. app 1 → `4001`, app 2 → `4002`, app 3 → `4003`) and each `web/` runs on Vite's default (`5173`). Since frontend and backend run on different origins, the Express app enables `cors()` for local dev. Fixed ports (rather than the default Express `3000`) avoid collisions if two apps' backends happen to run at once.

## Curriculum Framing

Three apps, each a small but real feature domain, sequenced so that each app's *theme* naturally requires the next tier of React concepts — concepts are motivated by what the app needs, not bolted on arbitrarily.

| # | App | New concepts introduced |
|---|-----|--------------------------|
| 1 | National Parks Explorer | `useState`, `useEffect` + dependency arrays, fetch + loading/error/empty states, rendering lists (`.map`/`key`), event handlers, props parent→child |
| 2 | Personal Bookshelf | React Router (multi-page), controlled form inputs, full CRUD (`POST`/`PUT`/`DELETE`), `useContext` (global toast), custom hooks |
| 3 | Team Kanban Board | `useReducer`, `useMemo`/`useCallback` + `React.memo`, fake auth + protected routes + `localStorage`, multiple composed custom hooks |

Each app builds on skills from the previous one (fetching, then CRUD, then complex state) rather than repeating them from scratch.

## App 1 — National Parks Explorer (Beginner)

**Concepts:** `useState`, `useEffect`, fetching data, loading/error/empty states, list rendering, event handlers, props.

**Why this theme:** a list-of-things-with-details UI is the simplest realistic shape, and national parks provide naturally varied, interesting data without needing images, auth, or writes.

**API** (read-only):
- `GET /api/parks` → `{ id, name, state, tagline }[]`
- `GET /api/parks/:id` → `{ id, name, state, tagline, description, established, sizeAcres, activities: string[] }`
- In-memory array of ~10-12 seeded national parks.

**Frontend requirements:**
- Fetch and display the park list on load, with a loading indicator and an error message on failure.
- Clicking a park fetches and displays its detail (separate `useEffect` keyed on a `selectedId` state value), with its own independent loading state.
- At least two components (e.g. `ParkList`, `ParkDetail`) to practice props/handoff.

**Stretch goals:** client-side text filter over the visible list (controlled input); a "favorite" star toggle in local state.

**Testing:** worked example — supertest test for `GET /api/parks`. Suggested practice test: RTL test of the loading→loaded transition.

## App 2 — Personal Bookshelf (Intermediate)

**Concepts:** React Router, controlled forms, full CRUD, `useContext`, custom hooks, richer `useEffect` dependencies.

**Why this theme:** tracking books owned/reading/read naturally requires create, edit, delete, and status changes — the smallest domain that justifies real CRUD and multiple pages.

**API:**
- `GET /api/books`, `GET /api/books/:id`, `POST /api/books`, `PUT /api/books/:id`, `DELETE /api/books/:id`
- Book shape: `{ id, title, author, status: "want" | "reading" | "read", rating?: number }`
- In-memory storage.

**Frontend requirements:**
- Routes: `/` (list, filterable by status), `/books/new` (add form), `/books/:id/edit` (edit form, pre-filled).
- Inline delete and status-change actions from the list.
- A `ToastContext` (via `useContext`) providing a global notification banner ("Book added!"/"Book deleted") consumable from any page.
- Encouraged: extract a `useBooks()` custom hook to share fetch/CRUD logic across pages.

**Stretch goals:** optimistic delete (remove from list immediately, roll back on failure); sort by rating.

**Testing:** worked example — supertest test covering `POST /api/books` validation. Suggested practice test: RTL test of the add-book form submission.

## App 3 — Team Kanban Board (Advanced)

**Concepts:** `useReducer`, `useMemo`/`useCallback`, `React.memo`, fake auth + protected routes + `localStorage`, composed custom hooks, search/filter over larger data.

**Why this theme:** moving tasks between columns fits reducer-style state transitions naturally, and a login gate is the smallest realistic way to practice protected routes. Auth is intentionally **fake** — this is a practice app, not production: any non-empty username/password succeeds and a token is stored in `localStorage`. No password hashing, sessions, or real security is in scope.

**API:**
- `POST /api/login` → accepts any non-empty `{ username, password }`, returns a fake token.
- `GET /api/tasks`, `POST /api/tasks`, `PUT /api/tasks/:id` (edits and column moves), `DELETE /api/tasks/:id`.
- Task shape: `{ id, title, description, assignee, status: "todo" | "in-progress" | "done" }`.
- All endpoints except `/login` require an `Authorization` header; respond 401 if missing/invalid.

**Frontend requirements:**
- `/login` page; a `ProtectedRoute` wrapper redirects there if no token is in `localStorage`.
- Board page with three columns; tasks grouped via `useMemo` from a flat array.
- Board state managed with `useReducer` (actions: add/move/delete).
- `TaskCard` wrapped in `React.memo`, with `useCallback` for handlers passed into it.
- Search input filtering visible tasks by title/assignee.
- Custom hooks: `useAuth()` (login state + localStorage sync), `useTasks()` (reducer + API sync).

**Stretch goals:** drag-and-drop instead of move buttons; task priority + sorting.

**Testing:** worked example — a reducer unit test (pure function, easiest to isolate). Suggested practice test: RTL test of the protected-route redirect behavior.

## Out of Scope

- Databases / persistence beyond in-memory arrays.
- Real authentication/security (password hashing, sessions, HTTPS concerns) — App 3's auth is explicitly fake and for UX-pattern practice only.
- Shared/monorepo tooling (workspaces, shared component libraries) — each app stays fully independent.
- Styling frameworks (Tailwind, CSS-in-JS) — plain CSS only.
- Pre-written feature implementations — Claude scaffolds infrastructure and writes the assignment; the user writes all component/hook/state code.

## Process Going Forward

Each app gets scaffolded as its own implementation-plan cycle (via the writing-plans skill), starting with App 1. After each app is scaffolded, the user builds it in their own time; the next app's plan is only executed when requested, so the curriculum can flex based on what the user wants to focus on next.

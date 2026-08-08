# National Parks Explorer

Your first React practice app. The API is already built and running; your job is to build the frontend that consumes it.

## Goal

Fetch and display a list of national parks. Clicking a park shows its full detail. This app is entirely read-only — no forms, no writes — so you can focus on the fetch → loading → render cycle.

## Running it

```bash
# terminal 1
cd api
npm install
npm run dev   # http://localhost:4001

# terminal 2
cd web
npm install
npm run dev   # http://localhost:5173
```

## Functional requirements

- On load, fetch `GET /api/parks` and render the list of parks.
- Show a loading indicator while the list is being fetched, and a readable error message if the fetch fails.
- Clicking a park fetches `GET /api/parks/:id` and displays its full detail (description, established year, size, activities) — with its own independent loading state, since it's a separate request from the list.
- Split your UI into at least two components (e.g. a list component and a detail component) so you practice passing data and event handlers via props.

## API contract

All endpoints are served from `http://localhost:4001` — since the frontend runs on a different origin (`5173`), fetch the full URL, e.g. `fetch('http://localhost:4001/api/parks')`. The API enables CORS for this.

`GET /api/parks` → array of summaries:

```json
[{ "id": "yellowstone", "name": "Yellowstone", "state": "WY, MT, ID", "tagline": "America's first national park" }]
```

`GET /api/parks/:id` → full detail:

```json
{
  "id": "yellowstone",
  "name": "Yellowstone",
  "state": "WY, MT, ID",
  "tagline": "America's first national park",
  "description": "...",
  "established": "1872",
  "sizeAcres": 2219791,
  "activities": ["Hiking", "Wildlife watching", "Geysers", "Camping"]
}
```

`GET /api/parks/:id` returns a 404 with `{ "error": "Park not found" }` for an unknown id.

## Concepts to practice

- `useState` — tracking the park list, the selected park's detail, loading flags, and error state
- `useEffect` — fetching on mount, and re-fetching detail when the selected id changes (dependency arrays)
- Conditional rendering — loading / error / empty / loaded states
- Rendering lists with `.map()` and a stable `key`
- Event handlers — clicking a park to select it
- Props — passing data and callbacks from a parent component down to children

## Stretch goals

- Add a text input that filters the visible list client-side as you type (a controlled input).
- Add a "favorite" star toggle per park, held in local state (no API changes needed).

## Suggested test

The API already has a worked-example test suite at `api/src/routes/parks.test.ts` — read it to see the pattern (supertest hitting the running Express app directly, no real server needed). Run it with `npm test` from `api/`.

For the frontend, try writing a test in `web/src/` using React Testing Library and Vitest that mocks `fetch` and asserts the component shows a loading state first, then renders the park list once the fetch resolves. Run it with `npm test` from `web/`.

# Repository Guidelines

## Project Structure & Module Organization
- `frontend/`: Vite + React + TypeScript client. Source lives in `src/`, static assets in `public/`, build artefacts output to `dist/`.
- `backend/`: Flask API managed by `uv`. Application code is in `app.py` with entry point `main.py`; environment examples live in `.env.example`.
- Shared docs (`README.md`, this guide) sit at the repo root. Keep infra files (`fly.toml`, Dockerfiles) beside the service they configure.

## Build, Test, and Development Commands
- Frontend dev server: `npm run dev` (inside `frontend/`) starts Vite on `http://localhost:5173`.
- Frontend build: `npm run build` produces production assets and type-checks with `tsc -b`.
- Frontend lint: `npm run lint` runs ESLint with the repo-configured rules.
- Backend deps: `UV_CACHE_DIR="$(pwd)/../.uv-cache" uv sync` (inside `backend/`) installs the locked environment.
- Backend server: `UV_CACHE_DIR="$(pwd)/../.uv-cache" uv run flask --app app --debug run --port 8000`.

## Coding Style & Naming Conventions
- TypeScript/JS: 2-space indentation, prefer functional React components, and keep files PascalCase for components (`HelloCard.tsx`) and camelCase for hooks/utilities (`useData.ts`).
- Python: follow `black`-compatible formatting (4 spaces). Modules lowercase with underscores; functions and variables snake_case.
- Environment variables: prefix frontend values with `VITE_` (e.g., `VITE_API_BASE_URL`) and document backend settings in `.env.example`.

## Testing Guidelines
- Frontend: add Vitest or Playwright suites under `frontend/src/__tests__/`. Name files `*.test.ts(x)` and run via `npm test` once configured (ensure CI calls it before deploy).
- Backend: favour `pytest` with files under `backend/tests/`. Use descriptive test names (`test_health_endpoint_returns_ok`). Integrate `uv run pytest` into CI when tests exist.

## Commit & Pull Request Guidelines
- Write imperative, scoped commit messages (`feat: add health endpoint`). Group unrelated changes into separate commits.
- Pull requests should summarize the change, note impacted services (frontend/backend), link tracking issues, and include screenshots or curl output when touching UI or API responses.
- Ensure CI workflows for both apps pass before requesting review. Mention deployment considerations (env vars, Fly config) so reviewers can validate post-merge steps.

## Deployment & Configuration Tips
- Set `VITE_API_BASE_URL` for the frontend and `CORS_ALLOWED_ORIGINS` for the backend via Fly secrets (`fly secrets set ...`).
- Use `.env.example` files as the single source for required configuration keys; update them whenever new variables are introduced.

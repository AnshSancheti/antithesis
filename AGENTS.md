# Repository Guidelines

## Project Structure & Module Organization
- `frontend/`: Vite + React + TypeScript UI. Core components live in `src/`; static assets in `public/`; tests go in `src/__tests__/` when added.
- `backend/`: Flask API with SQLAlchemy models. Domain code is in `app/`, migrations in `migrations/`, seed data in `seeds/`, and tests in `tests/`.
- Root docs (`README.md`, `AGENTS.md`) describe workflows; CI/CD configs live under `.github/` when introduced.

## Build, Test, and Development Commands
- Frontend dev server: `cd frontend && npm install && npm run dev` (hot reload on http://localhost:5173).
- Frontend build: `npm run build` generates `dist/`; `npm run lint` checks ESLint rules.
- Backend env: `cd backend && export UV_CACHE_DIR="$(pwd)/../.uv-cache" && uv sync` installs dependencies.
- Backend app: `uv run flask --app app:create_app --debug run --port 8000` launches the API on http://127.0.0.1:8000.
- Tests: `uv run pytest` (backend) and `npm test` or `npm run lint` (frontend) once suites are present.

## Coding Style & Naming Conventions
- TypeScript/JS: 2-space indentation, functional React components, PascalCase for components (`VoteCard.tsx`), camelCase for utilities (`formatVotes.ts`).
- Python: PEP 8 / Black style with 4-space indentation, snake_case names, SQLAlchemy models in singular form.
- Environment files: keep real values in uncommitted `.env`; share templates via `.env.example`. Never commit secrets.

## Testing Guidelines
- Frontend: use Vitest + React Testing Library; place files in `src/__tests__/name.test.tsx`. Snapshot sparingly; prefer behavioural assertions.
- Backend: pytest with fixtures for database sessions. Cover models, API routes, and materialized view behaviour. Ensure negative cases (duplicate votes, invalid pairs) are asserted.
- Strive for fast, deterministic tests that run in CI without external services.

## Commit & Pull Request Guidelines
- Follow conventional commit verbs (`feat`, `fix`, `chore`, `docs`) and keep messages imperative (`feat: add vote endpoint`).
- Each PR should explain the change, call out affected services (frontend/backend), link issues, and add screenshots or JSON examples when touching UI or API responses.
- Ensure `npm run build`, `npm run lint`, and `uv run pytest` pass locally before requesting review. Document migration steps or new env vars in the PR body.

## Security & Configuration Tips
- Use `fly secrets set` for production secrets like `DATABASE_URL` and `VITE_API_BASE_URL`.
- Rotate credentials periodically and never log sensitive request data.

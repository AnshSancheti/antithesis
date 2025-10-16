# Backend

Flask API paired with a PostgreSQL data store for the phrase voting application.

## Setup

1. Copy configuration and create a local Python environment with uv (cache dir keeps everything inside the repo):
   ```bash
   cp .env.example .env  # edit if you need to allow more origins
   export UV_CACHE_DIR="$(pwd)/../.uv-cache"
   uv sync
   ```

2. Apply database migrations (requires `psql` or an equivalent Postgres client):
   ```bash
   psql "$DATABASE_URL" -f migrations/001_initial_schema.sql
   ```

3. Seed sample data (optional but useful for manual testing):
   ```bash
   export UV_CACHE_DIR="$(pwd)/../.uv-cache"
   uv run python seeds/load_seeds.py
   ```

4. Run the development server (reload enabled):
   ```bash
   export UV_CACHE_DIR="$(pwd)/../.uv-cache"
   uv run flask --app app:create_app --debug run --port 8000
   ```

The API lives at `http://127.0.0.1:8000`.

## API Endpoints

- `GET /api/hello` — simple liveness check.
- `GET /api/health` — health endpoint.
- `GET /api/quiz` — returns all active phrase pairs with their current vote totals.
- `POST /api/vote` — body: `{ "phrasePairId": number, "selectedPhraseId": number, "sessionId": string }`. Records a vote and returns `204 No Content` on success. Responds with status `400`, `404`, or `409` when validation fails or the session already voted.

## Tests

Run the automated test suite:

```bash
export UV_CACHE_DIR="$(pwd)/../.uv-cache"
uv run pytest
```

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

The API lives at `http://127.0.0.1:8000/api/hello`.

## Tests

Run the automated test suite:

```bash
export UV_CACHE_DIR="$(pwd)/../.uv-cache"
uv run pytest
```

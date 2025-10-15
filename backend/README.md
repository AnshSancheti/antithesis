# Backend

Simple Flask API that serves `Hello from Flask` and a health endpoint.

## Setup

1. Create a local Python environment with uv (cache dir keeps everything inside the repo):
   ```bash
   export UV_CACHE_DIR="$(pwd)/../.uv-cache"
   uv sync
   ```

2. Run the development server (reload enabled):
   ```bash
   export UV_CACHE_DIR="$(pwd)/../.uv-cache"
   uv run flask --app app --debug run --port 8000
   ```

The API lives at `http://127.0.0.1:8000/api/hello`.

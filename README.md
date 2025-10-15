# Antithesis Scaffold

This repository contains a minimal TypeScript React frontend (Vite) and a Flask backend managed with `uv`. Both applications are wired together so the frontend fetches its greeting from the backend.

## Project layout
- `frontend/` – Vite + React + TypeScript UI (`npm` based)
- `backend/` – Flask API managed by `uv`

## Prerequisites
- Node.js 18+
- npm 9+
- Python 3.13 (managed automatically by `uv`)

## Getting started
1. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   The dev server runs on [http://localhost:5173](http://localhost:5173).

2. Bootstrap the backend (from `backend/`):
   ```bash
   export UV_CACHE_DIR="$(pwd)/../.uv-cache"
   uv sync
   export UV_CACHE_DIR="$(pwd)/../.uv-cache"
   uv run flask --app app --debug run --port 8000
   ```
   The API exposes `GET /api/hello` and `GET /api/health` on [http://127.0.0.1:8000](http://127.0.0.1:8000).

With both servers running, open the frontend and it will display the greeting fetched from the Flask backend. If the backend is unavailable, the UI shows a helpful message.

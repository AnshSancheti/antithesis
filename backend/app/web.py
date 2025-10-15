"""Flask application factory and HTTP routes."""

from __future__ import annotations

import os
from typing import List

from flask import Flask, jsonify
from flask_cors import CORS

DEFAULT_ALLOWED_ORIGINS: List[str] = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]


def _resolve_allowed_origins() -> List[str]:
    raw = os.getenv("CORS_ALLOWED_ORIGINS", "")
    extras = [origin.strip() for origin in raw.split(",") if origin.strip()]
    merged = DEFAULT_ALLOWED_ORIGINS + extras
    # Preserve order while removing duplicates
    seen: set[str] = set()
    unique: List[str] = []
    for origin in merged:
        if origin not in seen:
            seen.add(origin)
            unique.append(origin)
    return unique


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": _resolve_allowed_origins()}})

    @app.get("/api/hello")
    def hello_world() -> tuple[dict[str, str], int]:  # pragma: no cover - simple route
        return jsonify(message="Hello from Flask"), 200

    @app.get("/api/health")
    def healthcheck() -> tuple[dict[str, str], int]:  # pragma: no cover - simple route
        return jsonify(status="ok"), 200

    return app

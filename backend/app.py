import os

from flask import Flask, jsonify
from flask_cors import CORS

DEFAULT_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]


def _resolve_allowed_origins() -> list[str]:
    raw = os.getenv("CORS_ALLOWED_ORIGINS", "")
    extras = [origin.strip() for origin in raw.split(",") if origin.strip()]
    merged = DEFAULT_ALLOWED_ORIGINS + extras
    # Preserve order while removing duplicates
    seen: set[str] = set()
    unique: list[str] = []
    for origin in merged:
        if origin not in seen:
            seen.add(origin)
            unique.append(origin)
    return unique


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": _resolve_allowed_origins()}})

    @app.get("/api/hello")
    def hello_world() -> tuple[dict[str, str], int]:
        return jsonify(message="Hello from Flask"), 200

    @app.get("/api/health")
    def healthcheck() -> tuple[dict[str, str], int]:
        return jsonify(status="ok"), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

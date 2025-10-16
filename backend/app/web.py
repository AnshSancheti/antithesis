"""Flask application factory and HTTP routes."""

from __future__ import annotations

import os
from typing import List

from flask import Flask, jsonify
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
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

    from .database import SessionLocal
    from .models import PhrasePair, Vote

    @app.get("/api/hello")
    def hello_world() -> tuple[dict[str, str], int]:  # pragma: no cover - simple route
        return jsonify(message="Hello from Flask"), 200

    @app.get("/api/health")
    def healthcheck() -> tuple[dict[str, str], int]:  # pragma: no cover - simple route
        return jsonify(status="ok"), 200

    @app.get("/api/quiz")
    def list_quiz_pairs() -> tuple[dict[str, object], int]:
        """Return all active phrase pairs with current vote totals."""

        with SessionLocal() as session:
            # TODO: introduce pagination when the active set becomes large
            pairs = (
                session.execute(
                    select(PhrasePair)
                    .where(PhrasePair.is_active.is_(True))
                    .options(joinedload(PhrasePair.phrase_a), joinedload(PhrasePair.phrase_b))
                )
                .scalars()
                .all()
            )

            phrase_ids = {
                pair.phrase_a_id for pair in pairs
            } | {pair.phrase_b_id for pair in pairs}

            counts: dict[int, int] = {}
            if phrase_ids:
                count_rows = session.execute(
                    select(Vote.selected_phrase_id, func.count(Vote.id))
                    .where(Vote.selected_phrase_id.in_(phrase_ids))
                    .group_by(Vote.selected_phrase_id)
                ).all()
                counts = {phrase_id: total for phrase_id, total in count_rows}

        payload = {
            "pairs": [
                {
                    "id": pair.id,
                    "phraseA": {
                        "id": pair.phrase_a.id,
                        "text": pair.phrase_a.text,
                        "totalVotes": counts.get(pair.phrase_a.id, 0),
                    },
                    "phraseB": {
                        "id": pair.phrase_b.id,
                        "text": pair.phrase_b.text,
                        "totalVotes": counts.get(pair.phrase_b.id, 0),
                    },
                    "totalVotes": (
                        counts.get(pair.phrase_a.id, 0) + counts.get(pair.phrase_b.id, 0)
                    ),
                }
                for pair in pairs
            ]
        }

        return jsonify(payload), 200

    return app

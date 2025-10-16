"""Flask application factory and HTTP routes."""

from __future__ import annotations

import os
from typing import List

from flask import Flask, jsonify, request
from sqlalchemy import exc as sa_exc, func, select
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

    @app.post("/api/vote")
    def submit_vote():
        """Record a vote for a phrase within a pair.

        Expected payload: {"phrasePairId": int, "selectedPhraseId": int, "sessionId": str}
        Returns 204 No Content on success. Errors: 400 validation, 404 not found, 409 duplicate vote.
        """

        payload = request.get_json(silent=True) or {}

        try:
            pair_id = int(payload.get("phrasePairId"))
            selected_phrase_id = int(payload.get("selectedPhraseId"))
        except (TypeError, ValueError):
            return jsonify(error="phrasePairId and selectedPhraseId must be integers"), 400

        session_id = payload.get("sessionId")
        if not session_id or not isinstance(session_id, str):
            return jsonify(error="sessionId is required"), 400
        session_id = session_id.strip()
        if not session_id:
            return jsonify(error="sessionId cannot be blank"), 400
        if len(session_id) > 128:
            return jsonify(error="sessionId is too long"), 400

        with SessionLocal() as session:
            pair = session.execute(
                select(PhrasePair)
                .where(PhrasePair.id == pair_id)
                .options(joinedload(PhrasePair.phrase_a), joinedload(PhrasePair.phrase_b))
            ).scalar_one_or_none()

            if pair is None:
                return jsonify(error="Phrase pair not found"), 404

            if selected_phrase_id not in {pair.phrase_a_id, pair.phrase_b_id}:
                return jsonify(error="Selected phrase is not part of the pair"), 400

            vote = Vote(
                phrase_pair_id=pair_id,
                selected_phrase_id=selected_phrase_id,
                session_id=session_id,
            )

            session.add(vote)

            try:
                session.commit()
            except sa_exc.IntegrityError as exc:  # pragma: no cover - defensive path
                session.rollback()
                message = str(getattr(exc, "orig", exc))
                if "uq_vote_pair_session" in message:
                    return jsonify(error="Session has already voted for this pair"), 409
                return jsonify(error="Invalid vote"), 400

        return ("", 204)

    return app

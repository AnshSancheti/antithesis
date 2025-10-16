"""Integration tests for the /api/quiz endpoint."""

from __future__ import annotations

import json
from typing import Any

import pytest
from flask import Flask
from sqlalchemy import func, select

from app import create_app
from app.database import SessionLocal
from app.models import PhrasePair, Phrase, Vote


@pytest.fixture(scope="module")
def app_instance() -> Flask:
    return create_app()


@pytest.fixture()
def client(app_instance: Flask):
    return app_instance.test_client()


def test_quiz_returns_active_pairs(client) -> None:
    response = client.get("/api/quiz")
    assert response.status_code == 200

    payload: dict[str, Any] = json.loads(response.data)
    assert "pairs" in payload
    assert isinstance(payload["pairs"], list)

    # ensure only active pairs are returned
    with SessionLocal() as session:
        active_pair_ids = {
            row.id
            for row in session.execute(
                select(PhrasePair.id).where(PhrasePair.is_active.is_(True))
            )
        }

    returned_ids = {item["id"] for item in payload["pairs"]}
    assert returned_ids == active_pair_ids


def test_quiz_includes_vote_totals(client) -> None:
    response = client.get("/api/quiz")
    payload = json.loads(response.data)

    with SessionLocal() as session:
        counts = {
            phrase_id: total
            for phrase_id, total in session.execute(
                select(Vote.selected_phrase_id, func.count(Vote.id)).group_by(Vote.selected_phrase_id)
            )
        }
        phrases = {
            phrase.id: phrase
            for phrase in session.execute(select(Phrase)).scalars().all()
        }

    for pair in payload["pairs"]:
        phrase_a = pair["phraseA"]
        phrase_b = pair["phraseB"]

        assert phrase_a["totalVotes"] == counts.get(phrase_a["id"], 0)
        assert phrase_b["totalVotes"] == counts.get(phrase_b["id"], 0)
        assert phrase_a["text"] == phrases[phrase_a["id"]].text
        assert phrase_b["text"] == phrases[phrase_b["id"]].text

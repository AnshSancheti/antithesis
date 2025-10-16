"""Tests for the POST /api/vote endpoint."""

from __future__ import annotations

import json
from typing import Any

import pytest
from flask import Flask
from sqlalchemy import delete, select

from app import create_app
from app.database import SessionLocal
from app.models import PhrasePair, Vote


@pytest.fixture(scope="module")
def app_instance() -> Flask:
    return create_app()


@pytest.fixture()
def client(app_instance: Flask):
    return app_instance.test_client()


@pytest.fixture()
def active_pair() -> dict[str, Any]:
    with SessionLocal() as session:
        pair = session.execute(
            select(PhrasePair)
            .where(PhrasePair.is_active.is_(True))
            .limit(1)
        ).scalar_one()
        return {
            "id": pair.id,
            "phrase_a_id": pair.phrase_a_id,
            "phrase_b_id": pair.phrase_b_id,
        }


def test_vote_success(client, active_pair) -> None:
    payload = {
        "phrasePairId": active_pair["id"],
        "selectedPhraseId": active_pair["phrase_a_id"],
        "sessionId": "test-session-123",
    }
    response = client.post("/api/vote", json=payload)
    assert response.status_code == 204

    with SessionLocal() as session:
        vote = session.execute(
            select(Vote).where(
                Vote.phrase_pair_id == active_pair["id"],
                Vote.session_id == "test-session-123",
            )
        ).scalar_one_or_none()
    assert vote is not None
    assert vote.selected_phrase_id == active_pair["phrase_a_id"]

    with SessionLocal() as session:
        session.execute(
            delete(Vote).where(
                Vote.phrase_pair_id == active_pair["id"],
                Vote.session_id == "test-session-123",
            )
        )
        session.commit()


def test_vote_duplicate_session_returns_conflict(client, active_pair) -> None:
    payload = {
        "phrasePairId": active_pair["id"],
        "selectedPhraseId": active_pair["phrase_b_id"],
        "sessionId": "duplicate-session",
    }
    response_first = client.post("/api/vote", json=payload)
    assert response_first.status_code == 204

    response_second = client.post("/api/vote", json=payload)
    assert response_second.status_code == 409

    with SessionLocal() as session:
        session.execute(
            delete(Vote).where(
                Vote.phrase_pair_id == active_pair["id"],
                Vote.session_id == "duplicate-session",
            )
        )
        session.commit()


def test_vote_invalid_phrase_returns_bad_request(client, active_pair) -> None:
    payload = {
        "phrasePairId": active_pair["id"],
        "selectedPhraseId": 999999,
        "sessionId": "invalid-phrase",
    }
    response = client.post("/api/vote", json=payload)
    assert response.status_code == 400


def test_vote_missing_pair_returns_not_found(client) -> None:
    payload = {
        "phrasePairId": 999999,
        "selectedPhraseId": 1,
        "sessionId": "missing-pair",
    }
    response = client.post("/api/vote", json=payload)
    assert response.status_code == 404

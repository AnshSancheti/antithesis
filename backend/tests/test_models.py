"""Tests for ORM configuration and migration artifacts."""

from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy import CheckConstraint, UniqueConstraint

from app.models import PhrasePair, PhraseVoteCount, Vote


def test_phrase_pair_constraints() -> None:
    constraints = PhrasePair.__table__.constraints
    check_names = {c.name for c in constraints if isinstance(c, CheckConstraint)}
    unique_names = {c.name for c in constraints if isinstance(c, UniqueConstraint)}

    assert "ck_phrase_pair_distinct" in check_names
    assert "uq_phrase_pair_unique_combination" in unique_names


def test_vote_unique_session_constraint() -> None:
    constraints = Vote.__table__.constraints
    unique_names = {c.name for c in constraints if isinstance(c, UniqueConstraint)}

    assert "uq_vote_pair_session" in unique_names


def test_materialized_view_model_shape() -> None:
    columns = PhraseVoteCount.__table__.c
    assert set(columns.keys()) == {"phrase_id", "total_votes", "created_at", "updated_at"}
    assert PhraseVoteCount.__table__.info.get("materialized_view") is True


def test_migration_creates_materialized_view() -> None:
    migration_sql = (Path(__file__).resolve().parents[1] / "migrations" / "001_initial_schema.sql").read_text()
    assert "CREATE MATERIALIZED VIEW phrase_vote_counts" in migration_sql
    assert re.search(r"REFRESH MATERIALIZED VIEW phrase_vote_counts", migration_sql)
    assert "CREATE TRIGGER trg_refresh_counts_on_votes" in migration_sql


def test_seed_files_have_rows() -> None:
    seeds_dir = Path(__file__).resolve().parents[1] / "seeds"
    for filename in ("phrases.csv", "phrase_pairs.csv", "votes.csv"):
        path = seeds_dir / filename
        assert path.exists(), f"Missing seed file: {filename}"
        content = path.read_text().strip().splitlines()
        # content includes header; ensure there is at least one data row in addition to header
        assert len(content) >= 2, f"Seed file {filename} must contain at least one row"

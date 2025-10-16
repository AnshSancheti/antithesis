"""Seed the database with sample phrases, phrase pairs, and votes."""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Iterable

BASE_PATH = Path(__file__).parent
PROJECT_ROOT = BASE_PATH.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy.dialects.postgresql import insert

from app.database import SessionLocal
from app.models import Phrase, PhrasePair, Vote


def read_csv_rows(filename: str) -> Iterable[dict[str, str]]:
    with (BASE_PATH / filename).open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield row


def seed_phrases(session) -> int:
    stmt = insert(Phrase).values([
        {
            "id": int(row["id"]),
            "text": row["text"],
            "created_at": row["created_at"],
        }
        for row in read_csv_rows("phrases.csv")
    ])
    stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
    result = session.execute(stmt)
    return result.rowcount or 0


def seed_phrase_pairs(session) -> int:
    stmt = insert(PhrasePair).values([
        {
            "id": int(row["id"]),
            "phrase_a_id": int(row["phrase_a_id"]),
            "phrase_b_id": int(row["phrase_b_id"]),
            "is_active": row["is_active"].lower() == "true",
            "created_at": row["created_at"],
        }
        for row in read_csv_rows("phrase_pairs.csv")
    ])
    stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
    result = session.execute(stmt)
    return result.rowcount or 0


def seed_votes(session) -> int:
    stmt = insert(Vote).values([
        {
            "id": int(row["id"]),
            "phrase_pair_id": int(row["phrase_pair_id"]),
            "selected_phrase_id": int(row["selected_phrase_id"]),
            "session_id": row["session_id"],
            "created_at": row["created_at"],
        }
        for row in read_csv_rows("votes.csv")
    ])
    stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
    result = session.execute(stmt)
    return result.rowcount or 0

def main() -> None:
    with SessionLocal() as session:
        with session.begin():
            inserted_phrases = seed_phrases(session)
            inserted_pairs = seed_phrase_pairs(session)
            inserted_votes = seed_votes(session)
    print(
        "Seed complete: %d phrases, %d phrase pairs, %d votes" % (
            inserted_phrases,
            inserted_pairs,
            inserted_votes,
        )
    )


if __name__ == "__main__":
    main()

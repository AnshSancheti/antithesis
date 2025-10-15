"""ORM models representing the phrase voting domain."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Phrase(Base):
    """A unique phrase that can appear in a voting pair."""

    __tablename__ = "phrases"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    phrase_pairs_a: Mapped[List["PhrasePair"]] = relationship(
        back_populates="phrase_a", foreign_keys="PhrasePair.phrase_a_id"
    )
    phrase_pairs_b: Mapped[List["PhrasePair"]] = relationship(
        back_populates="phrase_b", foreign_keys="PhrasePair.phrase_b_id"
    )
    votes: Mapped[List["Vote"]] = relationship(back_populates="selected_phrase")

    def __repr__(self) -> str:  # pragma: no cover - for debugging convenience
        return f"Phrase(id={self.id!r}, text={self.text!r})"


class PhrasePair(Base):
    """A pair of phrases presented together for voting."""

    __tablename__ = "phrase_pairs"
    __table_args__ = (
        CheckConstraint("phrase_a_id <> phrase_b_id", name="ck_phrase_pair_distinct"),
        UniqueConstraint(
            "phrase_a_id",
            "phrase_b_id",
            name="uq_phrase_pair_unique_combination",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    phrase_a_id: Mapped[int] = mapped_column(ForeignKey("phrases.id", ondelete="RESTRICT"))
    phrase_b_id: Mapped[int] = mapped_column(ForeignKey("phrases.id", ondelete="RESTRICT"))
    is_active: Mapped[bool] = mapped_column(nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    phrase_a: Mapped[Phrase] = relationship(
        back_populates="phrase_pairs_a", foreign_keys=[phrase_a_id]
    )
    phrase_b: Mapped[Phrase] = relationship(
        back_populates="phrase_pairs_b", foreign_keys=[phrase_b_id]
    )
    votes: Mapped[List["Vote"]] = relationship(back_populates="phrase_pair")

    def __repr__(self) -> str:  # pragma: no cover
        return f"PhrasePair(id={self.id!r}, phrase_a_id={self.phrase_a_id!r}, phrase_b_id={self.phrase_b_id!r})"


class Vote(Base):
    """A single vote cast by a user session for a phrase within a pair."""

    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint("phrase_pair_id", "session_id", name="uq_vote_pair_session"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    phrase_pair_id: Mapped[int] = mapped_column(
        ForeignKey("phrase_pairs.id", ondelete="CASCADE"), nullable=False
    )
    selected_phrase_id: Mapped[int] = mapped_column(
        ForeignKey("phrases.id", ondelete="RESTRICT"), nullable=False
    )
    session_id: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    phrase_pair: Mapped[PhrasePair] = relationship(back_populates="votes")
    selected_phrase: Mapped[Phrase] = relationship(back_populates="votes")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            "Vote(id={!r}, phrase_pair_id={!r}, selected_phrase_id={!r}, session_id={!r})".format(
                self.id, self.phrase_pair_id, self.selected_phrase_id, self.session_id
            )
        )


class PhraseVoteCount(Base):
    """Materialized view projecting aggregate vote counts per phrase."""

    __tablename__ = "phrase_vote_counts"
    __table_args__ = {"info": {"materialized_view": True}}

    phrase_id: Mapped[int] = mapped_column(primary_key=True)
    total_votes: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    phrase: Mapped[Phrase] = relationship(viewonly=True, primaryjoin="PhraseVoteCount.phrase_id == Phrase.id")

    def __repr__(self) -> str:  # pragma: no cover
        return f"PhraseVoteCount(phrase_id={self.phrase_id!r}, total_votes={self.total_votes!r})"

"""Database configuration and SQLAlchemy session helpers."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker


class Base(DeclarativeBase):
    """Base class for all ORM models."""


DATABASE_URL = os.getenv("DATABASE_URL")

#if DATABASE_URL.startswith("postgresql://"):
#    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True, future=True)

SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


@contextmanager
def session_scope() -> Iterator[scoped_session]:
    """Provide a transactional scope around a series of operations."""

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:  # pragma: no cover - defensive rollback path
        session.rollback()
        raise
    finally:
        session.close()

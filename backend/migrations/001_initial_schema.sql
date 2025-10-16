-- Migration: create core voting schema
-- Requirements satisfied: phrases, phrase_pairs, votes tables

BEGIN;

CREATE TABLE IF NOT EXISTS phrases (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS phrase_pairs (
    id SERIAL PRIMARY KEY,
    phrase_a_id INTEGER NOT NULL REFERENCES phrases(id) ON DELETE RESTRICT,
    phrase_b_id INTEGER NOT NULL REFERENCES phrases(id) ON DELETE RESTRICT,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_phrase_pair_distinct CHECK (phrase_a_id <> phrase_b_id),
    CONSTRAINT uq_phrase_pair_unique_combination UNIQUE (phrase_a_id, phrase_b_id)
);

CREATE TABLE IF NOT EXISTS votes (
    id BIGSERIAL PRIMARY KEY,
    phrase_pair_id INTEGER NOT NULL REFERENCES phrase_pairs(id) ON DELETE CASCADE,
    selected_phrase_id INTEGER NOT NULL REFERENCES phrases(id) ON DELETE RESTRICT,
    session_id VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_vote_pair_session UNIQUE (phrase_pair_id, session_id)
);

CREATE OR REPLACE FUNCTION enforce_vote_phrase_membership()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM phrase_pairs AS pp
        WHERE pp.id = NEW.phrase_pair_id
          AND (pp.phrase_a_id = NEW.selected_phrase_id OR pp.phrase_b_id = NEW.selected_phrase_id)
    ) THEN
        RAISE EXCEPTION 'Selected phrase % is not part of pair %', NEW.selected_phrase_id, NEW.phrase_pair_id
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_votes_enforce_phrase_membership ON votes;
CREATE TRIGGER trg_votes_enforce_phrase_membership
BEFORE INSERT OR UPDATE ON votes
FOR EACH ROW
EXECUTE FUNCTION enforce_vote_phrase_membership();

COMMIT;

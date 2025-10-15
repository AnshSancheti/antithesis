-- Migration: create core voting schema and materialized view cache
-- Requirements satisfied: phrases, phrase_pairs, votes tables, phrase_vote_counts materialized view

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

-- Materialized view to cache aggregate vote counts per phrase
DROP MATERIALIZED VIEW IF EXISTS phrase_vote_counts;
CREATE MATERIALIZED VIEW phrase_vote_counts AS
SELECT
    p.id AS phrase_id,
    COALESCE(COUNT(v.id), 0)::BIGINT AS total_votes,
    CASE WHEN COUNT(v.id) > 0 THEN MIN(v.created_at) ELSE p.created_at END AS created_at,
    CASE WHEN COUNT(v.id) > 0 THEN MAX(v.created_at) ELSE p.created_at END AS updated_at
FROM phrases AS p
LEFT JOIN votes AS v ON v.selected_phrase_id = p.id
GROUP BY p.id, p.created_at;

CREATE UNIQUE INDEX IF NOT EXISTS uq_phrase_vote_counts_phrase_id
    ON phrase_vote_counts (phrase_id);

CREATE OR REPLACE FUNCTION refresh_phrase_vote_counts()
RETURNS TRIGGER AS $$
BEGIN
    -- serialize refresh calls to avoid contention
    PERFORM pg_advisory_xact_lock(871234);
    REFRESH MATERIALIZED VIEW phrase_vote_counts;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_refresh_counts_on_votes ON votes;
CREATE TRIGGER trg_refresh_counts_on_votes
AFTER INSERT OR UPDATE OR DELETE ON votes
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_phrase_vote_counts();

DROP TRIGGER IF EXISTS trg_refresh_counts_on_phrases ON phrases;
CREATE TRIGGER trg_refresh_counts_on_phrases
AFTER INSERT OR UPDATE OR DELETE ON phrases
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_phrase_vote_counts();

-- initial refresh to ensure freshly created view accurately reflects empty dataset
REFRESH MATERIALIZED VIEW phrase_vote_counts;

COMMIT;

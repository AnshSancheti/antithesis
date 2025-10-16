# Phrase Voting Schema

## Overview
The schema supports presenting two phrases, collecting votes, and reporting live tallies. It targets PostgreSQL (Fly.io managed or local) and uses efficient on-demand aggregations to keep API responses fast without additional cache layers.

```
phrases ─┬──── phrase_pairs ─── votes
         │           │
         └───────────┘
```

## Tables
- **phrases**: Primary catalogue of phrases (`id`, `text`, `created_at`). `text` is unique to avoid duplicates.
- **phrase_pairs**: Connects two distinct phrases, enforcing `phrase_a_id <> phrase_b_id` and uniqueness of the combination. `is_active` marks the pair currently shown to voters.
- **votes**: Records one vote per session per pair with a unique constraint on (`phrase_pair_id`, `session_id`). A trigger validates that the selected phrase belongs to the pair.

## Aggregations
- Totals per phrase are calculated on demand by aggregating the `votes` table. The `/api/quiz` endpoint performs this aggregation in a single query so the client receives fresh counts with minimal latency.

## Integrity & Concurrency
- Foreign keys cascade deletes only where safe (`votes` cascade on pair removal) and restrict when data should persist (`phrases`).
- Check and trigger-based validation prevent malformed data, preserving analytics accuracy even under concurrent voting.

## Access Patterns
- **Read phrases & pairs**: Query `phrase_pairs` joined to `phrases` for UI display.
- **Aggregate pairs**: Use `/api/quiz` to fetch all active pairs and current totals; the query aggregates votes on demand and returns a combined payload for the UI.
- **Cast vote**: POST `/api/vote` inserts a row into `votes`; triggers enforce membership and the unique constraint prevents duplicate session votes.
- **Fetch tallies**: Any SQL client can run `SELECT selected_phrase_id, COUNT(*) FROM votes GROUP BY selected_phrase_id` to produce the same counts used by the API.

## Error Handling Notes
- Violating the pair membership rule raises SQLSTATE `23514`; surface this as a 400-level error in the API.
- Aggregation is part of the read query; transactional inserts ensure vote counts remain consistent. If a read fails, the caller receives an error rather than stale data.

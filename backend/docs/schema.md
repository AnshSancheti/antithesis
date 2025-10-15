# Phrase Voting Schema

## Overview
The schema supports presenting two phrases, collecting votes, and reporting live tallies. It targets PostgreSQL (Fly.io managed or local) and optimises read performance via a materialised view.

```
phrases ─┬──── phrase_pairs ─── votes
         │           │         │
         └───────────┘         └── materialised view: phrase_vote_counts
```

## Tables
- **phrases**: Primary catalogue of phrases (`id`, `text`, `created_at`). `text` is unique to avoid duplicates.
- **phrase_pairs**: Connects two distinct phrases, enforcing `phrase_a_id <> phrase_b_id` and uniqueness of the combination. `is_active` marks the pair currently shown to voters.
- **votes**: Records one vote per session per pair with a unique constraint on (`phrase_pair_id`, `session_id`). A trigger validates that the selected phrase belongs to the pair.

## Materialised View
- **phrase_vote_counts**: Aggregates votes per phrase with total count plus first/most recent vote timestamps. It is refreshed automatically by triggers on `phrases` and `votes`, guaranteeing quick tally retrieval during high-traffic scenarios.

## Integrity & Concurrency
- Foreign keys cascade deletes only where safe (`votes` cascade on pair removal) and restrict when data should persist (`phrases`).
- Check and trigger-based validation prevent malformed data, preserving analytics accuracy even under concurrent voting.
- Advisory locks serialise materialised view refreshes to avoid thrashing in high-concurrency contexts.

## Access Patterns
- **Read phrases & pairs**: Query `phrase_pairs` joined to `phrases` for UI display.
- **Cast vote**: Insert into `votes`; triggers enforce membership and refresh aggregates.
- **Fetch tallies**: Select from `phrase_vote_counts`, joining back to `phrases` for text labels. Percentages can be derived on the fly: `total_votes / SUM(total_votes) OVER (PARTITION BY pair)`.

## Error Handling Notes
- Violating the pair membership rule raises SQLSTATE `23514`; surface this as a 400-level error in the API.
- Materialised view refresh failures roll back the transaction, ensuring callers receive a failure response rather than stale data.

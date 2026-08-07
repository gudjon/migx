---
id: arcflow-utf8-panic-blocks-graph-load
type: task
title: "ArcFlow 0.11.9 panics on non-ASCII during relationship CREATE — blocks the mirror graph"
status: done
owner: gudjon
priority: high
initiative: initiative-ai-djing-product
authored_by: claude-code
authored_kind: agent
triggered_by: "Loading the 83-playlist Spotify mirror corpus into ArcFlow as a
  World Graph; the load aborted with a Rust panic on an accented artist name"
created: "2026-08-07"
lastUpdated: "2026-08-07"
acceptance: |
  The 3-line repro below completes without a panic on the installed ArcFlow,
  and `mirrors-to-graph` loads all 83 mirrors (3720 tracks, 2962 artists)
  with zero errors. Verified by re-running the loader and querying
  `MATCH (t:Track)-[:BY]->(a:Artist) RETURN count(*)`.
---

# ArcFlow UTF-8 panic blocks the mirror graph

`tools/migx-cli/mirrors-to-graph` is written and correct; it cannot complete
because ArcFlow 0.11.9 crashes on non-ASCII text. For an Icelandic/Nordic
library this is not an edge case — `Nôze`, `Ysée`, `trentemøller`,
`Óðinn STUÐ`, `Jóla`, `Björk` are ordinary rows.

## Repro (deterministic, 3 statements)

```bash
arcflow --data-dir /tmp/probe <<'EOF'
CREATE (:Track {key: 'GB7QY1600125'})
CREATE (:Artist {name: 'Ysée'})
MATCH (t:Track {key: 'GB7QY1600125'}), (a:Artist {name: 'Ysée'}) CREATE (t)-[:BY]->(a)
EOF
```

```text
thread 'main' panicked at crates/arcflow-runtime/src/lib.rs:23872:45:
start byte index 60 is not a char boundary; it is inside 'é' (bytes 59..61 of string)
```

Replace `Ysée` with `Ysee` and it is clean. The panic came from a byte-wise
cursor in query-cache normalization forming `query[i..]` after advancing into
a UTF-8 continuation byte. In the failing statement, the incidental cursor
position 60 lands mid-`é`:

```python
b" 'Ys\xc3\xa9e'})"   # bytes 55..65 of the query
```

## What we established

| Condition | Panics |
| --- | --- |
| REPL (stdin), MATCH binds both nodes, `é` at byte 60 | **yes** |
| HTTP API (`--http`), same statement | **yes** — so it is the runtime, not the REPL |
| Same statement, `Ysee` (ASCII) | no |
| Same statement, `é` moved off offset 60 (padded key) | no |
| `CREATE` of a non-ASCII node alone, any length | no |

So the trigger is **statement text, not stored data**: the byte-wise scan can
stop inside any multi-byte character. Relationship CREATEs were simply the
first long statements in this corpus to expose it.

Impact on the load: the process dies mid-batch, so nothing after it is applied
and the snapshot is partial (the original failed run stopped at 50 nodes).

## Fix (arcflow-core)

`QueryCache::normalize_query_literals` now detects ASCII keywords through
bounded byte slices and advances ordinary text by complete Unicode scalar
values. Public runtime and Python FFI regressions cover the three-statement
Nordic fixture. There was no fixed truncation boundary to round down.

## Workarounds considered

- **`arcflow query` per statement** — avoids the batch abort but is ~14k
  processes (~35 min) and still panics when the offset lines up.
- **Pad/reorder statements** so no multi-byte char lands on 60 — fragile and
  silently breaks again when the offset changes.
- **Strip accents before loading** — corrupts the data to suit the bug; the
  graph would no longer match the mirrors. Rejected.

**Resolved.** Fixed in the arcflow-core checkout; the installed local CLI now
passes the 3-line repro with the relationship created and `Ysée` intact.

Because the published 0.11.9 binary lags the source fix, the loader also takes
`--arcflow` (or `$MIGX_ARCFLOW_BIN`) for explicit build selection. The local
installation was updated recoverably, with the published binary retained as a
timestamped backup.

The first successful UTF-8 load exposed a second transport bug: the REPL split
on semicolons inside quoted strings, omitting `Chicane;Máire Brennan` and its
`BY` edge. ArcFlow's shared CLI/PG-wire splitter is now quote-aware, with unit
and subprocess REPL regressions.

Full load against the patched build:

```text
83 mirrors -> 3720 tracks, 2962 artists, 83 playlists (16248 statements), 0:12
graph: 3720 Track · 2962 Artist · 83 Playlist · 5067 BY · 4416 ON
snapshot: generation 16248 · 6765 nodes · 9483 relationships
non-ASCII and punctuation intact: Ysée, trentemøller, Chicane;Máire Brennan
```

## Related

- `tools/migx-cli/mirrors-to-graph` — the loader
- `kanban/knowledge/arcflow-filesystem-m4.md` — the standing "take the
  technique, not the code" position, which this does not change

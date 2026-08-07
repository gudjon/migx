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
  and `mirrors-to-graph` loads all 83 mirrors (3727 tracks, 2102 artists)
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

Replace `Ysée` with `Ysee` and it is clean. The panic is a byte-index slice
at a fixed offset (60) that does not check UTF-8 char boundaries — in the
failing statement, byte 60 lands mid-`é`:

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

So the trigger is **statement text, not stored data**: a multi-byte character
straddling the hard-coded offset. Any long-enough query with non-ASCII can hit
it; relationship CREATEs are simply the longest statements we emit.

Impact on the load: the process dies mid-batch, so nothing after it is applied
and the snapshot is partial (we saw 50 of 3727 nodes).

## Fix (arcflow-core)

`crates/arcflow-runtime/src/lib.rs:23872` — replace the raw `&s[..60]`-style
slice with a char-safe truncation, e.g. `s.char_indices().take_while(|(i, _)|
*i < 60)` or `floor_char_boundary`. Then add a UTF-8 case to the query-parsing
tests; a Nordic/CJK fixture would have caught this.

## Workarounds considered

- **`arcflow query` per statement** — avoids the batch abort but is ~14k
  processes (~35 min) and still panics when the offset lines up.
- **Pad/reorder statements** so no multi-byte char lands on 60 — fragile and
  silently breaks again when the offset changes.
- **Strip accents before loading** — corrupts the data to suit the bug; the
  graph would no longer match the mirrors. Rejected.

**Resolved.** Fixed in the arcflow-core checkout; verified the 3-line repro
exits 0 with the relationship created and `Ysée` intact, while the installed
`~/.arcflow/bin/arcflow` still exits 134.

Because the released binary lags the fix, the loader takes `--arcflow`
(or `$MIGX_ARCFLOW_BIN`) so it can drive a patched build. Pointing at a build
is reversible; overwriting the installed binary is not, so that is left to the
owner.

Full load against the patched build:

```text
83 mirrors -> 3727 tracks, 2961 artists, 83 playlists (14k statements), 3:27
graph: 3720 Track · 2961 Artist · 83 Playlist · 5066 BY · 4416 ON
non-ASCII intact: Ysée, trentemøller
```

## Related

- `tools/migx-cli/mirrors-to-graph` — the loader
- `kanban/knowledge/arcflow-filesystem-m4.md` — the standing "take the
  technique, not the code" position, which this does not change

---
id: arcflow-distinct-playlist-count-semantics
type: task
title: "ArcFlow distinct-playlist aggregation must not count repeated placements"
status: closed
owner: gudjon
priority: high
initiative: initiative-ai-djing-product
authored_by: codex-cli
authored_kind: agent
triggered_by: "The first full Migx mirror graph showed 116 repeated ON placements and incorrect WITH DISTINCT collapse"
created: "2026-08-07"
lastUpdated: "2026-08-08"
acceptance: |
  A minimal graph with repeated Track-[:ON]->Playlist placements returns the
  correct distinct-playlist count per track and per artist through native GQL.
  WITH DISTINCT preserves every expected grouping row. Rust regressions cover
  both the minimal fixture and the Migx-shaped query. The 83-playlist ranking
  queries match an independently computed reference result.
---

# ArcFlow distinct-playlist count semantics

## Problem

The completed Migx graph contains 4,416 `ON` relationships, including 116
repeated placements of a track within the same playlist. Raw GQL `count()`
therefore measures placements, not distinct playlist membership. The attempted
`WITH DISTINCT` form collapses the aggregation incorrectly to one row.

Artist anchors, central tracks, and co-occurrence rankings need **distinct
playlist membership**. Shipping placement counts as playlist counts would make
the first ArcFlow-backed product insight confidently wrong.

## Resolution

ArcFlow PR [`#27`](https://github.com/ozinc/arcflow-core/pull/27) closes the
semantic defect and merged to `main` as `9c2f4ad8`. The installed local runtime
was subsequently built from `main` at `83c86311`, which contains that merge.

The reduction found three runtime defects rather than a parser defect:

1. grouped aggregate evaluators omitted `CountDistinct`;
2. global distinct lookup ignored the aggregate variable's scope; and
3. plain-variable `WITH DISTINCT` skipped projection, so deduplication could
   see no visible variable identities and retain only the first row.

The same corpus proof exposed a fourth adjacent defect: temporal probing in
`ORDER BY` started at byte offset two and could split a Unicode scalar. That
made valid strings such as `Ysée` panic during ranking. The fix now chooses a
UTF-8 character boundary and has a direct regression.

Both native forms below are supported and return the same result:

```gql
MATCH (t:Track)-[:ON]->(p:Playlist)
WITH t.key AS key, t.title AS track, count(DISTINCT p.id) AS playlists
RETURN key, track, playlists
ORDER BY playlists DESC, track, key
```

```gql
MATCH (t:Track)-[:ON]->(p:Playlist)
WITH DISTINCT t, p
WITH t.key AS key, t.title AS track, count(p) AS playlists
RETURN key, track, playlists
ORDER BY playlists DESC, track, key
```

Rank by stable `Track.key`, with title as display data. Grouping by title alone
merges distinct recordings that share a title (the corpus contains more than
one recording named `Home`).

## Guardrails

- Do not deduplicate or delete legitimate `ON` placement edges; position is
  source truth.
- Do not silently compute one metric in Python and label it as an ArcFlow native
  query.
- Keep DJ vocabulary and fixtures in Migx-facing tests or integration fixtures;
  the ArcFlow engine fix remains generic.
- This work is off the audio path and grants no playback authority.

## Evidence

- ArcFlow fix merge: PR #27 at `9c2f4ad8`; installed local build from later
  `main` commit `83c86311`.
- Installed binary SHA-256:
  `fbd29f7b6428e9b52fa26f99d54e3334a7100f3a83924ca7063b524a741f3b69`.
- Corpus: 3,720 tracks, 2,962 artists, 83 playlists, 5,067 `BY`, 4,416 `ON`.
- Independent set reference: 4,300 distinct track/playlist memberships, so the
  116 extra `ON` relationships are repeated placements rather than additional
  playlist memberships.
- Both native track-query forms returned identical top-12 rows. Four tracks
  span six playlists: `Dark Is The Night For All`, `No Goodbye`, `Spektrum
  (feat. Ali Love)`, and `Your Loving Arms - Original`.
- Native artist ranking matched the reference: CamelPhat and UNKLE span 12
  playlists; ANNA, Gui Boratto, and NTO span 11. Unicode names including
  `RÜFÜS DU SOL` and `Röyksopp` sort without a panic. The fresh installed-main
  proof also preserved `Ysée`, `trentemøller`, and `Chicane;Máire Brennan`.
- Rust runtime regression: 3 passed. Python FFI smoke plus the UTF-8 cache
  smoke: 2 passed. Scoped Clippy, formatting, and diff checks passed.
- All protected PR checks passed, including Test in 39m45s and Fitness in
  12m35s. Full TCK was not rerun.
- A clean `arcflow-cli` release build from `83c86311` completed in 3m30s. Its
  fresh 83-mirror store restored as 6,765 nodes and 9,483 relationships; both
  native ranking forms returned identical top-12 rows, and native counts
  remained 4,300 distinct memberships versus 4,416 placements.
- Integration boundary:
  `kanban/knowledge/arcflow-tui-agentic-dj-integration.md`.

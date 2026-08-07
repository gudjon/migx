---
id: arcflow-distinct-playlist-count-semantics
type: task
title: "ArcFlow distinct-playlist aggregation must not count repeated placements"
status: open
owner: gudjon
priority: high
initiative: initiative-ai-djing-product
authored_by: codex-cli
authored_kind: agent
triggered_by: "The first full Migx mirror graph showed 116 repeated ON placements and incorrect WITH DISTINCT collapse"
created: "2026-08-07"
lastUpdated: "2026-08-07"
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

## Required work

1. Reduce the failure to the smallest ArcFlow graph with two grouping keys, a
   duplicate relationship, and more than one expected output row.
2. Determine whether the defect is parsing, logical planning, row binding,
   aggregation, or `WITH DISTINCT` execution before changing the evaluator.
3. Add a Rust regression at the owning layer and an end-to-end GQL query test.
4. Compare the full Migx results with an independent set-based reference
   implementation.
5. Document the supported native query form and only then save rankings for the
   TUI/agent surface.

## Guardrails

- Do not deduplicate or delete legitimate `ON` placement edges; position is
  source truth.
- Do not silently compute one metric in Python and label it as an ArcFlow native
  query.
- Keep DJ vocabulary and fixtures in Migx-facing tests or integration fixtures;
  the ArcFlow engine fix remains generic.
- This work is off the audio path and grants no playback authority.

## Evidence

- Patched ArcFlow branch: `codex/arcflow-utf8-graph-load-fixes` at `deba9443`.
- Corpus: 3,720 tracks, 2,962 artists, 83 playlists, 5,067 `BY`, 4,416 `ON`.
- Integration boundary:
  `kanban/knowledge/arcflow-tui-agentic-dj-integration.md`.

---
id: dossier-FSL-filesystem-sidecar-spike
slug: 2026-07-17-antigravity-cli-FSL--filesystem-sidecar-spike
type: dossier
prefix: FSL
title: "Filesystem sidecar spike — additive DB→Song.migx/ export"
classification: A
phase: sealed
sealed: true
status_note: "FSL sealed: additive TrackDAO sidecar export is verified, only-on-change hardened, and now carries optional cues + waveform energy. EXO/analyzer successors own interpretation."
completion-criteria:
  - "TrackDAO writes an additive per-track sidecar (Song.migx/track.json) on save, without removing the DB."
  - "Builds arm64 + library/track/dao tests pass (no regression)."
  - "Sidecar is greppable/agent-legible and matches the filesystem-driven-architecture sidecar-as-SSoT plan."
facilitator: gudjon
current_dri: codex-cli
initiative: initiative-experience-ontology
authored_by: antigravity-cli
authored_kind: agent
triggered_by: "claude-code->antigravity-cli-001 federation handoff; Antigravity implemented, Claude verified + landed after Antigravity went offline"
created: "2026-07-17"
lastUpdated: "2026-07-18"
last_audited: "2026-07-18"
---

# Filesystem sidecar spike (FSL) — agent routing

Current DRI at seal: `codex-cli`. Historical authorship stays `antigravity-cli` because the dossier was
scaffolded before Antigravity was paused.

The additive **DB → per-track sidecar** first slice that unblocks EXO (the experience ontology needs a
greppable, agent-legible per-track home). Design SSoT: `kanban/knowledge/filesystem-driven-architecture.md`
(sidecar-as-SSoT, DB-as-rebuildable-index).

## What landed
`TrackDAO::saveTrack()` now also calls `exportToSidecar()`, writing `<track-location>.migx/track.json`
with bpm / key / replaygain / peak, plus optional `cues[]` and a coarse waveform-derived
`energy_curve` when those Track facts exist. Additive — the SQLite DB is retained. Verified by
arm64 `mixxx-test`, focused TrackDAO tests, EXO bridge tests, and sidecar smoke.

## Routing by intent
| You want to… | Go to |
|---|---|
| The design (sidecar-as-SSoT) | `kanban/knowledge/filesystem-driven-architecture.md` |
| The checkable spec | `00-FOUNDATION/PS-FSL-01.md` |
| The chosen design | `02-ARCHITECTURE/00-ARCHITECTURE.md` |
| Score / seal | `91-LOOP-CLOSURE/00-LOOP-CLOSURE.md` |

## Follow-on
- EXO owns sidecar -> ontology/session prep interpretation.
- Analyzer/EXO successor work owns sections, richer energy/structure, graph derivation, and backfill policy.

## The closed loop (MG-1)
Trigger: a track save. Capture: `<track>.migx/track.json`. Intelligence: the sidecar is the agent-legible
per-track surface EXO reads. Adjustment: future loops can move DB-as-index authority once backfill and
rebuild policy exist.

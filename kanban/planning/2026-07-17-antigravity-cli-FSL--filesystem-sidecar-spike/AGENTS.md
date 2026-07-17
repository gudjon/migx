---
id: dossier-FSL-filesystem-sidecar-spike
slug: 2026-07-17-antigravity-cli-FSL--filesystem-sidecar-spike
type: dossier
prefix: FSL
title: "Filesystem sidecar spike — additive DB→Song.migx/ export"
classification: A
phase: execution
sealed: false
status_note: "Wave-1 slice landed + verified: TrackDAO::saveTrack() exports <track>.migx/track.json (bpm/key/replaygain). Builds, 95 library tests pass. Follow-on: gate export to only-on-change."
completion-criteria:
  - "TrackDAO writes an additive per-track sidecar (Song.migx/track.json) on save, without removing the DB."
  - "Builds arm64 + library/track/dao tests pass (no regression)."
  - "Sidecar is greppable/agent-legible and matches the filesystem-driven-architecture sidecar-as-SSoT plan."
facilitator: gudjon
current_dri: claude-code
initiative: initiative-experience-ontology
authored_by: antigravity-cli
authored_kind: agent
triggered_by: "claude-code->antigravity-cli-001 federation handoff; Antigravity implemented, Claude verified + landed after Antigravity went offline"
created: "2026-07-17"
lastUpdated: "2026-07-17"
last_audited: "2026-07-17"
---

# Filesystem sidecar spike (FSL) — agent routing

Current DRI: `claude-code`. Historical authorship stays `antigravity-cli` because the dossier was
scaffolded before Antigravity was paused.

The additive **DB → per-track sidecar** first slice that unblocks EXO (the experience ontology needs a
greppable, agent-legible per-track home). Design SSoT: `kanban/knowledge/filesystem-driven-architecture.md`
(sidecar-as-SSoT, DB-as-rebuildable-index).

## What landed (verified, commit 66ed81d)
`TrackDAO::saveTrack()` now also calls `exportToSidecar()`, writing `<track-location>.migx/track.json`
with bpm / key / replaygain / peak. Additive — the SQLite DB is retained. Verified: applies cleanly,
mixxx-lib+mixxx-test build arm64, **95/95 library/track/dao tests pass**.

## Routing by intent
| You want to… | Go to |
|---|---|
| The design (sidecar-as-SSoT) | `kanban/knowledge/filesystem-driven-architecture.md` |
| The checkable spec | `00-FOUNDATION/PS-FSL-01.md` |
| The chosen design | `02-ARCHITECTURE/00-ARCHITECTURE.md` |
| Score / seal | `91-LOOP-CLOSURE/00-LOOP-CLOSURE.md` |

## Follow-on (before seal)
- Export currently fires on **every** `saveTrack()` — gate it to only-on-change (avoid redundant file I/O).
- Extend the sidecar with the EXO `ontology.json` (sections/energy/graph) once the analyzers exist.
- Error handling: `exportToSidecar` silently returns on open failure — add a classified log (`P-34`).

## The closed loop (MG-1)
Trigger: a track save. Capture: `<track>.migx/track.json`. Intelligence: the sidecar is the agent-legible
per-track SSoT EXO reads. Adjustment: the DB becomes a rebuildable index; the sidecar is canonical.

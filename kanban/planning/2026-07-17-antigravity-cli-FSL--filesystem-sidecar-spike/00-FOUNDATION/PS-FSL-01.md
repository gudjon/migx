---
id: PS-FSL-01
type: problem-statement
title: "Track metadata has no greppable, agent-legible per-track home on disk"
status: resolved
severity: SHOULD
ears_class: event-driven
dossier: 2026-07-17-antigravity-cli-FSL--filesystem-sidecar-spike
prefix: FSL
resolves: [P-07, P-34]
risks: [AP-16]
related: []
acceptance:
  - "On TrackDAO::saveTrack(), an additive <track>.migx/track.json sidecar is written with bpm/key/replaygain, without removing the SQLite DB; mixxx-lib+mixxx-test build arm64 and library/track/dao tests pass (95/95 confirmed)."
verified_against_code: "2026-07-17 (commit 66ed81d) — src/library/dao/trackdao.cpp exportToSidecar()"
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# PS-FSL-01 — no per-track agent-legible metadata home

**EARS (event-driven):**
> When a track is saved (`TrackDAO::saveTrack`), the system shall write an additive, human/agent-readable
> per-track sidecar (`<track>.migx/track.json`) capturing its musical metadata, without removing the DB.

## Context
Mixxx keeps track metadata in one central `mixxxdb.sqlite` — opaque and not greppable/agent-writable. The
EXO experience ontology needs a per-track, agent-legible home. This PS is the first additive slice toward
the sidecar-as-SSoT model (`kanban/knowledge/filesystem-driven-architecture.md`); the DB is retained as a
rebuildable index during migration.

## Acceptance contract
Implemented at `src/library/dao/trackdao.cpp` (`exportToSidecar()`), called from `saveTrack()`. Writes
`<location>.migx/track.json` (bpm/key/replaygain/peak). Verified: builds arm64, 95/95 library tests pass.

## Out of scope
The full EXO `ontology.json` (sections/energy/graph); only-on-change gating; DB→sidecar back-fill of the
existing library. Those are follow-ons (see the dossier card).

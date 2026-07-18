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
  - "On TrackDAO::saveTrack(), an additive <track>.migx/track.json sidecar is written with bpm/key/replaygain/peak plus optional cues and waveform energy when available, without removing the SQLite DB; mixxx-lib+mixxx-test build arm64 and focused TrackDAO/EXO bridge tests pass."
verified_against_code: "2026-07-18 — src/library/dao/trackdao.cpp exportToSidecar()"
created: "2026-07-17"
lastUpdated: "2026-07-18"
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
`<location>.migx/track.json` (bpm/key/replaygain/peak, plus `cues[]` and waveform `energy_curve` when
available). Verified: builds arm64, focused TrackDAO tests pass, and EXO sidecar bridge tests pass.

## Out of scope
The full EXO `ontology.json` (sections/phrases/graph); DB→sidecar back-fill of the existing library.
Those are follow-ons (see the dossier card and EXO/analyzer tasks).

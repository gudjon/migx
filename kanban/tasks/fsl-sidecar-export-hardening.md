---
id: fsl-sidecar-export-hardening
type: task
title: "Harden FSL sidecar export before dossier seal"
status: done
owner: codex-cli
priority: high
initiative: initiative-experience-ontology
parent_dossier: 2026-07-17-antigravity-cli-FSL--filesystem-sidecar-spike
depends_on: [absorb-antigravity-product-lane]
authored_by: codex-cli
authored_kind: agent
triggered_by: "Antigravity pause pickup; FSL Wave 1 landed with follow-ons before seal"
created: "2026-07-17"
lastUpdated: "2026-07-18"
acceptance: |
  TrackDAO sidecar export does not rewrite unchanged sidecars on every save; export/open failures
  produce classified logging; focused library/dao checks pass; sidecar now carries real cues and
  coarse waveform energy when available; FSL closure seals with analyzer/ontology successor work named.
---

# Harden FSL Sidecar Export

Current state: FSL Wave 1 records an additive `<track-location>.migx/track.json` export from
`TrackDAO::saveTrack()`. A Codex source pass is present in the current tree: `exportToSidecar()`
skips unchanged sidecars, logs directory/read/open/write/commit failures, and writes through
`QSaveFile`. The 2026-07-18 Codex pass extends the same additive export with optional `cues[]`
and coarse waveform `energy_curve` fields, plus focused C++ and EXO bridge coverage.

## Required

1. [x] Gate export to only-on-change or content-diff so repeated `saveTrack()` calls do not cause redundant
   file I/O.
2. [x] Add classified logging for sidecar directory/open/write failure (`P-34`).
3. [x] Run focused library/dao checks and record commands in the FSL JOURNAL.
4. [x] Update `91-LOOP-CLOSURE` honestly: seal only if the hardening gate is green, otherwise name the
   successor.

## Boundaries

- Do not flip DB-vs-sidecar SSoT authority in this task.
- Do not add AnalyzerStructure/Energy production DSP here.
- Do not touch RT audio callback paths.

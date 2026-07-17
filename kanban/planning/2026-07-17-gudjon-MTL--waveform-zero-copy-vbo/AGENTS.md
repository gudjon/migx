---
id: dossier-MTL-waveform-zero-copy-vbo
slug: 2026-07-17-gudjon-MTL--waveform-zero-copy-vbo
type: dossier
prefix: MTL
title: "Persistent VBO for the waveform GL backend — kill the per-draw CPU→GPU vertex copy"
classification: A          # agent-scaffolded
phase: execution           # scaffold | foundation | research | architecture | execution | sealed
sealed: false              # true only after 91-LOOP-CLOSURE is scored
status_note: "Implemented + built green + 165/165 render/engine tests pass. VBO measured to eliminate a ~450KB/~6.5us-floor per-frame upload on unchanged frames (EVD-0002, cocoa GL). CPU rebuild unchanged vs EVD-0001. MERGEABLE-PENDING-GUI: visual correctness + end-to-end frame time need human GUI verification. Not committed (facilitator reviews)."
completion-criteria:
  - "rendergraph_gl BaseGeometryNode draws from a persistent VBO; unchanged frame does zero CPU→GPU upload."
  - "Eliminated per-frame upload cost measured > 0 vs EVD-0001 (EVD-0002)."
  - "ctest -R 'Waveform|Engine' 100% green; BM_Waveform CPU rebuild unchanged vs EVD-0001."
  - "Human GUI verification of visual correctness before merge (flagged, not yet done)."
facilitator: gudjon
initiative: initiative-apple-silicon
authored_by: claude-code
authored_kind: mixed
triggered_by: "baseline dossier 2026-07-17-gudjon-MTL--waveform-render-baseline sealed with EVD-0001 + COPY-MAP; this is the FIRST optimization it feeds — copy-map lever 1 (VBO)"
created: "2026-07-17"
lastUpdated: "2026-07-17"
last_audited: "2026-07-17"
---

# Persistent VBO for the waveform GL backend — agent routing

The card above is this dossier's identity. Below is routing-by-intent for an agent entering here.

## Routing by intent

| You want to… | Go to |
|---|---|
| Understand why this bet exists | `00-FOUNDATION/PROBLEM.md` |
| See the checkable spec | `00-FOUNDATION/PS-MTL-02.md` (EARS + `acceptance:`) |
| See the measured before/after | `results/EVD-0002.md` (vs baseline `EVD-0001`) |
| See the ordered plan + gates | `90-EXECUTION/00-PHASE-PLAN.md` |
| Score / seal the bet | `91-LOOP-CLOSURE/00-LOOP-CLOSURE.md` |
| Catch up on what happened | `JOURNAL.md` |

## The closed loop this dossier is (MG-1)
- **Trigger** — the baseline dossier's `COPY-MAP.md` named the per-draw client-memory vertex bind
  (`basegeometrynode.cpp:89-102`) as the headline `P-22`/`AP-12` copy site.
- **Capture** — `PS-MTL-02` acceptance + `EVD-0001` baseline (~39µs CPU rebuild feeding a ~450 KB/frame
  client-array copy).
- **Intelligence** — `EVD-0002`: unchanged frame → zero upload; the eliminated upload is ~6.5µs floor /
  450 KB / deck; CPU rebuild unchanged; 165/165 tests green.
- **Adjustment** — the persistent-VBO change in `src/rendergraph/opengl/backend/` (in working tree,
  awaiting GUI verification + facilitator commit).

## Owning contexts
`arch-rendergraph` (src/rendergraph/) + `arch-waveform-render` (src/waveform/). Render thread only —
GPU work stays off the audio deadline (`P-21`/`P-23`); the RT audio path is untouched (`P-02`).

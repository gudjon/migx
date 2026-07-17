---
id: dossier-MTL-waveform-render-baseline
slug: 2026-07-17-gudjon-MTL--waveform-render-baseline
type: dossier
prefix: MTL
title: "Baseline the waveform render path on Apple Silicon (M4)"
classification: none
phase: sealed
sealed: true
status_note: "Execution COMPLETE — Waves 1-4 done: baseline EVD-0001 captured+verified (~34-39us RGB floor), copy-map written. Ready to seal at 91-LOOP-CLOSURE. Next: MTL optimization dossier (zero-copy VBOs, EVD-0001 to beat)."
completion-criteria:
  - "A pinned baseline benchmark of the waveform render path on M4, recorded as an EVD-* with the core config."
  - "The current GPU/CPU data path documented: does Qt RHI select Metal on macOS? where are per-frame copies?"
  - "p99/max frame time + any dropped frames captured under realistic load (a loaded, scrubbing deck)."
facilitator: gudjon
initiative: initiative-apple-silicon
authored_by: claude-code
authored_kind: mixed
triggered_by: "harness dogfood + initiative-apple-silicon — the MTL workstream needs a baseline before any optimization"
created: "2026-07-17"
lastUpdated: "2026-07-17"
last_audited: "2026-07-17"
---

# Baseline the waveform render path on M4 — agent routing

The card above is this dossier's identity. This is the **recommended first dossier** of
`initiative-apple-silicon`: baseline-only, so later MTL optimization dossiers have a number to beat.

## Routing by intent

| You want to… | Go to |
|---|---|
| Understand why this bet exists | `00-FOUNDATION/PROBLEM.md` |
| See the checkable spec | `00-FOUNDATION/PS-MTL-01.md` (EARS + `acceptance:`) |
| See prior art / upstream scan (Qt RHI/Metal) | `01-RESEARCH/00-RESEARCH.md` |
| See the measurement design | `02-ARCHITECTURE/00-ARCHITECTURE.md` |
| See the ordered plan + gates | `90-EXECUTION/00-PHASE-PLAN.md` |
| Score / seal the bet | `91-LOOP-CLOSURE/00-LOOP-CLOSURE.md` |

## The closed loop this dossier is (MG-1)
- **Trigger** — the M4 optimization initiative needs a baseline before any waveform work.
- **Capture** — an `EVD-*` record: waveform render p99/max frame time + dropped-frame count on M4, pinned to a commit.
- **Intelligence** — the baseline number + a map of where CPU/GPU copies happen on the render path.
- **Adjustment** — this baseline becomes the reference every later MTL optimization dossier measures its delta against.

## Owning contexts
`arch-waveform-render` (src/waveform/) + `arch-rendergraph` (src/rendergraph/, src/shaders/). Respects
the render/RT boundary: waveform renders on the display clock, never the audio clock (`P-23`); the audio
thread never waits on the GPU (`P-21`/`AP-12`).

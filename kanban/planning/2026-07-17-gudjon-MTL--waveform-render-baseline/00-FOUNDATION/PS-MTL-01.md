---
id: PS-MTL-01
type: problem-statement
title: "No pinned baseline for the M4 waveform render frame-time distribution"
status: open
severity: MUST
ears_class: event-driven
dossier: 2026-07-17-gudjon-MTL--waveform-render-baseline
prefix: MTL
resolves: [P-03, P-18, P-25]
risks: [AP-09, AP-12]
related: []
acceptance:
  - "A repeatable waveform-render benchmark exists (in the GoogleTest/benchmark tree) that reports p50, p99, and max frame time plus a dropped-frame count, run on this M4 under a realistic scene (a loaded, scrubbing deck)."
  - "The baseline result is recorded as an EVD-0001 in results/ with: the commit SHA it was measured at, the M4 core config (P/E core counts), the Qt version, and whether the RHI backend in use is Metal."
  - "The render-path data journey is documented: where sample/texture data lives across frames and every point a CPU<->GPU copy occurs (the input a future zero-copy dossier needs)."
verified_against_code: "2026-07-17 — src/waveform/ and src/rendergraph/ listed at HEAD; concrete renderer class TBD in RESEARCH"
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# PS-MTL-01 — No pinned baseline for the M4 waveform render frame-time distribution

**EARS statement (event-driven):**
> When the waveform render path is exercised under a realistic scrubbing scene on an M4, the harness
> shall record its frame-time distribution (p50/p99/max) and dropped-frame count as a commit-pinned
> baseline that later optimizations measure their delta against.

## Context
The render path lives in `src/waveform/` (renderers, `WaveformWidgetFactory`) and
`src/rendergraph/`+`src/shaders/` (the Qt RHI scene-graph substrate). On macOS Qt6 RHI *may* already
select Metal — confirming that is part of RESEARCH. The waveform tap from the engine is the lock-free
`ControlValueAtomic<VisualPlayPositionData>` in `src/waveform/visualplayposition.h` (do not disturb it;
`P-16`). This PS measures; it does not change the path.

## Acceptance contract (how the loop closes)
- **Benchmark:** a new case in the benchmark tree driving the waveform renderer over N frames of a
  scrubbing scene; run via the `mixxx-test`/benchmark binary. Report p50/p99/max + dropped frames.
- **Baseline:** `results/EVD-0001` — the numbers + commit SHA + M4 core config + Qt version + RHI
  backend (Metal?). Pinned (`P-25`); future deltas measure against it, never a moving `main` (`AP-09`).
- **Threshold:** this is a baseline dossier — the "threshold" is *reproducibility*: two runs of the
  benchmark on the same commit agree within a stated tolerance, so the number is trustworthy.
- **Guard:** the measurement must not itself introduce a per-frame CPU↔GPU round-trip (`AP-12`) or
  couple render to the audio clock (`P-23`).

## Out of scope
Any change that makes it faster (Metal offload, zero-copy buffers, shader rework) — those are separate
MTL/optimization dossiers that consume this baseline.

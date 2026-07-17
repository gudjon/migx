---
id: signal-2026-07-17-dsp-iir-accelerate-field-notes
type: signal-brief
from: grok-signal
date: "2026-07-17"
relevance: actionable
topics: [dsp, accelerate, neon, iir, rt-audio, apple-silicon]
mapped_to:
  - PS-DSP-01
  - kanban/planning/2026-07-17-gudjon-DSP--iir-eq-filter-simd/
  - initiative-apple-silicon
  - P-02
sources:
  - "Apple Accelerate / vDSP docs (biquad, vDSP_deq22 legacy, BNNS when applicable)"
  - "X field: NEON denormal flush-by-default vs x86 FTZ/DAZ (audio IIR stability, 2026-07)"
  - "EVD-DSP-01 / enginefilterbenchmark on main @ e3b622a"
---

# Signal — DSP Wave 2 field notes (IIR · Accelerate · RT)

For **Claude** while implementing PS-DSP-01 Wave 2. Grok is **not** claiming the engine lane.

## Context
Wave 1 baseline is on `main` (`e3b622a`): headless `BM_EngineFilter*` + EVD-DSP-01. Target is
scalar `EngineFilterIIR::process()` steady-state (`enginefilteriir.h` ~239–244), biquad peaking
SIZE=5 and Butterworth8 SIZE=8, **zero alloc/lock**, numeric epsilon vs scalar.

## Field notes worth using

1. **Denormals** — Audio IIR tails hit denormal penalty on x86 unless FTZ/DAZ; **NEON typically flushes
   denormals by default**. On M4 still verify: no surprise soft-float path; optional tiny DC offset
   policy only if measurable. Keep measurement in the same bench harness (p99).

2. **Stereo deinterleave** — Current path processes L/R via `m_buf1`/`m_buf2` scalar. A vDSP/NEON
   form often wants **SoA** (planar) or interleaved SIMD lanes carefully; do **not** allocate
   temporary planar buffers on the callback — pre-allocate at setCoefs/construction (`P-02`/`P-17`).

3. **vDSP biquad family** — Prefer documented Accelerate biquad/cascade APIs over inventing a
   partial NEON unroll that fails SIZE=8 specialization parity. If vDSP batch needs block size
   alignment, match Mixxx buffer sizes (1024 frames) already in the bench.

4. **House physics** — Faster p99 that changes sound is a **regression** (`AP-02`). Wave 2 acceptance
   already states epsilon + ctest Engine|Effects.

5. **Out of Grok scope** — No engine edits from grok-signal; send `research-request` if you want a
   deeper Apple-doc / paper sweep on a specific vDSP entry point.

## Suggested Claude actions
1. Keep claiming DSP dossier only; leave federation signal path free.
2. After SIMD draft: run `mixxx-test --benchmark --benchmark_filter=BM_EngineFilter` vs EVD-DSP-01.
3. If blocked on API choice (vDSP vs hand NEON), open `research-request` → `grok-signal`.

## Handoff budget
This brief is **actionable support**, not a second implementer.

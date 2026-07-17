---
id: PS-DSP-01
type: problem-statement
title: "No pinned baseline for the scalar EngineFilterIIR EQ hot loop on M4, and no SIMD path"
status: open
severity: MUST
ears_class: event-driven
dossier: 2026-07-17-gudjon-DSP--iir-eq-filter-simd
prefix: DSP
resolves: [P-02, P-03, P-16, P-18, P-25]
risks: [AP-02, AP-11]
related: []
acceptance:
  - "Wave 1: a headless benchmark (GoogleTest/benchmark tree, no GL/GPU context) drives EngineFilterIIR<SIZE,PASS>::process() (src/engine/filters/enginefilteriir.h:239) over 1024-frame, 44.1kHz interleaved-stereo buffers for at least one biquad instantiation (EngineFilterBiquad1Peaking, src/engine/filters/enginefilterbiquad1.h:27, SIZE=5) and at least one higher-order instantiation (EngineFilterBessel8Low or EngineFilterButterworth8Low, SIZE=8), reporting p50/p90/p99/max time per buffer, run with fixed Iterations for reproducibility (two runs agree within a stated tolerance)."
  - "The Wave 1 result is recorded as EVD-DSP-01 in results/ with: commit SHA, M4 core config (P/E core counts), macOS + Qt build info, and confirmation the build is arm64-native (P-24)."
  - "Wave 2: a NEON/Accelerate(vDSP) rewrite of the steady-state (!m_doRamping) branch of process() does not regress p99 vs EVD-DSP-01 for either instantiation benchmarked in Wave 1, and every rewritten sample matches the scalar processSample() output within a stated numerical tolerance (e.g. 1e-6 relative, measured over a swept-frequency + impulse test signal) — a faster filter that changes the sound is a regression, not a win."
  - "Wave 2/3: the SIMD path adds zero allocation and zero locks to process() (P-02) — any NEON/vDSP scratch state is constructed once, at EngineFilterIIR construction/setCoefs time, never on the per-buffer call — and ctest --test-dir build -R 'Engine|Effects' stays green."
verified_against_code: "2026-07-17 — src/engine/filters/enginefilteriir.h opened at HEAD (deda627b1b)"
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# PS-DSP-01 — No pinned baseline for the scalar EngineFilterIIR EQ hot loop on M4, and no SIMD path

**EARS statement (event-driven):**
> When an EQ effect is active on a deck, the `EngineFilterIIR::process()` steady-state path shall have
> its per-buffer time distribution (p50/p90/p99/max) captured as a commit-pinned, headless baseline on
> M4, and a NEON/Accelerate(vDSP) replacement shall not regress that p99 while staying allocation-free
> and numerically equivalent within a stated tolerance.

## Context
`EngineFilterIIR<SIZE, PASS>::process()` (`src/engine/filters/enginefilteriir.h:239-244`) is the
scalar hot loop `initiative-apple-silicon`'s DSP row names: in the steady-state branch it calls
`processSample(m_coef, m_buf1, pIn[i])` / `processSample(m_coef, m_buf2, pIn[i + 1])` per stereo sample
pair — a scalar per-sample IIR difference equation, deinterleaved stereo (`m_buf1` = left, `m_buf2` =
right). `processSample` is declared as a member at `src/engine/filters/enginefilteriir.h:294` and has no generic body; it
is explicitly specialized per `(SIZE, PASS)` filter order/topology further down the same header (e.g.
the `SIZE=4, IIR_LP` specialization at `src/engine/filters/enginefilteriir.h:368`, the `SIZE=8, IIR_LP` specialization at
`src/engine/filters/enginefilteriir.h:436`, the `SIZE=5, IIR_BP` — the biquad peaking/shelving form — at
`src/engine/filters/enginefilteriir.h:549`). Every specialization runs entirely scalar, per-sample, with a serial
data dependency through `buf[]` (each stage's output feeds the next), which is exactly the shape SIMD
lane-parallelism does not trivially help *within one channel* but Accelerate/vDSP's biquad cascade
primitives (`vDSP_biquad`) or a NEON-parallelized L/R pair are built for.

This runs on **every audio buffer for every deck with an EQ effect enabled** — concrete instantiations
are template specializations of the same class:
- `EngineFilterBiquad1Peaking : EngineFilterIIR<5, IIR_BP>` (`src/engine/filters/enginefilterbiquad1.h:27`),
  used by the parametric EQ (`src/effects/backends/builtin/parametriceqeffect.h:9,28`), the graphic EQ
  (`src/effects/backends/builtin/graphiceqeffect.h:10,21`), and the Full Kill EQ boost bands
  (`src/effects/backends/builtin/biquadfullkilleqeffect.h:9,24`).
- `EngineFilterBiquad1Low` / `EngineFilterBiquad1High : EngineFilterIIR<2, IIR_LP/IIR_HP>`
  (`src/engine/filters/enginefilterbiquad1.h:54,77`), used by the Filter effect
  (`src/effects/backends/builtin/filtereffect.h:8-9,18-19`).
- `EngineFilterBessel4Low/Band/High : EngineFilterIIR<4|8, ...>`
  (`src/engine/filters/enginefilterbessel4.h:6,18,29`) and `EngineFilterBessel8Low/Band/High`
  (`src/engine/filters/enginefilterbessel8.h:6,18,29`), used by the Full Kill EQ's LV-mix isolator band
  (`src/effects/backends/builtin/biquadfullkilleqeffect.h:8,29`).
- `EngineFilterButterworth4*` / `EngineFilterButterworth8*`
  (`src/engine/filters/enginefilterbutterworth4.h:6,13,24`,
  `src/engine/filters/enginefilterbutterworth8.h:6,13,24`) — the crossfade/EQ isolator family.

This dossier only measures and (Wave 2+) speeds up `process()`'s steady-state math; it does not touch
the ramping/crossfade branch (`src/engine/filters/enginefilteriir.h:245-291`), the fidlib coefficient design path
(`setCoefs`/`setCoefs2`), or which filters an effect chooses.

## Acceptance contract (how the loop closes)
- **Benchmark / test:** a new `BM_EngineFilterIIR*` case in the `mixxx-test`/benchmark tree, mirroring
  the house style of `src/test/waveformrenderbenchmark.cpp` (fixed `Iterations`, `benchmark::DoNotOptimize`
  on the output buffer, per-buffer p50/p90/p99/max counters + a `SetLabel` summary). Unlike the MTL
  waveform bench, this needs **no offscreen GL surface at all** — `EngineFilterIIR::process()` touches
  only CPU memory, so the full p50..max distribution is captured headlessly in one pass, with no
  GUI/hardware-dependent skip path.
- **Baseline:** `results/EVD-DSP-01` — the scalar numbers + commit SHA + M4 core config (P/E core
  counts) + confirmation of an arm64-native build (`P-24`), pinned per `P-25` (deltas measure against
  this fixed record, never a moving `main`, `AP-09`).
- **Threshold:** Wave 2's SIMD path must not regress p99 vs `EVD-DSP-01` (a "faster on average, worse
  tail" result is a fail — mean-hiding-the-tail is exactly `AP-11`), and its output must match the
  scalar path within a stated numerical tolerance over a swept-frequency test signal (bit-accuracy
  gate — a filter that sounds different is a regression regardless of speed).
- **Guard:** no allocation or lock added to `process()` (`P-02`/`AP-02`) — SIMD/vDSP scratch state is
  set up once at construction/`setCoefs` time, not per buffer; `ctest --test-dir build -R 'Engine|Effects'`
  green through every wave.

## Out of scope
The ramping/crossfade branch of `process()` (lines 245-291); the fidlib coefficient-design path
(`setCoefs`/`setCoefs2`); any change to which filter topology an effect uses; the resampling/analysis
DSP paths `initiative-apple-silicon`'s DSP row also names (separate future `DSP` dossiers, once this
one lands and its pattern can be reused).

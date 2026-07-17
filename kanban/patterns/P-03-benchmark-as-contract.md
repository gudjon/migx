---
id: P-03
type: pattern
title: "A performance claim needs a benchmark contract"
status: active
severity: MUST
domain: harness
related: [P-01, P-02, AP-02]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-03 — A performance claim needs a benchmark contract

## Statement
When a change claims to make Migx faster, it shall be accompanied by a repeatable benchmark with a
recorded baseline and a numeric threshold; the claim is "done" only when the benchmark closes the
loop against that baseline (MG-1).

## Why
"It feels faster" is not code (MG-2) and cannot be re-checked, so it silently rots. The north-star —
Apple Silicon optimization — is entirely perf work; without a contract per change we can't tell a
real win from noise, can't catch a later regression, and can't score the bet at `91-LOOP-CLOSURE`.
The benchmark *is* the Trigger+Capture of the closed loop.

## How to apply
1. **Baseline first.** Before changing anything, run the benchmark on this hardware (record the M4
   core config) and store the number as an `EVD-*` record in the dossier's `results/`. Pin the commit.
2. **Threshold in the PS.** The `acceptance:` block names the number to beat (e.g. "≥1.5× waveform
   redraw throughput; frame time p99 ≤ 8 ms; zero RT-thread allocations").
3. **Use the existing harness.** Migx links `benchmark::benchmark` and GoogleTest; add benchmarks
   there, run via `ctest`/the benchmark binary. Don't invent a parallel measurement path.
4. **Delta, not absolute.** Always measure the change as a delta against the pinned baseline on the
   same machine — never against a moving `main` (that's the "rehearse on unstable base" breakage).
5. **Guard house physics.** The contract must also assert no regression of `P-02` (no new RT alloc/lock).

## Example — wrong
> "Rewrote the waveform shader in Metal, it's much smoother now." — no baseline, no number, no re-check.

## Example — right
> `EVD-0007`: baseline waveform redraw = 210 fps @ M4 (10-core). Metal path = 380 fps, p99 frame
> 6.1 ms, 0 RT allocations. Contract in `PS-MTL-01` met (≥1.5×). Bench: `mixxx-test --benchmark_filter=Waveform`.

## Detection
- Review: a perf PR without an `EVD-*` baseline and a threshold is incomplete.
- Closure: `91-LOOP-CLOSURE` "Forecast vs actual" must cite the benchmark numbers.

## Cross-references
Serves `P-01`. Guards `P-02` / catches `AP-02`.

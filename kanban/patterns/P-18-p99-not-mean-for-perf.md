---
id: P-18
type: pattern
title: "Performance gates assert the tail, not the mean"
status: active
severity: MUST
domain: engine
related: [P-03, AP-11, AP-02]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-18 — Performance gates assert the tail, not the mean

## Statement
A performance benchmark that gates an audio-path change asserts **tail** behavior — p99 / max buffer
or frame time, and zero underruns — not mean throughput. A mean improvement with a worse tail fails
the gate.

## Why
DJ software is judged on worst-case glitch-free playback. A single dropped buffer is audible; a better
average is not. The mean hides exactly the events that matter — one occasional 20 ms stall inside a
sea of fast buffers averages away but produces the click the user hears. Gating on the tail is what
makes the benchmark contract (`P-03`) actually protect the experience.

## How to apply
- Report and threshold the distribution: p50 *and* p99/max, plus an explicit underrun count that must
  be zero. Use `benchmark::benchmark` (already linked) with enough iterations to populate the tail.
- Measure under realistic load (GPU active, library scanning) — the tail appears under contention, not
  at idle.
- State the threshold in the PS `acceptance:` as a tail number: e.g. "p99 buffer time ≤ 60% of the
  period; 0 underruns over N minutes," not "1.3× average throughput."

## Example — wrong
> "New resampler: +8% average throughput." (mean-only — hides that p99 got worse; `AP-11`)

## Example — right
> "New resampler: p50 −7%, **p99 −22%**, 0 underruns over 10 min under GPU load. Contract met."

## Detection
Review: a perf claim citing only a mean/throughput number; a benchmark with no tail metric or
underrun count.

## Cross-references
Refines `P-03`; the failure it prevents is `AP-11` (mean-hides-the-underrun) and it's the measurement
guard for `AP-02`.

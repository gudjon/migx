---
id: P-14
type: pattern
title: "Prove the candidate beats the current path before you fix"
status: active
severity: MUST
domain: engine
related: [P-03, P-25, P-18, AP-02]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-14 — Prove the candidate beats the current path before you fix

## Statement
Before landing an RT/DSP change (a resampler, a filter, a mixing kernel, a waveform pack), an offline
benchmark on a **real signal** shall demonstrate that the candidate implementation beats the current
path on the metric that motivated it — measured on the same hardware, before the fix is committed.

## Why
"This algorithm should be faster" is a hypothesis, not a result (MG-2). The north-star is Apple
Silicon perf, and the audio/DSP hot paths are where most of the gain (and most of the risk) lives — a
change that looks better on paper can lose to the current path once you count real cache behavior,
denormals, and tail latency. Proving the win *offline, on real audio, before* touching the live engine
keeps the risky work off the RT thread and makes the loop closeable (`P-03`, `P-10`).

## How to apply
- Feed a representative signal (an actual decoded track buffer, not white noise) through both the
  current path and the candidate in an offline harness; compare on the motivating metric.
- Report the **tail**, not the mean (`P-18`): p99/max buffer time and correctness (bit-exact or a
  bounded error), not just average throughput.
- Pin the baseline to a commit + recorded HW (`P-25`); the candidate is a delta against it.
- Only after the offline bench proves the win do you wire the candidate into the engine (`P-10`).

## Example — wrong
> Swapped the resampler in `EngineBuffer` directly on `main`, "it's a better algorithm," and measured
> afterward against a moving tree. No before-number on real audio.

## Example — right
> `EVD-0031`: offline bench, real 44.1k track buffer through old vs new resampler. New: p99 −19%,
> max −24%, error < −140 dBFS. Beats current path on M4 (10-core). Now safe to land behind `P-10`.

## Detection
Review: a DSP/RT PR with no pre-change offline benchmark on real signal, or a bench that only reports a
mean, is incomplete.

## Cross-references
Feeds the contract `P-03`; measures the tail per `P-18`; baseline discipline `P-25`; the safe rollout
is `P-10`. Skipping it is how `AP-02` (speedup that regresses house physics) merges.

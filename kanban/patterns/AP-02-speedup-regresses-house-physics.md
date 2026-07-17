---
id: AP-02
type: antipattern
title: "Speedup that regresses house physics"
status: active
severity: MUST-NOT
domain: engine
related: [P-02, P-03]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-02 — Speedup that regresses house physics

## What it looks like
An optimization improves an average/throughput number but introduces a real-time-safety or
ownership violation: a heap allocation or lock on the audio callback path, a data race on a
`ControlObject`, a Qt object without a valid parent, or GPU work that stalls the audio thread.

## Why it's harmful
DJ software is judged on **worst-case glitch-free playback**, not average throughput. A change that's
5% faster on average but occasionally allocates on the RT thread (`P-02`) trades an inaudible gain
for an audible dropout — a net regression, and a correctness bug, not a perf win. On the
unified-memory M4 SoC it's tempting to share buffers between GPU and audio paths; doing so without
respecting the RT boundary is the classic instance.

## What to do instead
- Keep the RT fast path allocation- and lock-free even while optimizing (`P-02`): set up SIMD/Metal
  state and scratch once, at construction.
- Make the benchmark contract (`P-03`) assert the invariant: zero RT-thread allocations, p99 (not
  mean) frame/buffer time, no new locks on the callback.
- Offload to GPU/other threads via lock-free handoff; never let GPU latency gate the audio deadline.

## Detection
Review + Phase-3 tooling: allocation-counter assertion on the RT path; p99 (tail) metrics in the
benchmark; thread-sanitizer on the engine tests.

## Cross-references
Violates `P-02`; caught by the contract in `P-03`.

---
name: pat-03-benchmark-as-contract
description: "Surface the benchmark-contract rule when a change makes a performance claim or touches a
  perf hot path. Fire when editing a benchmark (benchmark::benchmark, *_benchmark.cpp), a DSP/RT hot
  path under src/engine/, or a waveform/render hot path, or when a PR/PS claims something is faster.
  A perf claim needs a repeatable benchmark with a pinned baseline and a numeric threshold."
disable-model-invocation: false
defers_to:
  - kanban/patterns/P-03-benchmark-as-contract.md
  - kanban/patterns/P-25-pin-the-benchmark-baseline.md
audit_gate: "advisory — knowledge skill; perf-baseline lint in Phase 3"
verifiable_output_shape: "advisory — knowledge skill, no artifact"
metadata:
  cites_patterns: ["P-03", "P-25"]
---

# pat-03 — benchmark as contract

You are making or reviewing a performance claim. Surface
**[`P-03`](../../../kanban/patterns/P-03-benchmark-as-contract.md)** (a perf claim needs a repeatable
benchmark with a recorded baseline and a numeric threshold) and
**[`P-25`](../../../kanban/patterns/P-25-pin-the-benchmark-baseline.md)** (pin the baseline to a
commit + recorded HW; measure deltas against it, never a moving `main`). Record the baseline as an
`EVD-*` before changing anything. Read the cards; don't restate them.

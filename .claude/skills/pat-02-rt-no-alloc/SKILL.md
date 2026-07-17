---
name: pat-02-rt-no-alloc
description: "Surface the real-time audio-safety rule when editing the audio engine. Fire when the
  change touches a process()/callback path under src/engine/ (or src/effects/, src/vinylcontrol/,
  src/soundio/ callbacks), adds a buffer/allocation/lock near audio processing, or claims a perf
  optimization on the audio path. The RT audio thread must not allocate, lock, or block."
disable-model-invocation: false
defers_to:
  - kanban/patterns/P-02-rt-thread-no-alloc.md
  - kanban/patterns/AP-02-speedup-regresses-house-physics.md
  - AGENTS.md
audit_gate: "advisory — knowledge skill; enforcement via engine tests (P-32) in Phase 3"
verifiable_output_shape: "advisory — knowledge skill, no artifact"
metadata:
  cites_patterns: ["P-02", "AP-02"]
---

# pat-02 — real-time audio safety

You are editing a real-time audio path. Surface **[`P-02`](../../../kanban/patterns/P-02-rt-thread-no-alloc.md)**
(never allocate/lock/block on the RT thread) and its failure mode
**[`AP-02`](../../../kanban/patterns/AP-02-speedup-regresses-house-physics.md)** (a speedup that
regresses house physics). Read the cards; don't restate them here. Safe cross-thread patterns: `P-16`,
`P-17`. Measurement guard: `P-18`.

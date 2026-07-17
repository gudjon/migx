---
name: pat-16-lock-free-rt-handoff
description: "Surface the lock-free cross-thread rule when moving data across the audio-thread
  boundary. Fire when the change adds a queue/buffer/mutex between the engine and GUI/worker threads,
  touches util/fifo.h or engineworker*, or hands parameters/objects to the RT thread. GUI↔engine data
  crosses lock-free (ring buffer / atomic double-buffer / ControlObject), never a mutex."
disable-model-invocation: false
defers_to:
  - kanban/patterns/P-16-lock-free-rt-handoff.md
  - kanban/patterns/P-17-object-lifetime-off-the-rt-thread.md
  - kanban/patterns/AP-14-rt-thread-touches-gui-or-blocks.md
audit_gate: "advisory — knowledge skill; ThreadSanitizer on engine tests (P-32) in Phase 3"
verifiable_output_shape: "advisory — knowledge skill, no artifact"
metadata:
  cites_patterns: ["P-16", "P-17", "AP-14"]
---

# pat-16 — lock-free RT handoff

You are moving data across the audio-thread boundary. Surface
**[`P-16`](../../../kanban/patterns/P-16-lock-free-rt-handoff.md)** (SPSC ring / atomic double-buffer /
ControlObject — never a mutex or blocking queued call) and
**[`P-17`](../../../kanban/patterns/P-17-object-lifetime-off-the-rt-thread.md)** (allocate/destroy off
the RT thread). Failure mode: **[`AP-14`](../../../kanban/patterns/AP-14-rt-thread-touches-gui-or-blocks.md)**.
Migx primitive: `util/fifo.h`. Read the cards; don't restate them.

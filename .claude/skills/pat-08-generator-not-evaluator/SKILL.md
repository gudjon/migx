---
name: pat-08-generator-not-evaluator
description: "Surface the generator-is-not-evaluator rule when a change is being reviewed, promoted, or
  declared done — especially an engine/perf/audio-behaviour change. Fire when a session is about to
  mark its own work passing, write or run its own acceptance check, or close a loop without an
  independent verdict. The author of a change does not grade it; an independent evaluator runs the
  frozen contract."
disable-model-invocation: false
defers_to:
  - kanban/patterns/P-08-generator-is-not-evaluator.md
  - kanban/patterns/P-09-evaluation-contract.md
audit_gate: "advisory — knowledge skill; loop-closure review in Phase 3"
verifiable_output_shape: "advisory — knowledge skill, no artifact"
metadata:
  cites_patterns: ["P-08", "P-09"]
---

# pat-08 — generator is not evaluator

You are about to declare a change done or promote it. Surface
**[`P-08`](../../../kanban/patterns/P-08-generator-is-not-evaluator.md)** (the author does not grade
their own change; an independent evaluator returns the verdict) and
**[`P-09`](../../../kanban/patterns/P-09-evaluation-contract.md)** (acceptance criteria are measurable,
runnable, and frozen at creation). Freeze the contract before the work; run the verdict from a context
that didn't write the change. Read the cards; don't restate them.

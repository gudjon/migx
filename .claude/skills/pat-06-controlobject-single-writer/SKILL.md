---
name: pat-06-controlobject-single-writer
description: "Surface the single-writer rule when adding or changing a ControlObject writer. Fire when
  the change calls set() on a ControlObject/ControlProxy, creates a new [Group],key control in
  src/control/ or src/engine/, or wires a controller/QML/skin to write a control. Each [Group],key
  must have exactly one authoritative writer."
disable-model-invocation: false
defers_to:
  - kanban/patterns/P-06-controlobject-single-writer.md
  - kanban/patterns/AP-03-second-writer-on-a-controlobject.md
audit_gate: "advisory — knowledge skill; multi-writer lint in Phase 3"
verifiable_output_shape: "advisory — knowledge skill, no artifact"
metadata:
  cites_patterns: ["P-06", "AP-03"]
---

# pat-06 — ControlObject single writer

You are adding/changing a ControlObject writer. Surface
**[`P-06`](../../../kanban/patterns/P-06-controlobject-single-writer.md)** (one authoritative writer per
`[Group],key`; others read via `ControlProxy`) and its failure mode
**[`AP-03`](../../../kanban/patterns/AP-03-second-writer-on-a-controlobject.md)**. Before adding a
`set()`, grep the key literal across `src/`+`res/` to confirm no other writer. Read the cards; don't
restate them.

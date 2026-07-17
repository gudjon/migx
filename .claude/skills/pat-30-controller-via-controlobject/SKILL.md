---
name: pat-30-controller-via-controlobject
description: "Surface the controller-via-ControlObject rule when editing controller code. Fire when
  touching src/controllers/ (especially scripting/) or res/controllers/ *-scripts.js / *.midi.xml —
  any mapping or script that reaches the engine. Controller JS reaches the engine only via
  ControlObject (engine.setValue/getValue), never blocking RT or touching engine/GUI objects; mappings
  and constants live in data, not hardcoded."
disable-model-invocation: false
defers_to:
  - kanban/patterns/P-30-controller-script-talks-via-controlobject.md
  - kanban/patterns/AP-15-hardcoded-tuning-or-mapping-value.md
audit_gate: "advisory — knowledge skill; controller-boundary review in Phase 3"
verifiable_output_shape: "advisory — knowledge skill, no artifact"
metadata:
  cites_patterns: ["P-30", "AP-15"]
---

# pat-30 — controller via ControlObject

You are editing controller mapping/script code. Surface
**[`P-30`](../../../kanban/patterns/P-30-controller-script-talks-via-controlobject.md)** (controller JS
reaches the engine only through ControlObject on its own thread — never blocks RT, never touches an
engine/GUI object directly) and its failure
**[`AP-15`](../../../kanban/patterns/AP-15-hardcoded-tuning-or-mapping-value.md)** (mapping/tuning
constants hardcoded in C++/JS instead of their `res/controllers/` data home). Respect single-writer
(`P-06`). Read the cards; don't restate them.

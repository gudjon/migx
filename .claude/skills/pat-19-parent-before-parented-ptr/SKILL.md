---
name: pat-19-parent-before-parented-ptr
description: "Surface the Qt ownership rule when using parented_ptr/make_parented or creating QObjects.
  Fire when the change calls make_parented/parented_ptr, constructs a QObject/QWidget, or manages Qt
  object lifetime. A QObject must get a valid parent before its parented_ptr destructs, and the RT
  thread must respect QObject thread affinity."
disable-model-invocation: false
defers_to:
  - kanban/patterns/P-19-parent-before-parented-ptr.md
  - kanban/patterns/P-20-qobject-thread-affinity.md
  - kanban/patterns/AP-13-qobject-without-parent.md
  - AGENTS.md
audit_gate: "advisory — knowledge skill; Qt/ASan leak checks in Phase 3"
verifiable_output_shape: "advisory — knowledge skill, no artifact"
metadata:
  cites_patterns: ["P-19", "P-20", "AP-13"]
---

# pat-19 — Qt ownership & affinity

You are using `parented_ptr`/`make_parented` or creating a QObject. Surface
**[`P-19`](../../../kanban/patterns/P-19-parent-before-parented-ptr.md)** (set a valid parent at
construction) and **[`P-20`](../../../kanban/patterns/P-20-qobject-thread-affinity.md)** (a QObject
lives on its creating thread; the RT thread never mutates/receives-sync a QObject). Failure mode:
**[`AP-13`](../../../kanban/patterns/AP-13-qobject-without-parent.md)**. Read the cards; don't restate them.

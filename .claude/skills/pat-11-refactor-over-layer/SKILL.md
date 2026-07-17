---
name: pat-11-refactor-over-layer
description: "Surface the refactor-over-layer rule when an edit would add a parallel implementation
  beside a canonical one. Fire when creating a *_v2 / *New / duplicate function, class, or file that
  replaces existing behavior, or when introducing a new impl without migrating and deleting the old.
  Change in place, or migrate-all-callers-and-delete in the same change — never leave a _v2 beside."
disable-model-invocation: false
defers_to:
  - kanban/patterns/P-11-refactor-over-layer.md
  - kanban/patterns/AP-07-layering-over-refactor.md
audit_gate: "advisory — knowledge skill; duplicate-symbol review in Phase 3"
verifiable_output_shape: "advisory — knowledge skill, no artifact"
metadata:
  cites_patterns: ["P-11", "AP-07"]
---

# pat-11 — refactor over layer

You are about to add a parallel/`_v2` path. Surface
**[`P-11`](../../../kanban/patterns/P-11-refactor-over-layer.md)** (change in place, or add-migrate-all-
callers-and-delete in the same change — every add deletes) and its failure
**[`AP-07`](../../../kanban/patterns/AP-07-layering-over-refactor.md)** (a `_v2` left standing beside
the original). Trace callers first (`P-15`); grep the old symbol after — nonzero callers means
unfinished. Read the cards; don't restate them.

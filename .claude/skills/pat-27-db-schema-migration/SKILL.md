---
name: pat-27-db-schema-migration
description: "Surface the DB schema/DAO rules when editing library database code. Fire when changing
  res/schema.xml, files under src/library/dao/, or any code that runs ALTER/CREATE against the library
  DB or writes raw SQL. Schema changes go through forward-only versioned revisions in res/schema.xml;
  all library DB access goes through the typed DAO layer."
disable-model-invocation: false
defers_to:
  - kanban/patterns/P-27-versioned-db-schema-migration.md
  - kanban/patterns/P-28-dao-is-the-db-boundary.md
audit_gate: "advisory — knowledge skill; raw-SQL / schema-version lint in Phase 3"
verifiable_output_shape: "advisory — knowledge skill, no artifact"
metadata:
  cites_patterns: ["P-27", "P-28"]
---

# pat-27 — db schema migration

You are editing library DB code. Surface
**[`P-27`](../../../kanban/patterns/P-27-versioned-db-schema-migration.md)** (schema changes go through
forward-only versioned revisions in `res/schema.xml`, never ad-hoc `ALTER`) and
**[`P-28`](../../../kanban/patterns/P-28-dao-is-the-db-boundary.md)** (all library DB access via the
typed `src/library/dao/` layer; no raw SQL in callers). Never edit an existing revision; keep
migrations re-appliable. Read the cards; don't restate them.

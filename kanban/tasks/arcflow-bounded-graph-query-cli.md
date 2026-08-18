---
id: arcflow-bounded-graph-query-cli
type: task
title: "Expose ArcFlow centrality through a bounded Migx CLI query"
status: done
owner: gudjon
priority: high
initiative: initiative-ai-djing-product
depends_on: [arcflow-distinct-playlist-count-semantics]
authored_by: codex-cli
authored_kind: agent
triggered_by: "A0 had a verified graph and honest rankings but no TUI/CLI/agent product surface"
created: "2026-08-18"
lastUpdated: "2026-08-18"
acceptance: |
  `migx graph.rank` returns track or artist rankings through human and JSON
  output using native distinct-playlist semantics. Callers cannot submit GQL.
  Offline tests cover Unicode, scalar types, bounds, and both entities; the
  full corpus returns the pinned centrality leaders from the verified store.
---

# Bounded ArcFlow graph ranking

Implemented `graph.rank` as an ADR-008 query over the disposable ArcFlow index.
The adapter owns two fixed GQL templates, caps output at 100 rows, carries the
ArcFlow snapshot URI, and never enters a real-time or write path.

Verification:

- offline fake-runtime regressions cover `Ysée`, `RÜFÜS DU SOL`, numeric scalar
  restoration, read-only templates, invalid entities, and limit bounds;
- the command vocabulary lint recognizes `graph` in `arch-cli-commands`;
- the live 6,765-node / 9,483-relationship store returns the previously pinned
  track and artist leaders through `--json`;
- no DuckDB or parallel data engine was introduced.

Follow-on remains A0: ArcFlow `sync snapshot` currently reads a different
snapshot filename than `query`, and the installed daemon predates the pinned
runtime build. Neither is claimed as production-ready by this task.

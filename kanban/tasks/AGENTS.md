---
id: migx-tasks-format
type: doctrine
title: "Tasks — the flat backlog format"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/AGENTS.md
---

# Tasks

A **task** is a flat backlog item that is NOT owned by a live dossier — a follow-on spun out of a
closure, a small standalone fix, or a judgment call a `/loop`/Dream run deferred to a human. Real
design+execute work belongs in a **dossier** (MG-5), not here. Tasks are deliberately lightweight and
initiative-keyed, not a project tracker.

## When a task, when a dossier?
- Multi-step design/execute with a bet to score → **dossier**.
- A single bounded change, or an item to route to the right owner → **task**.
- A durable rule/decision → a **pattern** or **ADR**, not a task.

## File format
One file per task: `kanban/tasks/<slug>.md` — the filename IS the ID (`task-<slug>` when cited).

```yaml
---
id: <slug>
type: task
title: "<imperative one-liner>"
status: open              # open | in-progress | done | wont-do
owner: <who>
priority: medium          # low | medium | high
initiative: initiative-<slug>   # the standing bet this serves, if any
parent_dossier: <slug>    # set when spun out of a dossier's closure
depends_on: []            # [<slug>] other tasks / [PS-...] specs
authored_by: <agent-or-human>
authored_kind: mixed
triggered_by: <what surfaced this>
created: "YYYY-MM-DD"
lastUpdated: "YYYY-MM-DD"
acceptance: |
  <what "done" means, checkably>
---

<Body: context + the concrete change. Cite patterns/ADRs by ID; don't restate them.>
```

## Discipline
- Edges resolve: a `depends_on`/`parent_dossier` must point to something that exists (Phase-3 lint).
- Provenance: `authored_by`/`triggered_by` say where this came from — especially for agent-authored
  tasks from Dream runs.
- Close the loop: a `done` task should say what verified it (a test, a merged PR).

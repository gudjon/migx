---
id: migx-initiatives-agents
type: doctrine
title: "kanban/initiatives/ — purpose & format"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/AGENTS.md
  - kanban/GLOSSARY.md
---

# Initiatives

**The dossier is the unit of work (MG-5). An initiative is not.** An initiative is a *thin lateral
wrapper* around a hypothesis — one owner, one north-star metric, one guardrail — that points at the
**dossiers** which actually execute it and explains *why* the work is happening. It sits *alongside*
the work, not above it as a container.

Reach for one only when a strategic bet spans **several dossiers** and you want a single home for the
hypothesis and the metric they're all judged against. A one-dossier bet needs no initiative — the
dossier's `PROBLEM.md` already carries the why. Most work needs **zero** initiatives.

## Not to be confused with
- **Dossier** (`kanban/planning/`) — the 1–4-day design+execute unit that closes at `91-LOOP-CLOSURE`. *This is where work lives.*
- **Task** (`kanban/tasks/`) — a flat backlog item.
- **Pattern / ADR** (`kanban/patterns/`, `kanban/architecture/decisions/`) — durable knowledge / decided path.

## Isolation smell
An initiative with `status ≥ research` that points at **no** dossier is *isolated* — a smell. If it
has no dossier to wrap, it isn't ready to be an initiative yet; it's a note.

## Format
One file: `kanban/initiatives/initiative-<slug>.md` (add `-<quarter>` only if you actually run a
quarterly cadence). The filename slug is the ID — there is **no** `INIT-` typed anchor. Keep it
≤120 lines. Copy `_template.md`.

Required frontmatter: `id`, `type: initiative`, `title`, `owner`, `status`.
Core body: the hypothesis (`pm_overlay`), the dossiers it points at, the closed loop for the bet.

## Lifecycle
`proposed → research → active → complete → archived` (`paused` as a side state). `status: active`
means at least one wrapped dossier is executing.

## The closed loop (MG-1)
An initiative is itself a bet. Name its Trigger / Capture / Intelligence / Adjustment — for a perf
initiative that's usually: the benchmark suite / `EVD-*` records / delta-vs-baseline / a dossier
sealing or a `tasks/` card opening.

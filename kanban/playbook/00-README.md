---
id: migx-playbook
type: playbook
title: "The Migx Playbook — how to build software in the era of agent-paced engineering"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
audience: "Every engineer and every coding agent working in Migx. Read once on arrival; refer back when designing or grooming."
defers_to:
  - kanban/AGENTS.md
---

# The Migx Playbook

The doctrine for building Migx at agent speed — a deep, cleaned-up distillation of a mature reference
harness, refined for **one C++/Qt codebase** with a focused north-star: **Migx running blazingly fast
on Apple Silicon (M4/M5 + Metal)**. It keeps the company-agnostic practices (closed loops,
everything-is-code, refactor-over-layer) and drops the reference's org sprawl.

This playbook is the *why* and the *how*. `kanban/AGENTS.md` is the *ground rules* (MG-1..MG-6);
`kanban/GLOSSARY.md` is the *ID rules*; the per-primitive `AGENTS.md` files carry authoring
conventions. **Read the chapters in order on a first read; refer back by chapter afterwards.**

## The two ground rules (everything is a corollary)

- **MG-1 — Everything is a closed loop.** Trigger → Capture → Intelligence → Adjustment, with the
  adjustment automatic and verifiable against the same trigger. In Migx: a benchmark is the trigger,
  the delta-vs-baseline is the intelligence, the merged optimization is the adjustment.
- **MG-2 — Everything is code.** Load-bearing decisions live at stable grep-able paths, or they're
  scratch. *Human companion:* outsource thinking, not understanding.

## Chapters

| # | Chapter | What you get |
|---|---|---|
| **[01](01-frame-cadence-compounding.md)** | The Frame, the Cadence, and Compounding | The two ground rules; the dossier-as-sprint cadence; the 7-rule discipline checklist; compound-over-layer, no-ledger, the deletion test, memory-decays. **Start here.** |
| **[02](02-patterns-breakage-navigation.md)** | Patterns, Breakage, and Navigation | The pattern catalogue as compounding memory (anchor-not-name, skills cite not restate); the named breakage modes with Migx recoveries; symbol-not-string C++/Qt navigation with clangd. |
| **[03](03-harness-engineering-outer-ring.md)** | Harness Engineering — The Outer Ring | The outer-ring control system; the **which-primitive keeper rule** (subagent / skill / workflow / `/loop` / `/schedule`) modernized for current Claude Code; Guides×Sensors; the verification escalation ladder; build-one recipes. |
| **[04](04-daily-loop-and-the-dream.md)** | The Daily Loop and the Dream | The hour-by-hour developer loop; the autonomous decision cascade (running unattended); **the Dream** — the scheduled meta-loop that improves the harness itself; provenance. |

## Reading paths by role

| You are… | Read |
|---|---|
| New engineer / agent, day one | `01` → `04` (the daily loop) → refer to `02`/`03` as questions arise |
| Reviewing a PR | `01` §Discipline Checklist |
| Opening a unit of work | `01` §Cadence → scaffold from `kanban/planning/_template/` |
| Debugging a regression | `02` §Breakage catalogue |
| Extending the harness (skill/agent/workflow/loop) | `03` §Which primitive + `.claude/skills/AGENTS.md` + `.claude/workflows/AGENTS.md` |
| Running an overnight/optimization loop | `04` §Daily loop + §Autonomous decision cascade |
| Building / extending the Dream | `04` §The Dream + `kanban/triggers/registry.yaml` |

## Relationship to the rest of the kanban

The playbook governs *how* we work; the live state lives elsewhere and the playbook only points at it
(MG-3): patterns in `kanban/patterns/`, decisions in `kanban/architecture/decisions/`, the
architecture/DDD map in `kanban/architecture/`, cadence in `kanban/triggers/`, work in
`kanban/planning/`. When the playbook and the code disagree, **the code is right and the playbook is
stale** — fix the playbook.

> Everything is a closed loop. Everything is code. The day is one iteration of the bigger loop.

# AGENTS.md — Mixxx Project Instructions

See [README.md](README.md) for a project overview, and
[CONTRIBUTING.md](CONTRIBUTING.md) for build instructions, code style,
pre-commit setup, Git workflow, and pull request guidelines.

## Key Architecture

- **ControlObject/ControlProxy**: `[Group], key_name` inter-component communication.
- **Engine thread**: Real-time audio — no allocations, no locks, may emit Qt signals but cannot receive them.
- **parented_ptr/make_parented**: Qt object-tree ownership. Object must get a parent before `parented_ptr` destructs.

The three rules above are the **house physics** — the load-bearing invariants a change must never
break. They are stated once here; the harness below cites them, never restates them.

## Platform (hard floor)

**macOS 26.\*+ on Apple Silicon (arm64) only.** No Intel, no Rosetta, no Windows/Linux shipping
target. Decision: [`kanban/architecture/decisions/ADR-006-platform-scope-apple-silicon.md`](kanban/architecture/decisions/ADR-006-platform-scope-apple-silicon.md).

## Project Layout

```text
src/          C++ source (engine/, controllers/, library/, mixer/, effects/, qml/, preferences/, util/, test/)
res/          Resources (controllers/ JS/XML, skins/, qml/)
cmake/        CMake modules
tools/        Python helper scripts
kanban/       The agent harness — doctrine, playbook, patterns, architecture map, dossiers (SSoT for how we work)
```

## Agent harness (Claude Code / Codex / Grok)

This repo carries a tool-agnostic agent harness. Any coding agent should read:

- **[CLAUDE.md](CLAUDE.md)** — thin routing (Claude Code loads it every session).
- **[GROK.md](GROK.md)** — thin routing for Grok CLI (default role: federation **signal scout**).
- **[AGY.md](AGY.md)** — Antigravity CLI entry (**paused** — no tokens; not in active mix).
- **[kanban/AGENTS.md](kanban/AGENTS.md)** — the operating doctrine (MG-1..MG-6: closed loops,
  everything-is-code, single-source-of-truth, one owner, dossier-as-unit, house physics).
- **[kanban/federation/FEDERATION.md](kanban/federation/FEDERATION.md)** — peer federation on this box
  (active: Grok · Claude · Codex); CLI `./kanban/scripts/migx-fed`.
- **[kanban/playbook/](kanban/playbook/00-README.md)** — how to build software here: the cadence, the
  pattern catalogue, harness engineering, the daily loop.
- **[kanban/patterns/](kanban/patterns/AGENTS.md)** — design patterns / antipatterns (`P-NN`/`AP-NN`),
  cited by ID in code and dossiers. The `.claude/skills/pat-*` skills auto-surface them.
- **[kanban/architecture/README.md](kanban/architecture/README.md)** — the bounded-context (DDD) map,
  keyed on the real-time-thread axis.

**Domain charters** — each subsystem folder carries an `AGENTS.md` with its purpose, invariants, and
build/test entry points (it cites, but does not restate, the house rules above):

- [src/engine/AGENTS.md](src/engine/AGENTS.md) — the real-time audio graph (highest-risk)
- [src/control/AGENTS.md](src/control/AGENTS.md) — the ControlObject messaging bus
- [src/soundio/AGENTS.md](src/soundio/AGENTS.md) — the audio callback origin
- [src/mixer/AGENTS.md](src/mixer/AGENTS.md) — deck/player lifecycle

**North-stars:**

- **AI-DJing product** (Cursor-for-music, **MIT operating model**: proprietary app + Intelligence;
  public early → agora later) — [`kanban/Strategy-Current.md`](kanban/Strategy-Current.md) ·
  [ADR-003](kanban/architecture/decisions/ADR-003-licensing-and-openness.md) ·
  [ADR-005](kanban/architecture/decisions/ADR-005-open-core-plus-proprietary-intelligence.md).
- **Blazingly fast on Apple Silicon** (M4/M5 + Metal) — closed-loop benchmark dossiers under
  [initiative-apple-silicon](kanban/initiatives/initiative-apple-silicon.md).

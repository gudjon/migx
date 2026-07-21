---
id: migx-kanban-doctrine
type: doctrine
title: "Migx Operating Doctrine — how agents and engineers work in this repo"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
audience: "Every engineer and every coding agent working in Migx. Read once on arrival; refer back when designing or grooming."
---

# Migx Operating Doctrine

This is the spine of the Migx agent harness — the `kanban/` markdown-as-code memory that governs
*how* we work. **Migx** is a DJ-software brand forked from Mixxx; this harness is adapted from a
mature reference system, keeping the company-agnostic practice doctrine and leaving the reference's
domain behind.

Two files carry policy: this one (`kanban/AGENTS.md`) is the **portable doctrine** — read it even if
you are not Claude Code. `CLAUDE.md` at the repo root is the **thin Claude-Code routing layer** that
points here. The repo-root `AGENTS.md` carries the **house code physics** (RT engine, ControlObject,
Qt ownership) — this doctrine honors and extends it, never duplicates it.

## The two ground rules (everything else is a corollary)

**MG-1 — Everything is a closed loop.** Every important process runs with four beats:
**Trigger → Capture → Intelligence → Adjustment**. A loop is *closed* when the adjustment is
automatic, repeatable, and verifiable against the same trigger. Shipping work with no closed loop
attached means the work isn't done. For Migx performance work the loop is concrete: a benchmark is
the trigger + capture, the measured delta is the intelligence, the merged optimization is the
adjustment — and the next benchmark run re-closes it.

**MG-2 — Everything is code.** Anything load-bearing lives at a stable, grep-able path — a file in
`kanban/`, an ADR, a pattern, a source annotation. Slack, PR threads, and tribal knowledge are
scratch. If a load-bearing decision isn't written at a stable path, it is not load-bearing; it is
scratch.

*Human-side companion:* you can outsource thinking, not understanding. Comprehension stays in your
head; the thinking is what you delegate to agents.

## The corollary principles

**MG-3 — Single source of truth; derive, don't restate; cite, don't copy.** Every fact has exactly
one canonical home. Never store a value another file can derive. Cross-reference by typed ID
(`P-07`, `PS-ASI-01`, `ADR-003`), never by prose ("the waveform thing"). A doc that depends on
another declares `defers_to:` and points — it does not copy the text. (See `.claude/rules/single-source-of-truth.md`.)

**MG-4 — One owner per unit of work.** Every dossier has one facilitator (named in its folder); every
PR has one DRI who owns its full lifecycle — open, review-response, land. Judgment is exercised, not
deferred; a stale `blocked` premise is re-derived before it's trusted.

**MG-5 — The dossier is the unit of work.** Planning happens in dossiers, not tickets. A dossier is
one closed-loop design+execute sprint (`kanban/planning/<date>-<owner>-<pfx>--<slug>/`), scoped
full-capability, sealed at `91-LOOP-CLOSURE/` where the bet is scored (verdict · 5-pass retro ·
wiring ledger · forecast-vs-actual). **Compound before create:** before scaffolding a new dossier,
prove no OPEN dossier already owns the scope and fold into it if one does. A sealed dossier is a
dated snapshot — a record of THEN, never current truth; current truth lives in the code, the
`architecture/` map, and the pattern catalogue. (See `.claude/rules/dossier-lifecycle.md` and
`planning-harness.md`.)

**MG-6 — Respect the house physics.** Migx is a real-time audio application. The RT engine thread
does no allocation and takes no locks (it may emit Qt signals but cannot receive them); Qt objects
follow `parented_ptr`/`make_parented` ownership; components talk through ControlObject/ControlProxy
`[Group], key`. The **fast quality gate is `pre-commit`** (clang-format/tidy, qmllint, cmake lint),
not the heavy full build. These are non-negotiable — a "faster" change that allocates on the audio
thread is a regression, not an optimization. SSoT for the substance: repo-root `AGENTS.md`.

## What the harness is for (the north-stars)

The harness serves two standing product bets (see `kanban/Strategy-Current.md`):

1. **AI-DJing product** — Cursor-for-music under **MIT operating model** (ADR-003): hard fork, public
   early → [agora](https://github.com/orgs/agora) later, proprietary app + Intelligence (`initiative-ai-djing-product`,
   ADR-005).  
2. **Blazingly fast on Apple Silicon (M4/M5)** — Metal + DSP closed-loop dossiers
   (`initiative-apple-silicon`) so the AI layer never glitches audio.

Missing capabilities become development dossiers, each a closed loop scored on real benchmark or
product acceptance numbers. Roadmap: `kanban/planning/00-PORTFOLIO/migx-harness-roadmap.md`.

## Where things live (the routing table)

| You want to… | Go to |
|---|---|
| Learn the ID rules (prefixes, anchor-vs-semantic) | `kanban/GLOSSARY.md` |
| See which dossier prefixes are registered | `kanban/planning/00-PORTFOLIO/prefix-registry.yaml` |
| Start a new unit of work | scaffold a dossier from `kanban/planning/_template/` |
| Cite or add a validated pattern / named failure mode | `kanban/patterns/` (`P-NN` / `AP-NN`) |
| Record a path-pinning decision | `kanban/architecture/decisions/` (ADR) |
| Add a backlog task not tied to a live dossier | `kanban/tasks/` |
| See what fires on a cadence | `kanban/triggers/registry.yaml` |
| Run multiple agents on this box without clobbering | `kanban/runbooks/multi-agent-parallel-sessions.md` |
| Federate peers (Grok · Claude · Codex; AGY paused) | `kanban/federation/FEDERATION.md` + `./kanban/scripts/migx-fed` |
| Antigravity CLI (`agy`) — **paused** | repo-root `AGY.md` + `roles/antigravity-cli.md` (no tokens) |
| Active fleet how-to / what’s missing | `kanban/knowledge/fleet-operating-model.md` |
| Fleet conductor + Codex drain | `just fleet` / `just fleet-drain` · `kanban/runbooks/fleet-conductor.md` |
| Run Grok 4.5 like a Claude Code long loop | `kanban/runbooks/grok-long-harness-loop.md` |
| Port UI components with agents | `kanban/runbooks/ai-ui-migration-loop.md` + `kanban/knowledge/ui-framework-migration-map.md` |
| Shape NextGen music/arrangement mode | `kanban/knowledge/nextgen-music-management-mode.md` + `kanban/tasks/nextgen-music-management-mode.md` |
| Fix Gemini CLI on macOS / migrate to Antigravity | `kanban/runbooks/gemini-cli-macos-fix.md` |
| Understand the **product strategy** (Cursor for AI-DJing) | `kanban/Strategy-Current.md` + ADR-005 |
| Git posture (public early, agora later) | `kanban/runbooks/go-private-and-git-posture.md` |
| Understand the house code physics | repo-root `AGENTS.md` |
| Understand build/test/lint commands | repo-root `AGENTS.md` + `CONTRIBUTING.md` |

## The closed-loop test (apply to any process you build)

Name the four beats out loud. If you cannot, the loop is open:
1. **Trigger** — what starts it (a benchmark, a commit, a schedule, a merged PR)?
2. **Capture** — what data does it record at a stable path?
3. **Intelligence** — what reads that data and produces a verdict/delta?
4. **Adjustment** — what changes automatically as a result, verifiable against the same trigger?

> Everything is a closed loop. Everything is code. The day is one iteration of the bigger loop.

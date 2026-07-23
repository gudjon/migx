---
id: migx-agent-onboarding
type: doctrine
title: "Agent onboarding — what to read, in what order, and the 8 artifact families"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/AGENTS.md
  - kanban/HARNESS.md
---

# Agent Onboarding

You are a coding agent (or engineer) arriving in Migx. This is your reading list and the map of what
the harness maintains. Read the tier that matches your task; don't read everything.

## Reading tiers

**Tier 0 — always (every session).** Tool routing (`CLAUDE.md`, `GROK.md`, or tool-native root
routing) and repo-root `AGENTS.md` (house code physics: RT engine no-alloc/no-lock,
ControlObject/ControlProxy, `parented_ptr` Qt ownership, build/test/lint commands). These are
non-negotiable and short. Note: `AGY.md` / Antigravity is **paused** (no tokens) — skip unless re-enabled.

**Tier 1 — before doing any real work.** `kanban/AGENTS.md` (the operating doctrine, MG-1..MG-6) and
this file. Fifteen minutes; it changes how you work. If another agent is live on this box: also
`kanban/federation/FEDERATION.md` + your role under `kanban/federation/roles/`, then
`./kanban/scripts/migx-fed sync` and `./kanban/scripts/migx-fed poll --to <side>`.

**Tier 2 — by task shape:**
| Your task | Read |
|---|---|
| Designing/opening a unit of work | `kanban/playbook/01` (cadence) + `.claude/rules/planning-harness.md` → scaffold from `kanban/planning/_template/` |
| Writing an optimization (the north-star) | `kanban/initiatives/initiative-apple-silicon.md` + the relevant dossier + `kanban/patterns/` perf patterns |
| Reviewing a PR / diff | `kanban/playbook/01` §Discipline Checklist + `.claude/rules/agentic-decision-authority.md` |
| Debugging a regression | `kanban/playbook/02` §Breakage catalogue |
| Extending the harness (skill/agent/workflow) | `kanban/playbook/03` (which primitive) + `.claude/skills/AGENTS.md` + `.claude/workflows/AGENTS.md` |
| Grooming the kanban | `.claude/rules/single-source-of-truth.md` + `.claude/rules/dossier-lifecycle.md` |
| Multi-agent federation / worktrees | `kanban/federation/` + `runbooks/multi-agent-parallel-sessions.md` |
| Grok signal scout | `GROK.md` + `roles/grok-signal.md` + `runbooks/grok-long-harness-loop.md` |
| Grok 4.5 long harness / overnight loop | `runbooks/grok-long-harness-loop.md` + `knowledge/grok-long-harness-and-loops.md` |
| Codex long verifier harness | `AGENTS.md` + `kanban/federation/roles/codex-cli.md` + `runbooks/codex-long-harness-loop.md` |
| Antigravity co-implementer | **Paused** (no tokens). See `AGY.md` re-enable checklist when available |
| Claude implementer with federation live | `CLAUDE.md` §Multi-agent + `roles/claude-code.md` + `migx-fed sync` + `migx-fed poll` |
| Product strategy / agora transfer / moat | `kanban/Strategy-Current.md` + ADR-005 + `runbooks/go-private-and-git-posture.md` |
| Brand / positioning / messaging | `kanban/playbook/branding/` (`BRND-*`) + `knowledge/migx-brand-positioning-experience-designer.md` |

**Tier 3 — reference on demand.** `kanban/GLOSSARY.md` (ID rules), `kanban/patterns/` (catalogue),
`kanban/architecture/decisions/` (ADRs), `kanban/triggers/registry.yaml` (cadence).

## The 8 artifact families the harness maintains

A long-running harness authors and grooms these. Each has one home (MG-3).

1. **Operating doctrine** — `kanban/AGENTS.md` (MG-1..MG-6) + `kanban/playbook/`.
2. **Glossary / naming** — `kanban/GLOSSARY.md` + `prefix-registry.yaml`.
3. **Pattern + antipattern catalogue** — `kanban/patterns/` (`P-NN` / `AP-NN`).
4. **Planning lifecycle** — `kanban/planning/` dossiers + `_template/` + `91-LOOP-CLOSURE`.
5. **In-code annotation layer** — pattern-anchor comments in `src/` linking code to `P-NN` (Phase 2+).
6. **Workflow / cadence catalogue** — `.claude/workflows/` + `kanban/triggers/registry.yaml`.
7. **Skill / subagent inventory** — `.claude/skills/` + `.claude/agents/` (+ their `AGENTS.md`).
8. **Live-state / architecture mirror** — `kanban/architecture/` map + `kanban/knowledge/` notes;
   for perf work, the benchmark baseline records (`EVD-*`) are the live state.

## The one rule that catches you when unattended

If you're running a `/loop` or workflow and hit a fork, **do not stop to ask a human** unless the
action is irreversible or a genuine value judgment only the owner can make. Otherwise: articulate the
options, challenge with a 5-whys, decide with confidence ≥ 0.4 (or flag-and-skip and continue),
record the decision at a stable path, and keep the loop closed. Stopping to ask mid-loop is the
default failure mode.

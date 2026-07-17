# GROK.md — Migx (Grok CLI / Grok 4.5 entry)

Thin routing for **Grok** sessions. State each rule once in its home — this file only points.
Claude Code loads `CLAUDE.md`; you load **this** + repo-root `AGENTS.md`.
(Antigravity/`AGY.md` is **paused** — no tokens; not in the active mix.)

## Product context (30 seconds)
- **MIT operating model** (ADR-003): proprietary app + in-process AI allowed (Cursor path).  
- Strategy: `kanban/Strategy-Current.md`  
- Default peer role: **signal scout** for the federation: Claude implements, Codex verifies.

## Session start (always)

```bash
export MIGX_FED_SIDE=grok-signal
export MIGX_REPO_ROOT="$(git rev-parse --show-toplevel)"
./kanban/scripts/migx-fed sync
./kanban/scripts/migx-fed poll --to grok-signal
```

Then read only what the current **loop contract** needs (see long harness below) — not the whole monorepo.

## Roles

| Mode | When | Doc |
|---|---|---|
| **Signal scout** (default) | X/web field intel, research-requests | `kanban/federation/roles/grok-signal.md` |
| **Long harness loop** | Multi-hour / overnight autonomous waves | `kanban/runbooks/grok-long-harness-loop.md` |
| **Bounded generator** | Non-RT coding waves (docs, QML, tasks) | same runbook Mode B |
| **Implementer** (rare) | Owner reassigns; own worktree | house physics still bind |

## Read first
- House code physics → repo-root [`AGENTS.md`](AGENTS.md)  
- Doctrine → [`kanban/AGENTS.md`](kanban/AGENTS.md)  
- Federation → [`kanban/federation/FEDERATION.md`](kanban/federation/FEDERATION.md)  
- Long loop research map → [`kanban/knowledge/grok-long-harness-and-loops.md`](kanban/knowledge/grok-long-harness-and-loops.md)  
- Multi-agent worktrees → [`kanban/runbooks/multi-agent-parallel-sessions.md`](kanban/runbooks/multi-agent-parallel-sessions.md)

## Scout mandate
X + selective web for: audio/music **world models**, AI models for music/DJ, Metal/QML/architecture,
RT techniques, Cursor-product moves (freemium AI, privacy, closed product velocity), **harness/loop
engineering**. Promote only when actionable — map to Strategy pillars + ADR-005 layers A/B/C.

## Long harness like Claude Code (the Migx way)

Claude Code has `/loop` + hooks + subagents natively. Grok 4.5 gets the **same closed-loop
properties** via this repo:

| Need | Migx mechanism |
|---|---|
| Durable memory | `AGENTS.md`, `GROK.md`, kanban, federation mail |
| Loop | Disk contract + waves (`runbooks/grok-long-harness-loop.md`) |
| Multi-agent | `migx-fed` + worktrees (Claude implementer, Codex verifier; AGY paused) |
| Verify | handoff bar / pre-commit / leave perf eval to Claude (`P-08`) |
| Restart | read `contract.md` + `progress.md` only |

**Rule:** write the loop, not the prompt. State on disk. Short waves. Evaluator outside generator.

```bash
# one-time per long run
RUN_ID="scout-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p kanban/federation/scratchpad/$RUN_ID
# fill contract.md + progress.md per runbook — then wave until NEXT=stop
```

## Worktree preference
```bash
git worktree add ../migx-grok -b grok/loop-$(date +%Y%m%d)
cd ../migx-grok && grok
```
Keep compile-heavy work on Claude's tree when disk is tight.

## Scout session checklist
1. `migx-fed poll --to grok-signal`  
2. Drain `research-request` / `question` mail  
3. Scout → `signal/YYYY-MM-DD-*.md`  
4. 0–2 `signal-handoff` max  
5. Commit `kanban/federation/**` so addressed peers can pull
6. Update loop `progress.md` if in a long run  

## Unattended
Same cascade as Claude: decide ≥0.4 confidence, record path, continue. Halt only for irreversible
acts or pure value judgments (owner).

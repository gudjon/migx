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
./kanban/scripts/migx-fed audit
./kanban/scripts/migx-fed poll --to grok-signal
```

Then read only what the current **loop contract** needs (see long harness below) — not the whole monorepo.
If Grok is asked to mutate repo docs or code instead of only writing `signal/`, create a narrow
`migx-fed claim` first.

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

## Long harness (Grok Build full features + Migx disk)

Grok Build **natively** has `/goal`, `/loop`, `monitor`, subagents (default background), worktree
isolation, plan mode, compaction-surviving TODOs/bg tasks, multi-CLI resume (Claude/Codex/Cursor),
and X/web research tools. Use them — do not degrade to chat-only. Details:
`kanban/knowledge/grok-long-harness-and-loops.md` (pinned CLI 0.2.102+).

| Need | Grok Build runtime | Migx durable SSoT |
|---|---|---|
| Multi-turn objective | `/goal` + `update_goal` | `contract.md` / dossier PS |
| Recurring waves | `/loop`, `scheduler_*`, `monitor` | federation mail + commits |
| Parallel work | `spawn_subagent` + `isolation:worktree` | git worktrees + `migx-fed` |
| Plan before code | `/plan` (plan-file-only even under always-approve) | dossier waves |
| Survive compaction | TODOs + bg task IDs | `progress.md` + git |
| Restart after death | `/resume` + `/recap` | read contract + progress + fed poll |
| Verify | `/check-work`, independent subagent | pre-commit / ctest / peer (`P-08`) |

**Rule:** arm `/goal` + disk contract for any run >2 waves. Short waves. Evaluator ≠ generator.

```bash
# one-time per long run
RUN_ID="scout-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p kanban/federation/scratchpad/$RUN_ID
# fill contract.md + progress.md per runbook
# in TUI: /goal … then /loop 4h "one Mode A wave RUN=$RUN_ID"
```

## Worktree preference
```bash
git worktree add ../migx-grok -b grok/loop-$(date +%Y%m%d)
cd ../migx-grok && grok
```
Keep compile-heavy work on Claude's tree when disk is tight.

## Merge hygiene (Claude builds from `main`)
Claude Code expects a **buildable `main`**. Occasionally (every few waves, and before long Claude sessions):

```bash
git checkout main
git status -sb                    # no surprise WIP
# commit any intentional federation/docs/tools work on main
git push origin main              # remote matches local
```

- Prefer landing Grok federation + knowledge on **main** (or merge feature branches promptly).  
- Do not leave long-lived unpushed main commits — Claude’s build box pulls/uses `main`.  
- Never force-push `main`.

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

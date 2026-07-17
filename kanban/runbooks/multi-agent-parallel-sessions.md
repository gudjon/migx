---
id: runbook-multi-agent-parallel-sessions
type: runbook
title: "Running multiple AI coding agents (Claude, Grok, Codex) on Migx in parallel"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - .claude/rules/worktree-hygiene.md
  - kanban/AGENTS.md
  - kanban/federation/FEDERATION.md
---

# Multi-agent parallel sessions

Run Claude Code + Codex CLI + Grok CLI on the **same Migx repo** at the same time, safely.
(Antigravity/`agy` is **paused** — no tokens; see `peers.yaml` / `AGY.md`.)
The harness is tool-agnostic by design (`AGENTS.md` is the shared entry point every agent reads),
so the only real work is **isolation + coordination**.

## The hard rule
**Never run two agents in the same working tree on the same branch.** Concurrent edits clobber each
other's uncommitted writes and race on git. Use **git worktrees** (`.claude/rules/worktree-hygiene.md`).

## Recommended federation (this box)

| Peer | Tool | Side id | Default work | Entry doc | Status |
|---|---|---|---|---|---|
| **Implementer** | Claude Code | `claude-code` | C++/Qt, dossiers, RT/engine **+** non-RT/UI while AGY paused | `CLAUDE.md` + `roles/claude-code.md` | **active** |
| **Verifier-cartographer** | Codex CLI | `codex-cli` | Repo mapping, claim verification, harness tooling | `AGENTS.md` + `roles/codex-cli.md` | **active** |
| **Signal scout** | Grok CLI | `grok-signal` | X/web field signal, briefs, research answers | `GROK.md` + `roles/grok-signal.md` | **active** |
| Co-implementer (dormant) | Antigravity (`agy`) | `antigravity-cli` | Was: UI/ontology volume | `AGY.md` | **paused** |

**Federation** (durable handoffs, not chat): [`kanban/federation/FEDERATION.md`](../federation/FEDERATION.md)
and `./kanban/scripts/migx-fed`.

```text
Grok         → signal + signal-handoff     → Claude implements
Claude       → research-request            → Grok scouts X
Codex        → verification notes          → Claude / Gudjon act
```

## Setup (one worktree per agent)
```bash
# Terminal 1 — Claude Code (main checkout, compile-heavy OK)
cd ~/code/migx
export MIGX_FED_SIDE=claude-code
export MIGX_REPO_ROOT="$PWD"
./kanban/scripts/migx-fed sync
./kanban/scripts/migx-fed poll --to claude-code
claude

# Terminal 2 — Grok CLI (separate worktree + branch; prefer non-compile)
cd ~/code/migx
git worktree add ../migx-grok -b grok/signal-scout
cd ../migx-grok
export MIGX_FED_SIDE=grok-signal
export MIGX_REPO_ROOT="$(git rev-parse --show-toplevel)"
./kanban/scripts/migx-fed sync
./kanban/scripts/migx-fed poll --to grok-signal
# then: grok   # reads GROK.md + AGENTS.md + kanban/

# Terminal 3 — Codex CLI (separate worktree when mutating; read-only is okay in main)
cd ~/code/migx
git worktree add ../migx-codex -b codex/verify-steward
cd ../migx-codex
export MIGX_FED_SIDE=codex-cli
export MIGX_REPO_ROOT="$(git rev-parse --show-toplevel)"
./kanban/scripts/migx-fed sync
./kanban/scripts/migx-fed poll --to codex-cli
# optional long listener: ./kanban/scripts/migx-fed listen --to codex-cli --interval 900
# then: codex

# Terminal 4 — Antigravity CLI — PAUSED (no tokens). Do not start until peers.yaml re-activates.
# See AGY.md re-enable checklist when tokens return.
```
Separate directories, shared history, independent branches → **zero file collisions; reconcile via git.**

## Shared brain (why they cooperate, not just coexist)
- **`AGENTS.md`** (repo root) = portable entry point. `CLAUDE.md` / `GROK.md` are thin per-tool routing
  (`AGY.md` retained but paused).
- **`kanban/`** = shared memory + work tracking.
- **`kanban/federation/`** = peer mail + signal briefs (coordination substrate).

## Coordination protocol
1. **Own before you touch (MG-4).** Claim a `kanban/tasks/<slug>.md` or a dossier by setting
   `owner:`/`facilitator:` before working it. Don't grab a task another agent owns.
2. **Split by role first, DDD second.** Default: Grok = signal, Claude = all implementation
   (RT + non-RT while AGY paused), Codex = verification/cartography/harness. If multiple agents code,
   split by bounded context (`src/**/AGENTS.md`) and file a coordination message first.
3. **Federation for intent; git for code.** Handoffs and research requests go through `migx-fed`.
   Code lands as commits on each branch; merge via PR/local merge.
4. **Solo author.** Each agent commits as `Gudjon Mar Gudjonsson <gudjon@gmail.com>`, no AI co-author
   (`includeCoAuthoredBy: false`) — see `kanban/AUTHORS.md`.
5. **Session start sync + poll (all peers).**
   ```bash
   ./kanban/scripts/migx-fed sync
   ./kanban/scripts/migx-fed poll --to "$MIGX_FED_SIDE"
   ```
   For Codex long harness mode, use
   `./kanban/scripts/migx-fed listen --to codex-cli --interval 900` and run bounded verifier waves
   from `kanban/runbooks/codex-long-harness-loop.md`.

## Federation quick reference
```bash
./kanban/scripts/migx-fed doctor
./kanban/scripts/migx-fed sync
./kanban/scripts/migx-fed list --status open
./kanban/scripts/migx-fed listen --to codex-cli --interval 900
./kanban/scripts/migx-fed send --from grok-signal --to claude-code \
  --type signal-handoff --subject my-finding --body /tmp/body.md
./kanban/scripts/migx-fed ack  --id <id> --by claude-code
./kanban/scripts/migx-fed close --id <id> --by claude-code --resolution "landed in …"
```
Body **must** include `## Intent` / `## Context` / `## Evidence` / `## Requested Action` / `## Blockers`
(`kanban/federation/MSG-TEMPLATE.md`).

## Footguns (shared `.git` across worktrees)
- The **stash stack** and `.git/config` are shared. Inside a worktree: **no** bare `git add -A`, **no**
  `git stash pop`, **no** bare `git config user.name`. Stage explicit paths.
- Each worktree needs its **own `build/`** — a second full build is ~2–3 GB. On a tight disk, give
  Grok **non-compile** work (signal, docs, tasks). Antigravity stays dormant until tokens return.
- `kanban/federation/scratchpad/` is **gitignored** — local only.
- Commit federation paths so the other peer can pull; uncommitted mail is invisible to the other tree
  until committed (or cherry-picked).
- The `warn-worktree-boundary.py` hook flags edits that reach outside a worktree.

## Cleanup
```bash
git worktree remove ../migx-grok      # when done (branch merged or abandoned)
git worktree remove ../migx-codex
# git worktree remove ../migx-agy   # only if an old dormant AGY worktree exists
git worktree prune
```

## When to use what
- **Default product federation** (Claude implements RT + non-RT, Codex verifies, Grok scouts) → worktrees + federation.
- **Reduced lane** (one implementer, Codex verifies, Grok scouts) → worktrees + `migx-fed`.
- **Parallel feature coding** (both mutate `src/`) → worktrees + DDD split + still poll federation.
- **One agent, one focus** → main checkout; still optional `migx-fed poll`.
- **In-process fan-out** → Claude Code subagents/workflows (not a second CLI).

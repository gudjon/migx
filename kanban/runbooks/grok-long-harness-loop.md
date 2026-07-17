---
id: runbook-grok-long-harness-loop
type: runbook
title: "Run Grok 4.5 in a long harness loop (Claude-Code-shaped) on Migx"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/knowledge/grok-long-harness-and-loops.md
  - GROK.md
  - kanban/federation/FEDERATION.md
  - kanban/playbook/04-daily-loop-and-the-dream.md
  - .claude/rules/agentic-decision-authority.md
---

# Grok long harness loop

Run **Grok 4.5** (Grok CLI / Grok Build) for hours or overnight with the same *properties* as a
Claude Code `/loop`: durable state on disk, verify gates, clean restart, no human message-ferry.

Research map: `kanban/knowledge/grok-long-harness-and-loops.md`.

---

## Preconditions

```bash
cd ~/code/migx   # or grok worktree
export MIGX_FED_SIDE=grok-signal
export MIGX_REPO_ROOT="$(git rev-parse --show-toplevel)"
./kanban/scripts/migx-fed doctor
```

Prefer a **dedicated worktree** when Claude is compiling:

```bash
git worktree add ../migx-grok -b grok/loop-$(date +%Y%m%d) 2>/dev/null || true
cd ../migx-grok
export MIGX_FED_SIDE=grok-signal MIGX_REPO_ROOT="$(git rev-parse --show-toplevel)"
```

---

## Mode A — Signal scout loop (default)

### A0. Write the contract (once per run)

```bash
RUN_ID="scout-$(date -u +%Y%m%dT%H%M%SZ)"
DIR="$MIGX_REPO_ROOT/kanban/federation/scratchpad/$RUN_ID"
mkdir -p "$DIR"
```

Create `$DIR/contract.md`:

```markdown
# Contract — Grok signal scout
## Goal
Scout X/web for Migx-relevant signal; promote only actionable handoffs.
## In scope
audio/music WM, AI models for music/DJ, Metal/QML/architecture, Cursor-product moves, RT techniques
## Out of scope
src/engine RT edits; full native rebuild; more than 2 handoffs/day
## Done when
- ≥1 signal brief committed OR research-request mail drained
- each handoff has acceptance + Strategy/ADR map
- progress.md says NEXT=stop or sleep
## Verify
./kanban/scripts/migx-fed list --status open
ls kanban/federation/signal/ | tail
```

Create `$DIR/progress.md`:

```markdown
# Progress
- wave: 0
- next: poll federation mail
- blockers: none
```

### A1. One wave (repeat)

At the start of each wave, **only** load into context:

1. `GROK.md` + role charter (stable)  
2. `$DIR/contract.md`  
3. Tail of `$DIR/progress.md`  
4. `migx-fed poll --to grok-signal` output  

Then execute:

```text
1. Drain research-request / question mail (ack/close when done)
2. Scout (x_semantic_search / x_keyword_search / web) on mandate topics
3. Write kanban/federation/signal/YYYY-MM-DD-<slug>.md
4. Optionally: migx-fed send signal-handoff (0–2/day max)
5. Append progress.md: wave N, what landed, NEXT=
6. Commit federation paths so Claude can pull
7. If NEXT=stop → exit; else sleep interval → wave N+1
```

### A2. Unattended decisions
Use the same cascade as Claude (`.claude/rules/agentic-decision-authority.md`):

- Confidence ≥ 0.4 → decide, write to progress.md, continue  
- Irreversible (force-push, delete remote, ship binary) → stop  
- Value judgment (what product is worth) → flag for Gudjon, continue other work  

### A3. Sleep / cron shell (optional)

```bash
# example: one scout wave every 4h while machine is up
while true; do
  # open grok with a prompt that says: read contract+progress, run one wave, exit
  # grok -p "Run one Mode A wave per kanban/runbooks/grok-long-harness-loop.md RUN=$RUN_ID"
  sleep 14400
done
```

Exact `grok` CLI flags vary by install — the **invariant** is: each wave restarts from disk, not
from an infinite chat transcript.

---

## Mode B — Generator loop (bounded coding)

Use when Grok owns a **non-RT** coding wave (docs, QML chrome, tasks, federation, DESIGN.md).

### B0. Contract

```markdown
## Goal
<one wave outcome>
## Acceptance
<pre-commit green on files> + <test filter if any>
## Out of scope
src/engine/** RT paths unless explicitly assigned
## Evaluator
Claude or human reviews before merge to main integration branch
```

### B1. Wave

```text
implement → pre-commit run --files <changed> → ctest -R <filter> if needed
→ commit → update progress → stop or next wave
```

**Never** self-seal a perf claim (`P-08`). Hand to Claude for MTL/EVD.

---

## Mode C — Product federation day

| Time | Grok | Claude | Codex |
|---|---|---|---|
| Session start | `migx-fed poll` | `migx-fed poll` | `migx-fed poll` or `listen` |
| Day | Scout + answer research-requests | MTL/engine + UI/ontology/non-RT waves while AGY paused | Verify/map/steward |
| Handoff | `signal-handoff` commits | ack -> fold into dossier or task | evidence / coord notes |
| Blocked on field | - | `research-request` to Grok | `research-request` to Grok |
| End of day | progress.md + commits | journal + commits + Resolution | evidence + closed mail |

Worktrees separate; **git + federation** = shared long memory.

---

## Restart after crash / context death

```bash
# 1. find latest run
ls -1dt kanban/federation/scratchpad/scout-* | head -1
# 2. read contract + progress only
# 3. continue from NEXT=
```

If progress is stale, re-poll federation — **source of truth for cross-agent work is `messages/`**,
not scratchpad.

---

## Quality gates (scout)

A handoff is invalid unless:

- [ ] Evidence links (X/post/web)  
- [ ] Mapped to Strategy pillar or ADR-005 layer  
- [ ] `## Requested Action` Claude or Codex can do in one wave *or* “file task/dossier”  
- [ ] One-line `acceptance:`  

Else: leave as `signal/` brief with `relevance: watch`.

---

## What not to do

- Infinite chat without writing progress to disk  
- Second full `build/` while Claude owns compile and disk is tight  
- Closing your own messages to Claude  
- Grading your own engine optimization green  
- Spamming &gt;2 handoffs/day  

---

## Related

- Knowledge: `kanban/knowledge/grok-long-harness-and-loops.md`  
- Claude capabilities (parity target): `kanban/knowledge/claude-code-capabilities.md`  
- Federation: `kanban/federation/FEDERATION.md`  
- Daily loop doctrine: `kanban/playbook/04-daily-loop-and-the-dream.md`

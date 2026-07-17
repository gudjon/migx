---
id: runbook-grok-long-harness-loop
type: runbook
title: "Run Grok Build at full capability for long harness loops on Migx"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
pinned_cli: "0.2.102"
defers_to:
  - kanban/knowledge/grok-long-harness-and-loops.md
  - GROK.md
  - kanban/federation/FEDERATION.md
  - kanban/playbook/04-daily-loop-and-the-dream.md
  - .claude/rules/agentic-decision-authority.md
---

# Grok long harness loop (full Build features)

Run **Grok Build** for hours or overnight using the CLI’s native loop substrate (`/goal`, `/loop`,
subagents, worktrees, monitors, compaction-surviving TODOs) **plus** Migx disk/federation SSoT.

Capability map: `kanban/knowledge/grok-long-harness-and-loops.md`.  
**Pinned CLI:** `grok 0.2.102+` (verify with `grok --version`).

---

## Preconditions

```bash
cd ~/code/migx   # or a grok worktree
export MIGX_FED_SIDE=grok-signal
export MIGX_REPO_ROOT="$(git rev-parse --show-toplevel)"
./kanban/scripts/migx-fed doctor
grok --version   # expect ≥ 0.2.100 for multi-CLI resume + full fetch artifacts
```

Prefer a **dedicated worktree** when Claude is compiling:

```bash
# CLI worktree (Build-native)
grok -w --ref main   # or: git worktree add ../migx-grok -b grok/loop-$(date +%Y%m%d)

cd ../migx-grok   # if using git worktree
export MIGX_FED_SIDE=grok-signal MIGX_REPO_ROOT="$(git rev-parse --show-toplevel)"
grok
```

### Operator keybindings (keep open)

| Action | Key / command |
|---|---|
| Tasks pane | `Ctrl+B` |
| Prompt queue | `Ctrl+;` |
| Interject / queue mid-turn | type while waiting; empty Enter sends top queue |
| Bg foreground command | `Ctrl+G` |
| Sessions / dashboard | `/sessions` or `Ctrl+S` |
| Recap after away | `/recap` |
| Context cost | `/context` |
| Plan mode | `/plan` or Shift+Tab |
| Goal | `/goal <obj>` · `/goal status` · `/goal pause` |

---

## Session boot sequence (every long run)

Do this **before** large tool thrash:

1. **Federation poll**
   ```bash
   ./kanban/scripts/migx-fed sync
   ./kanban/scripts/migx-fed poll --to grok-signal
   ```
2. **Disk contract** (restart-proof; see A0 below).
3. **TODOs** — use the built-in todo list for waves (survives compaction).
4. **`/goal`** — one objective string for the whole run.
5. **Optional `/loop` or `monitor`** for unattended cadence.
6. Only then: explore/implement subagents.

---

## Mode A — Signal scout loop (default)

Highest leverage for Grok (X + web tools).

### A0. Disk contract (once per run)

```bash
RUN_ID="scout-$(date -u +%Y%m%dT%H%M%SZ)"
DIR="$MIGX_REPO_ROOT/kanban/federation/scratchpad/$RUN_ID"
mkdir -p "$DIR"
```

`$DIR/contract.md`:

```markdown
# Contract — Grok signal scout
## Goal
Scout X/web for Migx-relevant signal; promote only actionable handoffs.
## In scope
audio/music WM, AI/DJ models, Metal/QML/architecture, Cursor-product, RT techniques, harness engineering
## Out of scope
src/engine RT edits; full native rebuild; >2 handoffs/day
## Done when
- ≥1 signal brief committed OR research-request mail drained
- each handoff has acceptance + Strategy/ADR map
- progress.md NEXT=stop or sleep
## Verify
./kanban/scripts/migx-fed list --status open
ls kanban/federation/signal/ | tail
```

`$DIR/progress.md`:

```markdown
# Progress
- wave: 0
- next: poll federation mail
- blockers: none
```

### A1. Arm the runtime harness

In the Grok TUI (example prompts — adapt `RUN_ID`):

```text
/goal Scout Migx signal for RUN=scout-…; drain research-request mail; 0–2 handoffs; keep progress.md current; stop when NEXT=stop

/loop 4h One Mode A wave for RUN=scout-… per kanban/runbooks/grok-long-harness-loop.md: poll fed, scout X/web, write signal brief if warranted, update progress, commit federation paths
```

Optional CI/PR soak while scouting:

```text
Monitor: gh pr checks <n> every 60s with line-buffered grep for fail/success only (persistent)
```

### A2. One wave (model or loop firing)

Load into context **only**:

1. `GROK.md` + role (stable)  
2. `$DIR/contract.md`  
3. Tail of `$DIR/progress.md`  
4. `migx-fed poll --to grok-signal`  

Then:

```text
1. Drain research-request / question mail
2. Scout (x_semantic_search / x_keyword_search / web_search / web_fetch)
   — for long pages, use session web_fetch artifacts (0.2.100+)
3. Write kanban/federation/signal/YYYY-MM-DD-<slug>.md
4. Optional: migx-fed send signal-handoff (≤2/day)
5. Append progress.md: wave N, landed, NEXT=
6. Commit federation paths
7. update_goal progress; if NEXT=stop → complete goal
```

### A3. Unattended decisions

Same cascade as Claude (`.claude/rules/agentic-decision-authority.md`):

- Confidence ≥ 0.4 → decide, write progress/journal, continue  
- Irreversible → stop and surface  
- Value judgment → flag owner, continue other work  

### A4. Headless one-wave (cron / tmux)

```bash
# Headless waits for background tasks/subagents before exit (≥0.2.58)
grok -p --permission-mode auto \
  "Read kanban/runbooks/grok-long-harness-loop.md Mode A. RUN_ID=$RUN_ID. Execute exactly one wave. Update progress.md. Commit federation paths only. Exit."
```

---

## Mode B — Generator loop (bounded non-RT coding)

### B0. Plan first when ambiguous

```text
/plan
# agent writes plan file only — edits elsewhere rejected even under always-approve
# approve with 'a' when sound
```

### B1. Goal + parallel subagents

```text
/goal <one-wave outcome with acceptance line>

# Parent should:
# 1. spawn_subagent explore, background, read-only — map call sites
# 2. spawn_subagent general-purpose, isolation=worktree — implement
# 3. spawn_subagent explore/read-only OR /check-work — independent review (P-08)
# 4. pre-commit run --files <changed>
# 5. ctest -R <filter> if needed
# 6. commit; update progress; complete goal
```

**Never** self-seal a perf/RT claim. Hand to Claude/Codex for MTL/EVD.

### B2. resume_from chain

```text
research subagent finishes → spawn implementer with resume_from=<id>
  (same agent type; continues transcript in place)
```

---

## Mode C — Product federation day

| Time | Grok Build | Claude | Codex |
|---|---|---|---|
| Start | fed poll + `/goal` day objective | fed poll | fed poll |
| Day | Mode A and/or B; `/loop` scout | engine/UI implement | verify / map |
| Cross-CLI | `/sessions` resume Claude/Codex if needed (0.2.100+) | — | — |
| Handoff | `signal-handoff` commits | ack → dossier/task | evidence |
| Away | leave goal + progress; monitors | — | — |
| Return | `/recap` + fed poll | journal | close mail |

Worktrees separate; **git + federation** = shared long memory.

---

## Compaction mid-run (do not panic)

1. TODOs and background task IDs **survive** — keep driving from the todo list.  
2. After fold: re-read `contract.md` + tail `progress.md` if model drifts.  
3. Human: `/recap` instead of scrolling the whole transcript.  
4. Large fetches already on disk under session `web_fetch/` — re-`read_file` artifacts.  
5. Prefer commit + short wave over fighting context size.

---

## Restart after crash / context death

```bash
# 1. latest disk run
ls -1dt kanban/federation/scratchpad/scout-* 2>/dev/null | head -1
# 2. read contract + progress only
# 3. grok --resume <session> if TUI session still useful
# 4. else: new session, /goal from contract, continue NEXT=
# 5. always: migx-fed poll — messages/ are cross-agent SSoT
```

---

## Quality gates

### Scout handoff invalid unless

- [ ] Evidence links (X/post/web)  
- [ ] Mapped to Strategy pillar or ADR-005 layer  
- [ ] `## Requested Action` doable in one peer wave **or** “file task/dossier”  
- [ ] One-line `acceptance:`  

Else: `signal/` brief with `relevance: watch` only.

### Generator wave

- [ ] `pre-commit run --files <changed>`  
- [ ] Targeted tests if behavior changed  
- [ ] Independent review for non-trivial / any engine-adjacent change  
- [ ] No RT alloc/lock/GUI on callback paths (`P-02`)  

---

## What not to do

- Infinite chat without disk progress + goal/todos  
- Second full `build/` while Claude owns compile and disk is tight  
- Closing your own messages to Claude  
- Grading your own engine optimization green (`P-08`)  
- Spamming >2 signal handoffs/day  
- Raw `tail -f` monitors without `grep --line-buffered` (event flood → monitor kill)  
- Plan-mode implementation edits before approval  
- Force-push / destructive git without explicit owner request  

---

## Quick reference — feature → Migx action

| Build feature | Migx action |
|---|---|
| `/goal` | Arm the long objective; `update_goal` each wave |
| `/loop` | Unattended scout / CI cadence |
| `monitor` | Soak, PR checks, log ERROR lines only |
| `spawn_subagent` + worktree | Parallel implement without clobber |
| `explore` subagent | Map before touch |
| Plan mode | Ambiguous architecture |
| TODOs | Wave checklist across compaction |
| `/recap` | Human return |
| Multi-CLI resume | Pick up Claude/Codex session |
| `web_fetch` artifacts | Deep doc/changelog analysis |
| X tools | Mode A signal |
| Headless `-p` | Cron one-wave |
| `/check-work` / review | Independent eval |

---

## Related

- Knowledge: `kanban/knowledge/grok-long-harness-and-loops.md`  
- Entry: `GROK.md`  
- Claude capabilities: `kanban/knowledge/claude-code-capabilities.md`  
- Federation: `kanban/federation/FEDERATION.md`  
- Daily loop: `kanban/playbook/04-daily-loop-and-the-dream.md`  
- Changelog: https://x.ai/build/changelog  
- Local docs: `~/.grok/docs/user-guide/`

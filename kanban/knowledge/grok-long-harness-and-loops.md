---
id: grok-long-harness-and-loops
type: knowledge
title: "Grok Build full capability + long harness (changelog-grounded)"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
pinned_cli: "0.2.102 (ab5ebf69acec)"
changelog_through: "0.2.101 (x.ai/build/changelog, Jul 2026)"
sources:
  - "https://x.ai/build/changelog (v0.2.27–0.2.101+)"
  - "~/.grok/docs/user-guide/ (local install docs)"
  - "X discourse 2026-06..2026-07: harness > model; loop engineering"
  - "kanban/knowledge/claude-code-capabilities.md"
  - "kanban/federation/FEDERATION.md"
defers_to:
  - kanban/runbooks/grok-long-harness-loop.md
  - kanban/playbook/03-harness-engineering-outer-ring.md
  - kanban/playbook/04-daily-loop-and-the-dream.md
  - GROK.md
---

# Grok Build — full capability + long harness

How to run **Grok Build CLI** at full feature depth on Migx for multi-hour / overnight closed
loops. Grounded in the public [changelog](https://x.ai/build/changelog) through **v0.2.101** and
local docs at `~/.grok/docs/user-guide/`. **Pinned local binary:** `grok 0.2.102`.

**SSoT for *how to run it*:** [`kanban/runbooks/grok-long-harness-loop.md`](../runbooks/grok-long-harness-loop.md).  
This note is the **capability map + architecture**. Older “Grok has no /loop” framing is **obsolete**.

---

## 0. What changed (honest upgrade from earlier Migx notes)

| Earlier assumption (outdated) | Reality as of 0.2.100+ |
|---|---|
| Grok lacks Claude-like `/loop` | **Native `/loop` + `scheduler_*` + `monitor`** (user-guide 20) |
| Subagents “when available” | **Shipped:** `spawn_subagent`, default **background**, worktree isolation, `resume_from`, optional `model` |
| Only disk contracts for long runs | Disk contracts **plus** `/goal`, compaction-surviving TODOs/bg tasks, `/recap` |
| Multi-CLI is manual | Session picker resumes **Claude Code / Codex / Cursor** sessions (0.2.100) |
| Compaction kills long work | Bg tasks + TODOs **survive compaction** (0.2.80); headless waits for bg (0.2.58) |

**Still true (do not drop):** durable Migx state lives in **git + federation + dossiers**. Grok Build
session memory is a *runtime substrate*; the repo remains SSoT after the TUI exits.

---

## 1. Capability matrix (long-harness relevant)

### 1.1 Autonomy & loop primitives

| Feature | How | Changelog / doc | Migx use |
|---|---|---|---|
| **`/goal <objective>`** | Multi-turn autonomous progress via `update_goal` | 0.2.61–0.2.94; slash-commands | Overnight dossier wave / soak objective |
| **`/loop <interval> <prompt>`** | Recurring agent turns (min 60s; auto-expire 7d; max 50) | user-guide 20 | Scout every 4h; CI poll; fed poll |
| **`scheduler_create`** | Same as `/loop`; `durable`, `fire_immediately`, one-shot | user-guide 20 | Durable scout after restart |
| **`monitor`** | Stream stdout lines → chat events; `persistent: true` | 0.2.38+; 0.2.82 wake-on-exit | PR/CI/log soak without blocking |
| **Headless `grok -p`** | Waits for bg tasks/subagents before exit (0.2.58); JSON schema | 0.2.58, 0.2.67 | Cron one-wave scout |

### 1.2 Parallelism & isolation

| Feature | How | Notes | Migx use |
|---|---|---|---|
| **Subagents** | `spawn_subagent` → explore / plan / general-purpose (+ project agents) | **Background by default** (0.2.85); optional `model` (0.2.98) | explore codebase; plan wave; implement in worktree |
| **`isolation: worktree`** | Child git worktree; path returned | Dashboard `Ctrl+W`; `grok -w --ref` (0.2.65) | Parallel waves without clobbering Claude |
| **`resume_from`** | Continue finished subagent in place (not fork) | 0.2.56 | research → implement chain |
| **Capability modes** | `read-only` / `read-write` / `execute` / `all` | user-guide 16 | P-08: read-only evaluator vs generator |
| **Personas / roles** | `.grok/personas/`, `.grok/roles/`, config.toml | I/O contracts for chaining | `researcher` → `reviewer` chains |

### 1.3 Planning & mode control

| Feature | How | Notes | Migx use |
|---|---|---|---|
| **Plan mode** | `/plan`, Shift+Tab, `enter_plan_mode` | **Edits outside plan file rejected even under always-approve** (0.2.98) | Ambiguous refactors before code |
| **Plan file** | Session `plan.md` (default `.grok/plan.md` convention 0.2.89) | Survives compaction with reminder | Wave plan before RT-adjacent work |
| **`/effort`** | Reasoning effort mid-session | 0.2.82; rejects unsupported levels 0.2.96 | Deep analysis waves vs mechanical |
| **Permission modes** | Auto default in Shift+Tab (0.2.76); `/auto`, `/always-approve` | Fleet remote + managed_config | Unattended long runs: auto + deny globs |

### 1.4 Long-session survival

| Feature | How | Why it matters |
|---|---|---|
| **Bg tasks survive compaction** | 0.2.80 | Overnight compile/soak not lost at context fold |
| **TODOs survive compaction** | 0.2.62, 0.2.80 | Wave checklist survives `/compact` |
| **Compaction prep in background** | 0.2.79 | Less freeze mid-harness |
| **Reject short compaction summaries** | 0.2.52 | Prevents “empty brain” after fold |
| **`/recap`** | Default (0.2.62); collapsible block 0.2.64 | Human return-from-away without replaying transcript |
| **Queue + interject** | Type while waiting; Enter sends top queue; double-Enter / chord cancels wait | Steer long run without killing it |
| **Double-Esc rewind / Ctrl+C cancel** | Esc no longer cancels turn (0.2.93 era) | Safer navigation during long turns |
| **Memory flush pre-compact** | user-guide 13 | Durable facts → MEMORY before fold |
| **Date-change notice** | 0.2.52 | Long overnight sessions see calendar rollover |

### 1.5 Research / signal tools (Grok-native edge)

| Feature | How | Migx use |
|---|---|---|
| **X search** | `x_semantic_search`, `x_keyword_search`, `x_thread_fetch`, `x_user_search` | Default **grok-signal** role |
| **Web** | `web_search`, `web_fetch` | Architecture / Apple / Spotify research |
| **Truncated fetch → artifact** | 0.2.100 full page saved under session `web_fetch/` | Deep changelog/docs analysis without silent clip |
| **Citations** | Inline render from web/X results | Signal briefs with provenance |

### 1.6 Multi-CLI federation surface

| Feature | Version | Migx use |
|---|---|---|
| Resume **Claude Code / Codex / Cursor** sessions from picker | 0.2.100 | Continue peer work without re-brief |
| `grok inspect` compatibility settings for those CLIs | 0.2.101 | Debug “which session am I in” |
| Welcome one-click resume nudge | 0.2.100 | Fast handoff morning |

### 1.7 Tooling quality for monorepos

| Feature | Version | Why for Migx |
|---|---|---|
| `rg` auto-approved by default | 0.2.97 | Fast grep without permission thrash |
| Grep early-stop / timeout | 0.2.81, 0.2.84 | Large C++ tree |
| `read_file` full single-line (minified JSON) | 0.2.94 | EXO fixtures |
| MCP large results → disk + auto-recover HTTP | 0.2.55–0.2.97 | Slack/Linear connectors stable |
| Sandbox deny globs (`**/*.pem`) | 0.2.66 | Secrets hygiene |
| `remote_fetch` disable for airgap | 0.2.84 | Offline cabin mode |
| Project skills discovered even if gitignored | 0.2.85 | Local skill experiments |
| Bundled **check-work / review / execute-plan** skills | install skills | P-08 independent eval path |

### 1.8 UX operators should know mid-harness

| Action | Binding / command |
|---|---|
| Tasks pane (subagents, bg, monitors) | `Ctrl+B` |
| Prompt queue | `Ctrl+;` (or `Ctrl+4` on some terminals) |
| Interject mid-turn | `Ctrl+L` (editor terminals); type + queue |
| Bg a stuck foreground cmd | `Ctrl+G` |
| Session picker / dashboard | `/sessions`, `Ctrl+S` |
| Context cost (skills + MCP) | `/context` (0.2.98) |
| Recap | `/recap` |
| Code review skill | `/code-review` (0.2.51) |
| Docs browser | `/docs` (0.2.87) |

---

## 2. Long-harness architecture (full Grok Build)

```text
                    ┌─────────────────────────────────────────┐
                    │  Parent session (Grok 4.5 / grok-build) │
                    │  /goal  ·  todos  ·  contract on disk   │
                    └────────────┬────────────────────────────┘
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼
    spawn explore          spawn general-purpose    /loop or monitor
    (read-only map)        isolation:worktree       (scout / CI / soak)
           │                     │                     │
           ▼                     ▼                     ▼
    research brief          implement wave          event stream
           │                     │                     │
           └──────────► resume_from / merge ◄──────────┘
                              │
                    pre-commit · ctest · P-08 peer
                              │
                    git + migx-fed (durable SSoT)
```

### Three layers (all required for “long”)

1. **Runtime substrate (Grok Build)** — goal, subagents, bg tasks, loop/monitor, compaction survival.  
2. **Disk contract (Migx)** — `contract.md` / `progress.md` / federation mail (survives process death).  
3. **Verification (house physics)** — pre-commit, ctest, benches, **independent evaluator** (`P-08`).

Dropping layer 2 reverts to chat that dies with the TUI. Dropping layer 3 is green-over-red (`AP-01`).

---

## 3. Migx loop modes (updated)

### Mode A — Signal scout (default `grok-signal`)

**Best Grok edge:** X tools + web_fetch artifacts.

```text
/goal "Scout Migx-relevant signal; 0–2 handoffs/day; state on disk"
  → /loop 4h "One Mode A wave per runbook RUN=$RUN_ID"
  → optional monitor on gh/ci if a PR is open
```

Outputs: `kanban/federation/signal/*.md`, `migx-fed` handoffs. No second full native build.

### Mode B — Bounded generator (non-RT code)

```text
/plan → approve → /goal wave objective
  → spawn explore (map) → spawn general-purpose isolation:worktree (impl)
  → check-work / independent review → pre-commit → commit → progress.md
```

Evaluator ≠ generator: Codex or Claude grades engine/perf; Grok may grade docs/QML chrome only with
an independent subagent review.

### Mode C — Fleet tandem (product day)

| Peer | Runtime | Role |
|---|---|---|
| **Grok** | this CLI | signal, research, docs, non-RT waves, federation mail |
| **Claude** | Claude Code (resumable from Grok picker) | MTL/engine implement loop |
| **Codex** | Codex (resumable) | verify / map / steward |
| **AGY** | paused | no tokens |

Git + `migx-fed` remain the **cross-process memory**. Multi-CLI resume is a convenience, not a
replacement for federation mail.

---

## 4. Compaction strategy (runtime + disk)

### Runtime (Grok Build auto)

1. TODOs + background task IDs survive fold — **keep using them**.  
2. After auto-compact: `/recap` if human-present; model sees surviving TODO list.  
3. Large MCP/web results land on disk (read on demand) — don’t re-fetch full trees into context.  
4. Prefer **short waves** that commit to git before context pressure rises.

### Disk (Migx, restart-proof)

Every long run still maintains:

| File | Purpose |
|---|---|
| `kanban/federation/scratchpad/<run-id>/contract.md` | Done criteria, out of scope |
| `…/progress.md` | Last wave, NEXT=, blockers |
| `…/journal.md` | Append-only decisions |

**Restart after death:** read contract + progress + `migx-fed poll` — not the multi-GB transcript.

---

## 5. Verification ladder (any Grok generator wave)

```text
pre-commit --files <changed>
  → ctest -R <filter>
  → bench delta if perf (P-03 / P-18)
  → independent review (spawn read-only / Codex / /check-work)
  → never self-seal RT/perf (P-08)
```

Scout ladder:

```text
Strategy/ADR map → evidence (X/web) → handoff acceptance line → Claude/Codex ack
```

---

## 6. Gap analysis vs Claude Code (current)

| Capability | Claude Code | Grok Build 0.2.100+ | Migx note |
|---|---|---|---|
| Recurring loop | `/loop`, `/schedule` | **`/loop` + scheduler + monitor** | Parity for unattended |
| Goal / multi-turn objective | agentic loops | **`/goal` + `update_goal`** | Use for overnight |
| Subagents + worktrees | Agent tool | **spawn + isolation:worktree** | Parity |
| Plan mode | Plan mode | **Strict plan-file-only** | Strong |
| Hooks | rich lifecycle | Pre/PostCompact, host hooks, plugins | Use for memory flush |
| Project skills | `.claude/skills` | `.grok` + plugins + gitignored discovery | Map pat-* into prompts or skills |
| X-native research | limited | **first-class X tools** | Grok wins Mode A |
| Multi-CLI resume | n/a | **Claude/Codex/Cursor** | Fleet glue |
| Federation SSoT | CLAUDE.md patterns | same disk via `migx-fed` | Shared |

**Do not under-use the CLI.** Under-using Grok Build as a chat box wastes the harness Migx already
shares with Claude.

---

## 7. Operational defaults for Migx Grok sessions

1. **Session start:** `GROK.md` checklist + `migx-fed poll` (always).  
2. **Long run (>2 waves):** `/goal` + disk contract + TODOs.  
3. **Ambiguous architecture:** plan mode first (strict).  
4. **Parallel map/impl:** explore (bg) + worktree implementer; merge after gate.  
5. **Scout cadence:** `/loop 4h` or headless cron with `-p` + wait-for-bg.  
6. **Soak/CI:** `monitor` with line-buffered filters, not raw logs.  
7. **Context pressure:** commit → update progress → let compaction run; rely on TODOs.  
8. **Human away:** leave `/goal` + progress; on return `/recap` + `migx-fed poll`.  
9. **RT paths:** prefer Claude implement; Grok may research/map only unless reassigned.  
10. **Always:** house physics (P-02/P-06/P-08) bind regardless of permission mode.

---

## 8. Version pin & refresh

| Item | Value |
|---|---|
| Local binary checked | `grok 0.2.102 (ab5ebf69acec)` |
| Public changelog through | **0.2.101** (2026-07-13) on x.ai/build/changelog |
| Local docs | `~/.grok/docs/user-guide/` |
| Refresh policy | Re-read changelog on major minor bumps; re-pin `pinned_cli` here |

Upgrade: `curl -fsSL https://x.ai/cli/install.sh | bash` or `grok update`.

---

## 9. X / field themes (non-normative, still useful)

- Harness > model: tools, compaction, permissions, disk memory, subagents.  
- Loop engineering: contract → act → verify → short restart, not infinite transcript.  
- Multi-model fleets: Claude implement, Grok signal, Codex verify.  
- Grok’s durable product edge inside coding agents: **live X + research tools**.

Re-scout quarterly; the **capability matrix** above is the load-bearing part of this note.

---

## 10. Related

- Runbook (SOP): `kanban/runbooks/grok-long-harness-loop.md`  
- Entry routing: `GROK.md`  
- Claude parity target: `kanban/knowledge/claude-code-capabilities.md`  
- Federation: `kanban/federation/FEDERATION.md`  
- Multi-agent worktrees: `kanban/runbooks/multi-agent-parallel-sessions.md`

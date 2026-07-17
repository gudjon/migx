---
id: grok-long-harness-and-loops
type: knowledge
title: "Grok 4.5 in a long harness / loop — X signal + Migx mapping (vs Claude Code)"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
sources:
  - "X discourse 2026-06..2026-07: harness > model; loop engineering; Karpathy LOOPS.md summaries; Grok Build CLI; multi-model worker pattern"
  - "kanban/knowledge/claude-code-capabilities.md"
  - "kanban/federation/FEDERATION.md"
defers_to:
  - kanban/playbook/03-harness-engineering-outer-ring.md
  - kanban/playbook/04-daily-loop-and-the-dream.md
  - kanban/Strategy-Current.md
  - GROK.md
---

# Grok 4.5 in a long harness (Claude-Code-shaped loops)

How **Grok 4.5 + Grok CLI / Grok Build** can run *long, closed loops* on Migx the way Claude Code
does — distilled from **trending X signal** and mapped onto this repo’s tool-agnostic harness.

**SSoT for *how to run it*:** [`kanban/runbooks/grok-long-harness-loop.md`](../runbooks/grok-long-harness-loop.md).  
This note is the **research + architecture map**.

---

## 1. What X is saying (2026 signal)

### 1.1 Harness > model
Dominant consensus: a coding agent is **LLM → agent → agent harness → coding harness**. The “dumb
loop” (perceive → act → observe) is simple; **intelligence lives outside the weights** — tools,
compaction, permissions, memory on disk, subagents, verification gates.

Claude Code teardown themes (widely shared):

| Harness piece | Why it matters for long runs |
|---|---|
| Async generator / streaming loop | Events stream; abort/nest mid-run |
| Streaming tool start | Tools fire before the model finishes talking |
| Parallel read tools / serial writes | Speed without race conditions |
| Layered context compaction | Micro-cache → snip → summarize → collapse |
| Permission rule engine | Not a single toggle — progressive trust |
| Error recovery *as the loop* | Retry, backoff, fallback, heartbeat for unattended |
| Skills + hooks + MCP | Extend by dropping files, not forking the binary |
| Subagents + worktrees | Parallel work without clobbering |

**Implication for Grok:** Grok 4.5’s edge (reasoning, coding, low-refusal, X-native tools) only
compounds if we give it the **same external loop substrate** Migx already built for Claude — not if
we use it as a chat box.

### 1.2 Loop engineering (not prompt engineering)
Karpathy-style field notes (circulating as LOOPS.md summaries on X):

1. **Write the loop, not the prompt** — short cycles: gather → reason → act → verify → repeat.  
2. **Separate roles** — Planner / Generator / Evaluator; never one agent grading its own work (`P-08`).  
3. **Contract on disk first** — what “done” looks like, before code.  
4. **State in files** — `progress.md`, contract, logs; never rely on chat context alone.  
5. **Clean restart** — recover by reading 3 files, not replaying a 6-hour transcript.  
6. **Evaluator outside the generator** — tests, benches, rubrics, second agent.  
7. **Delete scaffolding as models improve** — bottleneck moves; fix the current one.

Hasan Toor / “Loop Engineering” framing: daily triage, PR babysit, CI sweep, dependency sweep —
**systems that prompt the agent**, not humans pasting prompts.

### 1.3 Grok 4.5 / Grok Build specifically
From recent X (incl. @grok and builders):

- **Grok Build** — terminal coding agent / TUI + agent runtime (ecosystem around Grok 4.5: tools,
  memory, self-correction; SuperGrok-tied in some launches).  
- **Grok 4.5** positioned as agentic reasoning + coding; “full ecosystem” (tools, memory, deployment,
  self-correction loops) is the unlock, not the base model alone.  
- **Multi-model fleets** are normal: Claude as orchestrator, Grok (or others) as workers in worktrees;
  or Grok as specialist (signal, low-refusal analysis) while Claude implements.  
- **CLI agent per model** is an emerging pattern (each frontier model gets a CLI; harness is shared).  
- Grok’s unique native advantage: **X search / real-time social signal** — no other coding CLI has
  first-class trending discourse tools for architecture and research.

### 1.4 What “long harness like Claude Code” actually means
Not “same binary.” It means the same **closed-loop properties**:

| Property | Claude Code native | Grok on Migx (this harness) |
|---|---|---|
| Durable memory | CLAUDE.md, MEMORY, session | `AGENTS.md`, `GROK.md`, kanban/, federation mail |
| Loop primitive | `/loop`, `/schedule`, workflows | **Disk-backed scout/impl loops** + `migx-fed` + cron/tmux |
| Subagents | Agent tool + worktrees | Worktrees + federation peers + optional subagents in Grok Build |
| Verification | hooks, tests, Stop hooks | `pre-commit`, `ctest`, EVD benches, second peer review |
| Unattended decisions | agentic-decision-authority cascade | Same cascade in `GROK.md` / doctrine |
| Multi-agent | teams / mailboxes | **`migx-fed`** (git-mediated) |

---

## 2. Migx mapping — two Grok loop modes

### Mode A — Signal scout loop (default role `grok-signal`)
**Best fit for Grok 4.5** (X tools + research).

```text
poll fed mail → scout X/web → write signal/ brief → (optional) handoff → commit → sleep → repeat
```

- Cadence: daily or on `research-request`  
- Output: `kanban/federation/signal/*.md` + 0–2 handoffs  
- Does **not** need a second full native build  
- Verifier: quality bar in `roles/grok-signal.md` (actionable? thesis-mapped? evidence?)

### Mode B — Bounded generator loop (optional, when Grok codes)
When Grok implements (docs, QML, non-RT paths):

```text
read contract → wave implement → pre-commit / tests → journal → commit → next wave
```

- Same dossier waves as Claude (`90-EXECUTION`)  
- Own worktree + branch  
- **Evaluator ≠ generator:** Claude or human runs adversarial review / benches for engine claims  
- Prefer Claude for `src/engine/` RT paths until Grok loop has proven RT discipline

### Mode C — Dual-peer long harness (recommended product tandem)
```text
┌──────────────┐  signal-handoff / research-request  ┌────────────────┐
│ Grok 4.5     │ ──────────────────────────────────► │ Claude Code    │
│ scout + loop │ ◄────────────────────────────────── │ implement loop │
└──────────────┘         migx-fed + git               └────────────────┘
        │                                                        │
        └──── shared brain: AGENTS.md, Strategy, dossiers ───────┘
```

Claude owns MTL/engine `/loop`. Grok owns field signal + research requests in parallel. **Git is the
session memory both can restart from.**

---

## 3. Disk-backed loop contract (Grok-compatible LOOPS.md)

Every long Grok run writes three files (restart = read these):

| File | Purpose |
|---|---|
| `kanban/federation/scratchpad/<run-id>/contract.md` | Done criteria, out of scope, tools allowed |
| `…/progress.md` | Last wave, next action, blockers |
| `…/journal.md` | Append-only decisions |

`scratchpad/` is **gitignored** for local thrash; promote durable outcomes to `signal/`, tasks, or
dossiers (committed).

Template shape lives in the runbook.

---

## 4. Compaction strategy for Grok sessions

X consensus: don’t dump full history into every turn. For Grok CLI / Grok Build:

1. **Stable prefix:** `GROK.md` + `AGENTS.md` + role charter (cacheable mental model).  
2. **Session state:** only `contract.md` + last 30 lines of `progress.md`.  
3. **Evidence on demand:** open specific signal briefs / files — not the whole `kanban/`.  
4. **Promote then forget:** after a handoff commits, next turn starts from poll + progress, not the
   entire scout transcript.

---

## 5. Verification ladder (shared with Claude)

Playbook ch.03 ladder applies to any Grok generator wave:

```text
pre-commit on changed files → targeted ctest → bench delta (if perf) → full build → adversarial review
```

Grok scout waves use a lighter ladder:

```text
thesis map (Strategy / ADR) → evidence links → handoff acceptance line → Claude ack/close
```

---

## 6. Gaps vs Claude Code (honest)

| Claude Code has | Grok path today on Migx |
|---|---|
| `/loop` + `/schedule` cloud | Manual/tmux/cron + disk contract; wire later |
| Native subagent fan-out | Worktrees + `migx-fed`; Grok Build subagents when available |
| Stop/SubagentStop hooks | Session checklist + federation poll |
| pat-* auto skills | Cite patterns by ID in prompts; optional future Grok skills dir |
| Deep project hooks | Rely on shared `kanban/` + house physics docs |

**Do not wait for feature parity.** Disk + federation + worktrees already make multi-hour/day loops
possible. Native loop UX is sugar on top.

---

## 7. Recommendations for Migx (actionable)

1. **Default Grok to Mode A** (signal scout loop) — highest leverage unique to Grok 4.5.  
2. **Always start with contract on disk** for any run &gt; 2 waves.  
3. **Claude evaluates engine/perf claims** even if Grok proposed them (`P-08`).  
4. **Wire `TR-grok-signal-scout`** when a clock exists (cron / tmux / Grok Build schedule).  
5. **One handoff quality bar** — no spam; 0–2 promotes per scout day.  
6. Under **MIT operating model**, Grok may also research closed-product / freemium / privacy patterns
   without open-core-only self-censorship.

---

## 8. X provenance (illustrative, non-normative)

Themes only — not endorsement of any third-party repo:

- Claude Code as multi-layer harness (loop, compaction, permissions, subagents, hooks)  
- Loop engineering / LOOPS.md-style persistence  
- Multi-model: Claude orchestrates, other CLIs (incl. Grok) as workers  
- Grok Build + Grok 4.5 agentic ecosystem messaging  
- Grok’s native advantage: live X/research tools inside the coding agent  

Re-scout quarterly; this note’s *mapping* to Migx is the durable part.

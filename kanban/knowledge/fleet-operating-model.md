---
id: fleet-operating-model
type: knowledge
title: "Fleet operating model — Claude · Codex · Grok (AGY paused) toward AI-DJing"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/Strategy-Current.md
  - kanban/federation/FEDERATION.md
  - kanban/playbook/04-daily-loop-and-the-dream.md
sources:
  - "X mid-2026: harness>model; loop engineering; Agent Teams; multi-CLI fleets; verified tasks per token"
---

# Fleet operating model (Claude · Codex · Grok)

How the coding/agent CLIs on this box map to Migx’s endgame, what is still missing, and how to
run them **autonomously** without thrash.

**2026-07-17:** Antigravity (`agy` / `antigravity-cli`) is **paused** — no subscription tokens.
Non-RT/UI/ontology volume → Claude. Re-enable: `AGY.md` + `peers.yaml` `status: active`.

## Endgame (north stars)

1. **Instrument (Layer A):** blazingly fast on Apple Silicon — Metal, DSP, zero underruns (`initiative-apple-silicon`).  
2. **Agent seams (Layer B):** session mirror, ontology, intent inbox — deep permission like Cursor.  
3. **Intelligence (Layer C):** multi-model co-pilot, freemium, privacy (`ADR-005`, MIT operating model).  
4. **Product home:** public early → later under agora.

The fleet builds **the product and the product’s co-pilot substrate** — not generic SaaS.

## What you already have (strong)

| Peer | Job | Best at | Status |
|---|---|---|---|
| **Claude Code** | Primary implementer | RT/C++/Qt + non-RT product while AGY paused | **active** |
| **Codex CLI** | Verifier-cartographer | Trace, tests, harness, P-08 independent eval | **active** |
| **Grok** | Signal scout | Live X + web field intel, architecture trends | **active** |
| **AGY** | (dormant co-implementer) | Was: multi-agent non-RT volume | **paused** |

**Federation** (`migx-fed` + worktrees + roles) is the right substrate: git-mediated mail, pull delivery,
one owner per path. That is already more mature than most “four terminals, no protocol” setups on X.

## What’s missing (critical gaps)

Ordered by leverage for *autonomous perfect software* toward the endgame:

### 1. Orchestrator / night loop (most critical)
**Gap:** No single process that wakes, reads open mail + board, assigns the next wave, and sleeps.  
Humans still start four CLIs. X calls this **loop engineering** (discover → plan → execute → verify →
iterate) and “verified tasks per token,” not more chat.

**Add:** A thin **fleet conductor** (script or Claude `/schedule` + tmux):

```text
every N min / nightly:
  git pull shared branch
  migx-fed list --status open
  derive: who is blocked, who has open acceptance
  spawn or nudge: only the DRI for the highest-priority open mail
  on green gate: close mail + journal
```

Does **not** need a fifth LLM at first — a shell + `migx-fed` + cron is enough.

### 2. Always-on independent evaluator (you have the role; wire the clock)
**Gap:** Codex is the P-08 peer, but evaluation is ad hoc. X: generator ≠ evaluator; loops die without
external proof.

**Add:** Standing rule — every merge-candidate for **engine/perf/EXO acceptance** opens or requires a
`coord` to `codex-cli` with a frozen command list. Optional: `migx-fed listen --to codex-cli`.

### 3. Model router policy (explicit, written)
**Gap:** Peers are fixed tools; no written policy for *which model for which wave* (AGY model
routing is moot while paused).

**Add:** One table in this file (below); when AGY returns, restore Flash vs Pro defaults.

### 4. Repo evidence compiler (context efficiency)
**Gap:** Each agent re-loads the repo. X trend: **index once, pass deltas** — symbol graph, test-impact,
evidence packets — so models are commoditized.

**Add (later):** clangd/`compile_commands` already; optional `codebase-researcher` subagent dumps;
dossier `00-RESEARCH` as the evidence packet. Not a new CLI peer — a **artifact type**.

### 5. Product co-pilot dogfood loop (endgame-specific)
**Gap:** Fleet builds Migx; nothing yet **runs the AI-DJing co-pilot against a live or mirrored set**
as a closed loop (suggestion → accept via CO → outcome).

**Add:** After EXO P-08: a tiny **session-mirror file + intent JSON** exercised by any agent offline
(no RT). That is the Cursor “Composer for DJ” dogfood.

### 6. What you do *not* need as a fifth peer
- Another general coding CLI (Cursor IDE) as a federated peer — optional human tool, not mail identity.  
- A dedicated “planner-only” model — use Claude plan before implement (AGY plan mode when re-enabled).  
- Slack/MCP between agents — git is enough.

## X trends (last days / mid-2026) that matter here

| Trend | Implication for Migx |
|---|---|
| **Harness > model** | Keep investing in `kanban/` + `migx-fed` + dossiers, not swapping Claude for “hotter” models weekly |
| **Loop engineering** | Write loops that re-prompt; contracts on disk; restart from 3 files |
| **Agent Teams** | When AGY returns: internal subagents; until then Claude subagents + federation |
| **Multi-CLI inside one harness** | Keep **git federation** for multi-vendor peers (Claude · Codex · Grok active) |
| **Autopilot / ralph / persistence** | OK only behind acceptance + verify; never unbounded on `src/engine` |
| **Verified tasks / MTok** | Gate waves on `pre-commit`, `ctest -R`, EVD, not “agent said done” |
| **Commoditize models** | Federation roles outlive any one vendor |

## How to get the best of each model

| Peer | Do | Don’t |
|---|---|---|
| **Claude** | RT/MTL **and** DUI/EXO/product while AGY paused; seal perf with benches | Self-seal P-08 without Codex |
| **Codex** | Cartography, P-08, harness scripts, “is this claim true in tree?” | Compete for Claude’s open wave files |
| **Grok** | Daily/overnight X scout; handoff only if actionable | Write engine code by default |
| **AGY** | *Paused* — re-enable for non-RT volume when tokens return | Address new open mail while paused |

## Autonomous day / night operating system

### Day (human in the loop lightly)
```text
09:00  Gudjon: read migx-fed list --status open + active dossier JOURNALs
       Priority order: (1) red gates / underruns (2) open high mail (3) north-star dossiers
09:15  Start only the DRIs needed (Claude / Codex / Grok — not AGY while paused)
       Claude for implement; Grok if research-request; Codex if P-08 pending
All day  Each peer: poll → wave → commit → close mail
EOD     One conductor note in kanban/ or JOURNAL: what closed, what’s blocked
```

### Night (unattended)
```text
Claude  /loop or schedule: MTL/bench delta only if machine free + disk OK
Grok    long scout loop (disk contract) 1–2 waves; ≤2 handoffs
Codex   listen or single wake: drain P-08 / verify mails
Conductor shell: list open → if EXO P-08 open and fixtures unchanged, nudge codex only
# AGY: do not schedule while peers.yaml status=paused
```

### Golden rules for autonomy
1. **Contract before code** (acceptance in PS or mail).  
2. **One owner per path** (worktrees).  
3. **Generator ≠ evaluator** (Codex/human for seal).  
4. **Evidence on disk** (EVD, JOURNAL, closed mail Resolution).  
5. **House physics never optional** (P-02, P-06, P-20).  
6. **Commoditize the model; own the harness** (federation + kanban).

## “Perfect software” for Migx = closed loops on the product

Not infinite agent lines of code. Score progress as:

| Loop | Green looks like |
|---|---|
| Perf | EVD p99/max + zero underruns vs baseline |
| UI tokens | `gen_theme_from_design.py --check` green |
| Ontology | Agent transition proof + **independent** P-08 |
| Co-pilot | Intent file → CO path (later) with no RT violation |
| Fleet | Open mail age &lt; 48h; no dual writers; weekly scout |

## Critical additions checklist (build these, not more peers)

- [x] **Fleet conductor** — `kanban/scripts/migx-fleet-conductor.py` + `just fleet`  
- [x] **Codex seal drain** — `migx-codex-drain.py` + `just fleet-drain` (EXO P-08 first)  
- [x] **Runbook + LaunchAgent example** — `kanban/runbooks/fleet-conductor.md`  
- [x] **Model routing** — table in this file + AGY.md / CLAUDE.md pointers  
- [x] **Night tick** — `just night-loop` / `migx-night-loop.sh` (conductor+drain+theme-check; Grok still manual)  
- [x] **Session-mirror dogfood** — EXO `fixtures/dogfood/` (offline mirror + intent inbox)  
- [ ] **Night Grok scout** fully cron-wired (optional; long-harness runbook exists)  
- [ ] Optional: evidence-packet convention for research subagents  
- [ ] Live CO reconciler for intent-inbox (product Layer B — later dossier)  

## Related
- Roles: `kanban/federation/roles/*`  
- Strategy: `Strategy-Current.md`  
- AGY strengths signal: `signal/2026-07-17-antigravity-cli-strengths-federation.md`

---
id: migx-federation
type: doctrine
title: "Migx agent federation — Grok · Claude · Codex (Antigravity paused)"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
inspired_by:
  - /Users/gudjon/code/oz-platform/kanban/HARNESS-BIBLE/05-cross-agent-federation.md
  - /Users/gudjon/code/oz-platform/kanban/federation/FEDERATION.md
  - /Users/gudjon/code/oz-platform/kanban/knowledge/cross-repo-agent-federation-tandem.md
defers_to:
  - kanban/AGENTS.md
  - kanban/runbooks/multi-agent-parallel-sessions.md
  - .claude/rules/worktree-hygiene.md
---

# FEDERATION.md — Migx cross-agent coordination

## What this is

**Active** peer agents on this box cooperate on Migx **without a human ferrying chat**:

| Side id | Role | Default tool | Owns | Status |
|---|---|---|---|---|
| `grok-signal` | **Signal scout** | Grok CLI | X/web research, field scan, idea briefs, architecture/feature signal | **active** |
| `claude-code` | **Implementer** | Claude Code | C++/Qt, dossiers, benches, PRs; also non-RT/UI/ontology while AGY paused | **active** |
| `codex-cli` | **Verifier-cartographer** | Codex CLI | Repo orientation, code-path tracing, harness/tooling, verification, federation stewardship | **active** |
| `antigravity-cli` | Co-implementer (dormant) | Antigravity CLI (`agy`) | Was: goal-driven UI/ontology/non-RT | **paused** — no tokens (2026-07-17) |

Do **not** open new mail to `antigravity-cli` until `peers.yaml` marks it `active` again.

**Coordination is a commit, not a message.** Durable handoffs live as markdown under
`kanban/federation/`. Git is the substrate. There is no MCP broker, no NATS topic, no Slack relay.

This is a **same-repo, same-machine** federation (one box, shared `migx` history). It is deliberately
smaller than oz-platform's multi-repo `fed` maildir — same principles, Migx-sized surface.

## Lane discipline — poll + claim BEFORE you start (the anti-duplication rule)
The failure this prevents: two peers doing the **same work in parallel** (e.g. two scoring docs for one
module — which happened 2026-07-23, owner flagged "agents need better cooperation"). Before starting any
non-trivial lane:
1. **`just fed-sync` + poll your inbox** — see peer mail + active claims, and whether a peer already has a
   brief/claim for this lane. **If they do, build from it — do not write a parallel one.**
2. **Respect the operating split** (roles table above): `grok-signal` owns signal/research/**policy
   briefs**; `claude-code` owns the **implementation/build**; `codex-cli` owns **verification/judge**.
   Straying into a peer's lane duplicates work. *(2026-07-23: Claude wrote a scoring-policy note in Grok's
   lane; reconciled by narrowing it to defer to Grok's brief.)*
3. **`migx-fed claim` the paths** you'll mutate (TTL-bounded) so a peer who polls sees the lane is taken.
4. **One SSoT per topic** — a second doc on the same subject must `defers_to:` the first and cite, never
   duplicate (MG-3). Find a duplicate → reconcile immediately (narrow one to its unique lane).
5. **Ack, don't re-decide** — when a peer answers your open question via mail, `migx-fed ack` it and build
   on it; don't silently re-litigate what they resolved.

## Why federation (not just worktrees)

Worktrees stop agents from **clobbering files**. Federation stops them from **losing intent**:

- Grok finds a useful X thread on music world-models; Claude can pick it up without a human ferrying chat.
- Claude finishes a spike and needs a research question answered; Grok can receive the request from the durable inbox.
- Codex spots a verification gap or ownership collision; the right implementer sees an evidence-backed coordination note.

Federation gives each side a **pull inbox**. Delivery is **PULL**: a message is durable when committed;
the receiver acts when their session polls.

## Topology (this box)

```text
┌─────────────────────────────┐     git commits      ┌──────────────────────────────┐
│  Grok CLI                   │ ───────────────────► │  kanban/federation/          │
│  side: grok-signal          │                      │   signal/   (briefs)         │
│  worktree: ../migx-grok     │ ◄─────────────────── │   messages/{open,ack,closed} │
│  branch: grok/*             │     git pull/poll    │   peers.yaml                 │
└─────────────────────────────┘                      └──────────────▲───────────────┘
                                                                    │
┌─────────────────────────────┐     git commits                     │
│  Claude Code                │ ────────────────────────────────────┘
│  side: claude-code          │ ◄──── poll open → act → ack/close
│  checkout: ~/code/migx      │
│  branch: mtl/* or feature   │
└─────────────────────────────┘

┌─────────────────────────────┐     git commits / read-only sweeps
│  Codex CLI                  │ ───────────────────► federation/docs/tests
│  side: codex-cli            │ ◄──── poll open → verify/map/triage
│  worktree: ../migx-codex    │
│  branch: codex/*            │
└─────────────────────────────┘

┌─────────────────────────────┐     PAUSED (no tokens)
│  Antigravity CLI (agy)      │     side id retained for history only
│  side: antigravity-cli      │     do not address new open mail here
└─────────────────────────────┘
```

**Hard rule (still):** never two mutating agents in the same worktree on the same branch.
See `kanban/runbooks/multi-agent-parallel-sessions.md`.

**Soft rule for federation files:** prefer committing federation messages on a short-lived
`fed/*` branch or frequently rebasing/merging into the shared integration branch so all sides
see them. Do not leave open handoffs only in uncommitted worktree dirt.

## Channels

SSoT: [`channels.yaml`](channels.yaml). Three primary surfaces:

| Channel | Path | Writer | Consumer | Purpose |
|---|---|---|---|---|
| `signal` | `signal/*.md` | `grok-signal` | anyone (esp. Claude, Codex, Gudjon) | Field intel — X, papers, models, architecture ideas. **Not** a work order by itself. |
| `messages` | `messages/{open,ack,closed}/` | any peer | addressed peer | Durable handoffs with lifecycle. **State IS location.** |
| `claims` | `claims/{active,closed}/` | any peer | all peers | Temporary edit-lane ownership. **Not a lock**; a visible collision warning. |

Optional later: `broadcast` (to all peers). Not needed until addressed mail becomes too narrow.

## Message lifecycle (state = location)

```text
  migx-fed send  →  messages/open/<id>.md     status: open
  receiver ack   →  messages/ack/<id>.md      status: ack     (receiver moves + edits)
  work done      →  messages/closed/<id>.md   status: closed  (receiver moves + Resolution)
```

- **Sender never closes their own message** (oz §52). Receiver owns `ack` and `closed`.
- **Once closed**, treat as history. New work = new message (or a task/dossier).

## Lane claims (temporary ownership)

Claims answer "who is editing what right now?" They are for collision avoidance, not permission.

```text
  migx-fed claim   -> claims/active/<id>.md    status: active
  migx-fed release -> claims/closed/<id>.md    status: closed
```

Use a claim when a peer will mutate a dossier, harness tool, task set, or source area that another
peer could reasonably touch. Do not claim for pure read-only orientation. Keep claims narrow and
release them when done. Expired claims show as stale in `migx-fed sync`; they are a warning to verify
with git/status before editing.

`migx-fed claim` refuses to create a live overlapping claim unless you pass `--force`. Use `--force`
only when the overlap is intentional and coordinated; `migx-fed sync` will still report it under
**Claim Collisions**.

## Message ID

```text
<from>-<to>-YYYY-MM-DD-NNN-<slug>.md

grok-signal-claude-code-2026-07-17-001-music-wm-papers.md
claude-code-grok-signal-2026-07-17-002-need-metal-waveform-signal.md
```

`NNN` is a per-day sequence for that from→to pair (01, 02, …).

## Frontmatter (required)

```yaml
---
id: grok-signal-claude-code-2026-07-17-001-music-wm-papers
from: grok-signal          # peers.yaml id
to: claude-code
type: signal-handoff | research-request | status | blocker | question | coord
status: open               # open | ack | closed  — MUST match folder (derive; don't lie)
created: "2026-07-17"
created_utc: "2026-07-17T16:00:00Z"
severity: low | medium | high | blocker
subject: "music-wm-papers"
relates_to: []             # ADR-*, PS-*, dossier paths, prior msg ids, URLs
acceptance: "one line — what done looks like"
branch: ""                 # optional: branch the sender was on
commit: ""                 # optional: short SHA at send time
---
```

## Body contract (required sections)

Keep each section short (under one screen). A receiver must act in **one prompt-cycle**.

```markdown
## Intent
## Context
## Evidence
## Requested Action
## Blockers
```

On close, receiver appends:

```markdown
## Resolution
- what landed (paths, SHAs, task ids)
- what was deferred and where
```

Template: [`MSG-TEMPLATE.md`](MSG-TEMPLATE.md).

### `type` vocabulary

| type | When |
|---|---|
| `signal-handoff` | Grok promotes a signal brief into work Claude, Codex, or Gudjon should consider |
| `research-request` | Claude, Codex, or Gudjon asks Grok to scout a topic on X/web |
| `question` | Needs an answer; not yet a build |
| `coord` | Scheduling / ownership / branch intent |
| `blocker` | Something is stuck; needs the other side |
| `status` | Progress ping (prefer closing the original over status spam) |

## Signal briefs (Grok's primary product)

Path: `kanban/federation/signal/YYYY-MM-DD-<slug>.md`

These are **intelligence artifacts**, not tickets. Promote to a `signal-handoff` message only when:

1. It maps to a Migx thesis (Apple Silicon perf, AI-DJing, EXO/world-model, UI stack, audio engine), and
2. There is a concrete next step Claude, Codex, or Gudjon can take (spike, dossier, ADR amend, task card).

Signal template: [`signal/_TEMPLATE.md`](signal/_TEMPLATE.md).  
Scout mandate: [`roles/grok-signal.md`](roles/grok-signal.md).

## CLI — `migx-fed`

```bash
# from repo root (or any worktree of this repo)
./kanban/scripts/migx-fed doctor
./kanban/scripts/migx-fed audit [--open-hours N] [--ack-hours N] [--strict] [--json]
./kanban/scripts/migx-fed sync                         # shared peer/mail/worktree snapshot
./kanban/scripts/migx-fed claims [--status active|closed|all]
./kanban/scripts/migx-fed claim --by SIDE --subject short-lane --paths path [path ...] [--force]
./kanban/scripts/migx-fed release --id <claim-id> --by SIDE --resolution "done"
./kanban/scripts/migx-fed list [--to SIDE] [--status open|ack|closed|all]
./kanban/scripts/migx-fed poll --to SIDE          # print open messages for SIDE
./kanban/scripts/migx-fed listen --to SIDE        # periodically poll open messages
./kanban/scripts/migx-fed harness --to SIDE       # periodically sync + audit + poll
./kanban/scripts/migx-fed send \
  --from grok-signal --to claude-code \
  --type signal-handoff --subject music-wm-papers \
  --severity medium \
  --body path/to/body.md          # or --stdin
./kanban/scripts/migx-fed ack  --id <id> --by claude-code
./kanban/scripts/migx-fed close --id <id> --by claude-code --resolution path/or/text
```

Env (optional):

```bash
export MIGX_FED_SIDE=claude-code   # or grok-signal | codex-cli
export MIGX_REPO_ROOT=/Users/gudjon/code/migx
```

`fed --help` equivalent: `./kanban/scripts/migx-fed --help`.

`doctor` checks structure/schema. `audit` checks operational drift: expired active claims, live claim
collisions, old open/ack messages, and open/ack messages with missing timestamps. Use `--strict` when
you want a nonzero exit for stale-state gates.

## Session loop (each peer)

### Grok (`grok-signal`) — every scout session

```text
0. migx-fed sync                           # shared queue/worktree/dirty snapshot
1. migx-fed audit                          # stale handoffs/claims
2. migx-fed poll --to grok-signal          # research-requests from Claude
3. Scout X/web on mandate topics (role charter)
4. Write signal/YYYY-MM-DD-*.md for durable intel
5. If actionable → migx-fed send signal-handoff → claude-code
6. Commit federation paths; push/merge so Claude can pull
```

### Claude Code (`claude-code`) — every coding session start

```text
0. migx-fed sync                           # shared queue/worktree/dirty snapshot
1. migx-fed audit                          # stale handoffs/claims
2. migx-fed poll --to claude-code          # open handoffs
3. For each open: triage → ack OR close-as-wontfix with reason
4. Claim any mutating dossier/source lane before heavy coding
5. Do heavy coding on owned dossiers (MTL, engine, ...)
6. When stuck on "what's out there?": send research-request → grok-signal
7. On handoff done: release claim and close with Resolution (paths/SHAs/tasks)
```

### Codex CLI (`codex-cli`) — every verification / harness session

```text
1. migx-fed sync, then audit, then poll --to codex-cli, or run migx-fed harness --to codex-cli for long harness mode
2. Map repo state, active dossiers, dirty files, and ownership before proposing edits
3. Trace code paths and verify claims with grep, tests, benches, browser/tooling, or local scripts
4. Claim harness/docs/tooling lanes before mutating them
5. File coordination messages when a second writer risk or verification gap appears
6. Release any Codex claim, then close with evidence: paths, commands, test output, or a task/dossier pointer
```

Long harness runbook: [`kanban/runbooks/codex-long-harness-loop.md`](../runbooks/codex-long-harness-loop.md).

### Antigravity CLI (`antigravity-cli`) — paused

```text
No active session loop. No tokens on this box (2026-07-17).
Do not poll/listen/send new open mail for this side until peers.yaml sets status: active again.
Former AGY product/UI/ontology/non-RT work is owned by claude-code while paused.
```

Entry: repo-root [`AGY.md`](../../AGY.md) · role: [`roles/antigravity-cli.md`](roles/antigravity-cli.md).

## Closed loop (MG-1)

| Beat | Grok scout | Claude implementer | Codex verifier-cartographer |
|---|---|---|---|
| Trigger | Cadence / research-request / owner ask | Open `signal-handoff` / dossier wave / AGY-paused product lane | Review/orientation/verification ask |
| Capture | `signal/*.md` + optional message | Code + tests + dossier JOURNAL / EVD | Repo map, command output, lint/test/bench evidence |
| Intelligence | Relevance filter vs Migx thesis | Architecture fit + house physics + product fit | Gap analysis, ownership risk, evidence quality |
| Adjustment | Handoff message or "no promote" note | Merge / task / ADR / reject with reason | Message/task/ADR patch, verifier gate, role correction |

## What federation is NOT

- Not real-time control (not audio, not 60 Hz UI).
- Not a substitute for dossiers — handoffs **seed** work; dossiers **own** multi-day execution.
- Not a third UI stack decision channel — strategy still lands in ADRs.
- Not cross-machine mesh (yet). Same-box first. Extend later if a second host joins.

## Bootstrap (first time on this box)

```bash
cd ~/code/migx
./kanban/scripts/migx-fed doctor          # must be clean

# Claude main
export MIGX_FED_SIDE=claude-code

# Codex verifier worktree
git worktree add ../migx-codex -b codex/verify-steward
cd ../migx-codex
export MIGX_FED_SIDE=codex-cli

# Grok worktree
git worktree add ../migx-grok -b grok/signal-scout
cd ../migx-grok
export MIGX_FED_SIDE=grok-signal
# grok … then scout + send
```

Roles: [`roles/`](roles/). Peers: [`peers.yaml`](peers.yaml).

## Provenance

Distilled from oz-platform federation practice: git-mediated mailbox, structured body, receiver-owned
status, pull delivery, archive-on-act discipline. **Not** a verbatim vendor of oz's multi-repo `fed`
CLI — Migx starts with one repo and a small same-box peer set.

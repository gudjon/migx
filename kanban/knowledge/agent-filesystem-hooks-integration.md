---
id: agent-filesystem-hooks-integration
type: knowledge
title: "Agent integration — filesystem state + CLI + hooks (Claude Code / Vercel shape)"
status: draft
owner: gudjon
authored_by: grok-signal
created: "2026-08-08"
lastUpdated: "2026-08-08"
defers_to:
  - kanban/architecture/decisions/ADR-008-cli-core-two-equal-clients.md
  - kanban/knowledge/session-coaching-multimodal-agent.md
  - repo-root AGENTS.md
related:
  - kanban/federation/signal/2026-08-08-agent-fs-hooks-x.md
  - tools/migx-cli/migx_cli/session.py
  - tools/migx-cli/migx_cli/engine.py
  - install.sh
  - kanban/planning/00-PORTFOLIO/capability-gap-matrix.md
  - kanban/tasks/replace-set-play-render-with-live-transport.md
note: >
  SSoT for how coding agents (Claude Code, Codex, Cursor, Grok) integrate with a
  live Migx session: level-triggered state files, edge-triggered hooks, CLI as
  the only mutator. Mirrors Claude Code hooks + Vercel "filesystem + bash"
  thesis. MCP remains wont-do.
---

# Agent integration — filesystem, CLI, hooks

## One sentence

An agent integrates with Migx the same way it integrates with a codebase: **read
files for truth**, **run `migx … --json` to act**, **subscribe to hooks to react**
— never MCP, never the RT audio thread.

## Field consensus (why this shape)

Industry signal (Claude Code hooks lifecycle, Vercel “filesystems and bash”,
Codex/Claude harness engineering) converges on three claims:

1. **CLI + filesystem beats custom tool protocols.** Agents already know `cat`,
   `grep`, pipes, exit codes. Structured stdout is enough discovery. MCP is a
   second protocol that drifts from the real surface (Migx: `wont-do`, ADR-008).
2. **The harness is outside the model.** Stateless model turns; durable state on
   disk; dumb loop that feeds state back. Anthropic’s managed-agent writeups and
   reverse-engineered Claude Code diagrams both put *state store + tools* outside
   the weights.
3. **Hooks are edge-triggered guardrails / notifiers, not the SSoT.** Lifecycle
   events fire external commands with JSON on stdin; timeouts matter; hooks must
   not block the critical path. Claude Code’s `async` / timeout fields exist for
   the same reason Migx must never stall a deck.

Migx is already ahead on (1): `--json` on commands, `system.capabilities`,
sidecars as SSoT, session coaching CLI. Gaps are (2) single-session lock +
authoritative live state dir, and (3) config-declared hooks.

## Three surfaces (each has one job)

| Surface | Trigger shape | Job | Agent does |
| --- | --- | --- | --- |
| **State files** | Level (always true *now*) | “What is playing / queued / planned?” | `cat` / `jq` / `migx session.now --json` |
| **CLI commands** | Request/response | Mutate library, plan set, record feedback | `migx … --json` |
| **Hooks** | Edge (just happened) | React without polling | external `command` + JSON stdin |

**Why both files and hooks:** an agent that starts mid-set, or reconnects after a
crash, has missed every event. Hooks cannot recover history. Files can. Hooks
exist so a *running* coach does not busy-poll `now.json` every 200 ms.

### 1. State directory (level-triggered)

Canonical home (installer already creates the parent):

```text
~/Library/Application Support/Migx/
  session.lock          # one live session per OS user (pid + start time + host)
  session/
    now.json            # currently playing / bound: path, isrc, deck, position_s, bpm, camelot
    queue.json          # ordered upcoming paths (or crate / plan slice)
    plan.json           # transition into each upcoming track (from set.plan maths)
    history.jsonl       # append-only what actually played this night
  hooks.log             # hook timeouts / non-zero exits (visible failures)
```

**Relationship to today’s library-root files**

| Today | Role | Target |
| --- | --- | --- |
| `<library>/_live.json` | coaching bind (CLI/TUI) | keep as *prep* bind; promote to `session/now.json` when engine owns play |
| `<library>/_session.jsonl` | night log in library tree | mirror or move to `session/history.jsonl` in state dir (state dir survives library path changes) |
| track sidecars | lifetime judgments | stay beside audio forever |

Writers: **off-RT only** — engine bridge worker, CLI, TUI. Same atomic replace as
`sidecar.write` / `session.write` (temp + rename). Readers never see half JSON.

**Engine absent is normal.** `now.json` may be missing or mark
`"source": "cli-bind"` while the DJ preps. Fabricating playposition without an
engine is a lie (`P-34`); prefer unbound + honest `session.now` exit 1.

### 2. Commands (act)

Already the product spine (ADR-008). Agent loop for a live set:

```bash
migx session.now --json
# → path, title, deck, room, position_s if known

migx set.plan --json | jq '.tracks[0:5]'
# → next tracks + technique / pitch / harmonic into each

# optional when queue/plan files exist:
jq . ~/Library/Application\ Support/Migx/session/queue.json
jq . ~/Library/Application\ Support/Migx/session/plan.json

migx track.feedback now --fit weak --note "lost the floor"
migx session.room --theme melodic --energy mid
migx session.show --json   # night reconstruct
```

Exit codes stay gates: `0` ok, `1` empty/unbound/findings, `2` usage error.
`system.capabilities --json` remains the discovery surface — no registry.

### 3. Hooks (edge-triggered)

Modelled on Claude Code: config-declared matchers, external command, **JSON on
stdin**, timeout, logged failure. Not on the audio callback.

#### Event vocabulary (closed set)

| Event | When | Payload (min) |
| --- | --- | --- |
| `SessionStart` | lock acquired / first bind | user, library.root, pid |
| `SessionEnd` | clear / lock release | duration, play count |
| `TrackLoaded` | deck load receipt | path, isrc, deck, source |
| `TrackPlaying` | playposition starts advancing / bind while playing | path, deck, position_s, bpm, camelot |
| `TrackUnloaded` | deck empty | deck, path (last) |
| `TransitionStarted` | crossfade / mix-out armed or detected | from, to, technique?, pitch_pct? |
| `TransitionEnded` | incoming is master | from, to |
| `QueueChanged` | re-plan / feedback moved next | queue hash or full queue.json ref |
| `FeedbackRecorded` | `track.feedback` succeeded | path, fit, placement, … |
| `HookFailed` | (internal log only) | event, command, status |

#### Config sketch (user settings, not project git by default)

```json
{
  "hooks": {
    "TrackPlaying": [
      {
        "command": "~/dj/hooks/on-track.sh",
        "timeout_ms": 2000
      }
    ],
    "TransitionStarted": [
      {
        "command": "~/dj/hooks/on-blend.sh",
        "timeout_ms": 2000,
        "async": true
      }
    ],
    "SessionEnd": [
      {
        "command": "~/dj/hooks/wrap-up.sh",
        "timeout_ms": 5000
      }
    ]
  }
}
```

Handler contract (Claude Code-compatible *shape*):

```bash
#!/bin/bash
# stdin: one JSON object
# stdout: optional JSON decision (v0: ignore; fire-and-forget notify only)
# exit 0 = ok; non-zero = logged to hooks.log; never blocks deck
jq -r '.path, .title, .deck' >> ~/dj/session-sidechannel.log
```

#### Non-negotiables (house physics)

1. **Never on the RT audio thread.** Hook dispatch is fork/exec or a worker queue
   filled from a lock-free handoff (`P-02`, `P-16`). The callback only updates
   atomics / ring; a worker serializes JSON and spawns hooks.
2. **Timeout + visible failure.** Default ~2 s for track events; hang → kill
   process group, append `hooks.log`, fire no silent drop. A hook that stops
   firing must not look like a quiet set (`P-34`).
3. **Hooks do not write ControlObjects.** They may run `migx` commands (off-RT)
   or write their own side files. Perform intents stay armed / preconditioned.
4. **No hook as authority for “what is playing”.** `now.json` / `session.now` are
   the level-triggered SSoT; hooks are notifications.

## Single session per OS user

Installer model (already): per-user `~/.local/bin` symlink, state under
`~/Library/Application Support/Migx`, no sudo.

**Lockfile discipline** (build next — guards races already seen with
`library.watch`):

```text
session.lock =
  { "pid": 12345, "started_at": "…Z", "host": "…", "cmdline": "migx-tui|engine" }
```

- Acquire: atomic create / exclusive open.
- **Stale = detectable:** if pid is not alive (or start-time does not match
  process), delete and retake. “File exists ⇒ running” is a lie we do not ship.
- Contenders exit 2 with a clear message: who holds the lock and how to force
  after confirming the process is dead.

One session at a time matches booth reality and keeps `now.json` unambiguous.

## How Claude Code (or any agent) runs a coaching session

```text
[DJ plays / TUI binds]
        │
        ▼
  now.json + history.jsonl   ◄── level: agent always recoverable
        │
        ├── hooks: TrackPlaying ──► optional side scripts / notify agent
        │
        ▼
  agent: migx session.now --json
  agent: migx set.plan --json | jq  (or read plan.json / queue.json)
  DJ speech → agent maps → migx track.feedback now --fit …
        │
        ▼
  sidecars + candidate_bias → next set.plan / Arrange differs
  (live re-plan later rewrites queue.json / plan.json)
```

No second chat product. The coding agent *is* the session coach UI; Migx is the
filesystem + CLI substrate (Vercel thesis applied to the booth).

## Build order (dependency-respecting)

| # | Deliverable | Acceptance | Depends on |
| --- | --- | --- | --- |
| **1** | Session lock | second `migx-tui` / live writer refuses; stale lock recoverable | installer `STATE_DIR` |
| **2** | `session/now.json` + `history.jsonl` | agent can `cat` truth mid-set; atomic writes; engine-absent honest | engine bridge status receipts *or* CLI bind promotion |
| **3** | Hooks v0 | config → command + JSON stdin + timeout; `TrackPlaying` / `SessionEnd` | **2** (hooks over untrusted state amplify lies) |
| **4** | `queue.json` / `plan.json` live re-plan | feedback mid-night changes next 3 candidates on disk | set.plan + lock + now |
| **5** | Config layering | user → project/gig → local overrides for hooks paths | useful after hooks |
| **6** | Armed perform hooks | free-deck load only; never silent Automix | engine bridge load |

**Do not start 3 before 2.** A `TrackPlaying` hook is only as true as the writer
behind `now.json`.

## Map: Claude Code / Codex / Vercel → Migx

| Pattern | Field | Migx |
| --- | --- | --- |
| Structured stdout | CLI agents | `--json` everywhere |
| Discovery without protocol | capabilities | `system.capabilities` |
| Exit codes as gates | shell agents | 0/1/2 |
| Filesystem as context | Vercel bash-tool | Collection + sidecars + state dir |
| Skills as markdown | Claude / Codex | `.claude/skills/migx-session-coach` |
| Hooks JSON stdin | Claude Code hooks | **to build** (events above) |
| Session lifecycle | SessionStart/End | lock + `session.clear` |
| Async non-blocking hooks | Claude `async` / timeout | worker queue + `timeout_ms` |
| Remote control | Claude Dispatch | later; lock + state first |
| MCP marketplace | plugins | **wont-do** as product path |
| Install per user | CC / Codex | `./install.sh` → `~/.local/bin` |

## Anti-patterns

| Pattern | Why not |
| --- | --- |
| MCP as the agent adapter | second protocol; ADR-008 CLI spine |
| Hook on audio callback | RT violation (`P-02`) |
| Silent hook failure | looks like quiet set (`P-34`) |
| Hook-only “now playing” | mid-session agents have no truth |
| Multi-writer sidecars without lock | races already hit on watch |
| Agent unsolicited deck load | Automix anti-identity |
| Copy install (not symlink) | which binary mid-set? |

## What an agent can answer (target)

| Question | Level read | Edge (hook) | Command |
| --- | --- | --- | --- |
| What song is now? | `now.json` | `TrackPlaying` | `session.now --json` |
| What’s next? | `queue.json` | `QueueChanged` | `set.plan --json` |
| What’s the blend into the next? | `plan.json` | `TransitionStarted` | same / `mixing` via plan rows |
| What did I say about this track? | track sidecar | `FeedbackRecorded` | `track.show` |
| What happened tonight? | `history.jsonl` | `SessionEnd` | `session.show --json` |

## Promotion / harvest

- Implementation waves land as CLI + optional small C++ off-RT writer only.
- Durable API shapes: pin in this file + CAPABILITIES; do not leave only in chat.
- Related coaching dogfood: `session-coaching-multimodal-agent.md` (waves 0–5
  largely shipped; live engine position + hooks remain).

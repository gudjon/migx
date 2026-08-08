---
name: migx-session-coach
description: >
  Use when the DJ is coaching a live or prep Migx session in natural language or
  voice: feedback on the current song (worked/outdated/retire), cutoffs, segment
  length, transitions, room/crowd theme, next-energy, EQ/volume reminders.
  Fire on phrasings like "this feels outdated", "don't play again", "shorter next
  time", "crowd is more melodic", "last blend was weak", "session.now", or when
  writing feedback via migx CLI. Prefer direct CLI, never MCP.
disable-model-invocation: false
user-invocable: true
defers_to:
  - kanban/knowledge/session-coaching-multimodal-agent.md
  - kanban/federation/signal/2026-08-08-multimodal-session-coaching-x.md
  - tools/migx-cli/migx_cli/feedback.py
  - tools/migx-cli/migx_cli/session.py
  - kanban/architecture/decisions/ADR-008-cli-core-two-equal-clients.md
audit_gate: "python3 tools/migx-cli/test_migx_cli.py (session + feedback cases)"
verifiable_output_shape: >
  Shell commands run: session.now/bind/room/show and track.feedback/note/cue with
  structured flags; no free-form writes except --note text.
---

# migx-session-coach

You are the **session coach** adapter: the DJ talks (voice→text or chat); you
**interpret** into structured `migx` CLI. Migx persists and applies. You do **not**
ride faders, load decks unsolicited, or invent Automix.

SSoT: [`session-coaching-multimodal-agent.md`](../../../kanban/knowledge/session-coaching-multimodal-agent.md).

## Always CLI-direct (no MCP)

```bash
./tools/migx-cli/migx <command> … --json   # when you need machine parse
./tools/migx-cli/migx <command> …          # human-readable ok for confirmation
```

## Loop every coaching turn

1. **`session.now --json`** — who is "now"?  
   - If unbound: ask which track, or run **`session.bind "<fragment>"`** (or bind after TUI `t`).  
2. Map speech → **one or more** structured commands below.  
3. Confirm with a short receipt (command stdout).  
4. Never claim you changed EQ/volume in the engine unless a future perform command exists and is armed.

## Speech → command map

| DJ says (examples) | Command |
| --- | --- |
| worked / landed / keep | `track.feedback now --fit worked` |
| weak / didn't land | `track.feedback now --fit weak` |
| outdated / never again / bin it | `track.feedback now --fit retire` |
| good opener / open with this | `track.feedback now --placement opener` |
| peak-time only / not for opening | `track.feedback now --placement peak` |
| shorter next time | `track.feedback now --segment shorter` |
| longer stretch next time | `track.feedback now --segment longer` |
| blend into this was 2/5 or "bad transition" | `track.feedback now --transition 2` |
| free-text judgment | `track.feedback now --note "…"` (combine with flags) |
| cutoff / mix-out at 1:30 | `track.cue now 1:30 "mix out — keep"` *(use path if cue lacks now)* |
| tag / vibe note | `track.note now --tag outdated --note "…"` if note path supports now; else bind path |
| crowd melodic / peak / cool-down | `session.room --theme melodic --energy mid` |
| next tracks higher energy | `session.room --energy high --note "next few: more energy"` |
| what happened tonight / recap | `session.show` or `session.show --json` |
| clear end of set | `session.clear` *(log kept for show)* |

If `track.cue` / `track.note` do not accept `now`, resolve path from `session.now --json` → `.path`.

## Combine flags in one call

```bash
./tools/migx-cli/migx track.feedback now \
  --fit weak --segment shorter --transition 2 \
  --note "felt tired; cut earlier next time"
```

## Hard rules

- **Structured flags only** near the library (`feedback.py` law). You own NL→flags.  
- **No RT / no ControlObject** from this skill.  
- **No silent deck load.** Prep suggestions only unless user explicitly asks and a load command is armed.  
- Prefer **`now`** after bind so speech stays bound to the playing file id.  
- Floor flags **change the next set**: `retire` removes; `weak`/`worked` and
  `--transition` nudge Arrange / `set.plan` rank; `opener`/`peak` move the open.
  After recording, you may re-run `set.plan` / glance Arrange to confirm.

## Bind helpers

```bash
./tools/migx-cli/migx session.bind "Reckoning" --deck A
./tools/migx-cli/migx session.now --json
./tools/migx-cli/migx session.show --json   # night plays + feedback arc
# TUI: press t on a Library row also binds (source=tui)
```

---
id: session-state-home-removable-volume
type: task
title: "Session state lives on a removable volume — decide its home before hooks"
status: open
owner: gudjon
priority: high
initiative: initiative-ai-djing-product
authored_by: claude-code
authored_kind: agent
triggered_by: "Wave 2 of the agent integration surface found the state already
  built by a peer, but under <library>/ on the USB SSD, while the session lock
  went to the OS state dir — two homes for one session's truth"
created: "2026-08-08"
lastUpdated: "2026-08-08"
---

# Session state home — decide before hooks land

## What exists (verified 2026-08-08)
Wave 2 is **largely already built**, by a peer, and correctly: `session.py` writes
`<library>/_live.json` (current binding + room) and `<library>/_session.jsonl` (append-only night
log), with an atomic replace. `migx session.now --json` is reachable and answers
`migx.live-status/1` today. **Do not build `session/now.json` alongside it** — that is the parallel
implementation `P-11` names, and this session has spent all day deleting those.

## The problem
The two halves of one session's truth now live in different places:

| What | Where | Survives SSD eject? |
| --- | --- | --- |
| session lock | `~/Library/Application Support/Migx/` | yes |
| `_live.json` / `_session.jsonl` | `<library>/` = `/Volumes/Code/Music` | **no** |

`/Volumes/Code/Music` is a **removable USB SSD**. Unplug it mid-set, or start an agent before it
mounts, and "what is playing?" becomes unanswerable — not wrong, *unreachable*. An agent that cannot
read the level signal is exactly the reconnect case the whole file-based design exists to serve.

## The decision to make
1. **Move live state to the OS state dir**, keep the night log with the library. The "now" pointer is
   about the *session*; the log is about the *library* and belongs beside the music it describes.
2. **Keep both under the library**, and accept that no state is readable without the volume.
3. **Write both to the state dir**, and treat the library copy as an export.

Leaning (1): it splits on the real seam — ephemeral session truth versus durable library history —
and it is the only option where `session.now` still answers with the SSD unplugged.

## Why this blocks hooks (wave 3)
A `TrackPlaying` hook is only as true as the state behind it. If that state can vanish with a volume,
hooks fire into a void and the agent keeps coaching from its last known value — a confident lie, and
the same `P-34` shape as everything else fixed today. Settle the home first.

## Also worth checking
`session.now` currently answers `{"path": null}` when nothing is bound. Confirm it answers
*distinguishably* when the library is **unreachable** — "nothing playing" and "I cannot tell" must not
look alike.

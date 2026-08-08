---
id: replace-set-play-render-with-live-transport
type: task
title: "Replace set.play's file render with a live, dynamic transport"
status: open
owner: gudjon
priority: high
initiative: initiative-ai-djing-product
authored_by: claude-code
authored_kind: agent
triggered_by: "Gudjon, on seeing the 23-minute rendered mix: 'there is not a use
  case to just render long mp3 files from mixes, as we're a dynamic DJ software.
  Automix is great, but when it just plays, like how the new Spotify DJ feature
  just plays.'"
created: "2026-08-08"
lastUpdated: "2026-08-08"
---

# Replace `set.play`'s file render with a live transport

## The correction
`set.play` currently renders a planned set to a single `.mp3` via ffmpeg. It works — it produced a
23-minute beatmatched mix from the live library — and it is **the wrong shape for this product.**

Nobody wants a long mixed file. The value of Automix is that it **plays**, continuously and live, the
way Spotify's DJ feature does: the software is mixing *now*, and the DJ can intervene at any moment.
A rendered file is the opposite — the decisions are frozen before you hear them, and there is nothing
to intervene in. It is also the anti-identity named in
`kanban/knowledge/session-coaching-multimodal-agent.md`: hands on the mix, mouth on the coach.

**Do not build on the render path.** It stays only as an offline audition of the transition maths.

## What survives (and it is the valuable half)
The musical decisions in `setplay.py` are exactly what a live transport needs, and they are already
shared with `set.plan` and the Deck view (`P-11`):

- the **tempo chain** — running tempo is each track's *played* BPM, so a beatmatched run holds steady
- the **±8% reachability rule** — what a real pitch fader can do
- **cut instead of force** — a track that cannot reach the tempo is not silently warped 30%
- entry points from the DJ's own mix-in cues

## What replaces it
A live transport that plays the *next* track while the current one is still playing, applying the same
numbers in real time, and stays steerable mid-set:

- continuous playback with the transition applied at the planned point, not baked ahead
- the running order re-planned **as it plays**, so `track.feedback` and `session.room` change what
  comes next *during* the set, not only in the next one
- the DJ can override the next pick, skip, extend, or take the blend manually at any moment

## Constraints
- **Never on the RT audio thread.** Whatever drives playback is worker/UI-class; `P-02` is absolute.
  The engine already owns real decks — prefer driving those over inventing a second audio path.
- One writer per ControlObject (`P-06`) if this reaches the engine.
- The transition maths has ONE home. A live transport must call the same functions, not re-derive them.

## Route: DECIDED — drive the engine (Gudjon, 2026-08-08)

Route 1. The CLI does **not** grow a second audio path; it drives the real decks. This kills the
parallel-implementation risk outright and means "what the CLI plays" and "what the DJ hears" are the
same thing by construction.

### What exists today (verified at HEAD, 2026-08-08)
**Nothing.** There is no external control surface to build on:

| Searched | Result |
| --- | --- |
| `QLocalServer` / `QTcpServer` | absent from `src/` |
| websocket / JSON-RPC | absent |
| `osc` | only false positives inside unrelated identifiers |

The closest precedent is `src/controllers/` — the MIDI/HID controller path, which already translates
external events into `ControlObject` writes. That is the shape to copy, not to bypass.

### Design constraints (house physics — non-negotiable)
- **Never on the RT thread.** The bridge is main/worker-thread-class. The engine emits but never
  receives Qt signals; the sanctioned write path is `ControlProxy`, exactly as controllers use.
- **`P-06` one writer per ControlObject.** The bridge must not fight the GUI or a mapped controller
  for the same key. Decide the ownership rule *before* writing the first `set()`.
- **`P-11`** the transition maths already has one home (`mixing` / `setplan`). The bridge issues
  intents; it does not re-derive tempo or pitch.

### Shape
A local socket (`QLocalServer`, no network surface) accepting line-delimited JSON intents, mapped onto
`ControlProxy` writes — `[ChannelN]` load/play/rate/crossfader. Reads come back as receipts so the CLI
and TUI see real deck state rather than guessing.

    migx → socket → bridge (main thread) → ControlProxy → engine decks

### First wave (smallest thing that proves the route)
Load a track onto deck 1 and start it, from the CLI, with the engine running — then read back
`[Channel1],play` as a receipt. Everything else (tempo, blends, the live re-plan) is worthless until
that round-trip works.

### Still open
Whether the bridge lives in the app process (simplest) or a headless engine host. Answer it when the
first wave has a round-trip, not before.

## Related
- `kanban/knowledge/session-coaching-multimodal-agent.md` — anti-Automix-as-identity
- matrix row `engine command bridge` (gap)
- `tools/migx-cli/migx_cli/setplay.py` — carries the direction note

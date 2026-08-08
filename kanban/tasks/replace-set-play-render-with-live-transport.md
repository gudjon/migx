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

## Open question for the owner
Two routes, and this is a product call, not a technical one:

1. **Drive the Migx engine** (real decks, real crossfader, the actual DJ application) — faithful, and
   the engine already exists; needs the command bridge on the matrix (`engine command bridge`).
2. **A CLI-side live player** — faster to reach, but risks becoming a second audio path, which is the
   parallel-implementation trap.

Route 1 is the honest one if the engine bridge is coming anyway.

## Related
- `kanban/knowledge/session-coaching-multimodal-agent.md` — anti-Automix-as-identity
- matrix row `engine command bridge` (gap)
- `tools/migx-cli/migx_cli/setplay.py` — carries the direction note

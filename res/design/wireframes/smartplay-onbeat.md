# Wireframe draft — SmartPlay: one-touch beat-aligned play (the "stupid-simple mixing" magic)

Status: **DRAFT — owner-directed, in review for the specifics** (2026-07-23). Enriches `cap-deck-transport`
(the PLAY behaviour) + `cap-tempo-sync`. Owner directive: *default ON.*

## The idea (owner, 2026-07-23)
> When I press **PLAY**, if another song is already playing, the deck should automatically **"swing" into
> the right beat** — beatmatched + phase-aligned to what's playing — **immediately**. On-beat by default,
> zero setup. Press play → it plays *right now* from the correct beat point. **Immediate reward.**

This is the single feature that makes mixing **stupid-simple**: the hardest, most intimidating DJ skill —
beatmatching — is removed from the critical path and folded into the one button everyone already presses.

## Behaviour
```
press PLAY on a stopped deck
        │
        ├─ no other deck playing ──▶ plays normally (from cue/start)
        │
        └─ another deck playing ───▶ SmartPlay:
                 1. quantize ON              (snap to the beat grid)
                 2. match tempo to the leader (beatsync_tempo / sync_enabled)
                 3. play + align phase        (beatsync_phase → downbeats line up)
              ⇒ starts on-beat, in time, instantly — "swings in"
```
Default **ON**. It is *just PLAY* — no new button, no mode, no thinking. A small, quiet indicator on the
strip (`◇ on-beat`) shows it engaged; an opt-out lives in settings for purists who want a hard manual cut.

## Value-creation case
- **The accessibility magic** — a first-timer sounds beatmatched on their first press. This is the "anyone
  can DJ" promise, and it's the emotional **immediate reward** the owner named (press → it just works).
- Directly serves the thesis: the human↔music link, **lowest cognitive load**, no modal setup, instant feedback.
- Tiny to build — a behaviour on the already-shipped `DeckTransport` (togglePlay), all engine COs exist.

## Cognitive-load case
- **Zero new surface** — it's the existing PLAY button; the DJ learns nothing.
- **Immediate, legible reward** — playback starts on-beat and in time; the DJ *hears* it work at once.
- Fail-safe: if there's no other deck, or tempos are incompatible, it degrades to a normal play (never a
  dialog, never a silent wrong-tempo lurch).

## Industry-trend grounding
rekordbox / Serato / Traktor all ship **SYNC + quantize** — but as **separate toggles the user must arm**
first. djay Pro leans "beginner-friendly / automatic" and is praised for it (digitaldjtips: "visual
simplicity"). Our divergence: **default-ON and folded into PLAY** — no arming, no setup. We make the
*simple* path the *default* path, and keep an opt-out for purists (who are the minority we still respect).

## Engine sketch (feasible — COs verified)
In `DeckTransportModel.togglePlay()` on a start, if any other deck's `play > 0`:
`quantize = 1` → `beatsync` (or `sync_enabled = 1`) → `play = 1` → `beatsync_phase`. All are existing
`[ChannelN]` controls (`sync_enabled`, `beatsync`, `beatsync_tempo`, `beatsync_phase`, `quantize`). One
writer per CO (P-06); GUI/worker only, never on the audio thread. Engine note: phase only aligns while
playing + quantize on — so set quantize first, then play, then phase.

## Open questions (owner directed default-ON; these are the *specifics*)
1. **Opt-out home** — a global "SmartPlay: on" in settings + a per-deck override? (Recommend: global
   default-on toggle in settings; no permanent PERFORM chrome.)
2. **Beat vs phrase align** — snap to the nearest **beat** (tight, instant) or the nearest **phrase/downbeat**
   (musically cleaner but may wait up to a bar)? (Recommend: beat for "immediate"; phrase as a later option.)
3. **Tempo guard** — if tempos are far apart (e.g. 128 vs 174), sync to **half/double-time** when it lands
   in range, else **don't tempo-warp** (avoid a chipmunk lurch) — just phase-align. (Recommend: half/double aware.)
4. **Leader when ≥2 decks play** — sync to the current sync-leader / loudest / most-recent? (Recommend: the sync-leader.)

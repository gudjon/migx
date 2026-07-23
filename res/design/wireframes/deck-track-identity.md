# Wireframe draft — deck-track-identity (deck bounded context)

Status: **DRAFT — in review** (per-module design gate, `nextgen-ui-architecture`). No code until approved.

## Proposed module
The per-deck **track-identity anchor**: album art · title · artist · **BPM · KEY**. Sits above the
DeckClock + DeckTransport we already built. The always-present "what is loaded, and is it mixable?"
readout — the head of every deck in every major DJ app.

## ASCII wireframe — PERFORM, Deck 1 (target)
```
┌─ PERFORM ───────────────────────────────────────────── ⌘1 ─┐
│                                                             │
│   ┌────────┐   Jin (Original Mix)                           │  ← title  (loud)
│   │        │   Arche                                        │  ← artist (quiet)
│   │  art   │                                                │
│   │  56²  │   ┌──────────┐  ┌──────────┐                   │
│   └────────┘   │ 128.0 BPM│  │ Gm · 8A  │                   │  ← reusable BPM/KEY badges
│                └──────────┘  └──────────┘                   │     (green when mixable vs other deck*)
│                                                             │
│                        −01:16                               │  ← DeckClock  (built)
│                      04:15 / 05:31                          │
│                                                             │
│                      [    PLAY    ]                         │  ← DeckTransport (built)
│                        ▶ playing                            │
└─────────────────────────────────────────────────────────────┘
   empty state →  [ ▢ ]  — no track —      -- BPM   -- KEY
```
\*mixability tint is a *later* enhancement (needs the other deck's key); v1 badges are neutral.

## Value-creation case (why this is the right next module)
- Answers the deck's #1 question — **"what am I playing, and can I mix it?"** — at a glance, with zero
  interaction. Nothing else on a deck is looked at more often than title + BPM + KEY.
- **Unblocks ARRANGE.** Title/artist/BPM/KEY is the exact vocabulary the browser + co-pilot use. Build the
  **BPM/KEY badge once** and reuse it on the deck, the ARRANGE track-list rows, and the co-pilot chips —
  one component, three surfaces.
- Higher always-on value than the alternatives: **cue** is a single action folded into transport;
  **hotcues** need per-track structure data (bigger, later); **waveform** is the true #1 but Metal-pinned.
  Track-identity is the cheapest universal win that also compounds into ARRANGE.

## Cognitive-load case (must LOWER load)
- **One clear hierarchy**: title loud → artist quiet → BPM/KEY as compact badges. Three glance-targets, no
  reading required.
- **No new mode, no new interaction** — pure read-only display; nothing to learn.
- **Minimal chrome**: badges are small and fixed; no labels beyond the values. Art is a small anchor, not
  a hero image (56², per "admin chrome is minimal").
- **Fail-quiet**: no track → greyed placeholder, never a dialog (non-modal law).

## Industry-trend grounding
Rekordbox 7 (`res/design/references/rekordbox7-performance`) places exactly this row at the head of each
deck: art · title · artist · **BPM · KEY** · time. Serato, Traktor, VirtualDJ and djay all do the same —
it is the single most consistent element across DJ software. **BPM + KEY as the always-visible "lingua
franca"** is the trend we adopt; we diverge by scoring mixability with the co-pilot rather than leaving the
DJ to compute it, and by keeping the row uncluttered (no SYNC/MASTER/key-shift chrome on the PERFORM face).

## Engine bindings (proposed, verified feasible)
| Field | Source | Notes |
|---|---|---|
| title / artist / art | `Mixxx.PlayerManager.getPlayer(group).currentTrack?.{title,artist,coverArtUrl}` | read-only track object (precedent: `res/qml/Deck.qml`) |
| BPM | `[ChannelN],bpm` ControlProxy | numeric → format `128.0` |
| KEY | `[ChannelN],key` ControlProxy | numeric 1–24 → musical (`Gm`) + Camelot (`8A`) map in the ViewModel |

Split (invariant #2): dumb `DeckIdentity.qml` view (props: title/artist/artUrl/bpmText/keyText/hasTrack)
+ read-only `DeckIdentityModel.qml` ViewModel + a reusable `NgKeyBpmBadge` (deck + ARRANGE). Fixture-runnable.

## Open questions for review (owner value judgments)
1. **KEY notation** — show musical (`Gm`), Camelot (`8A`), or both (`Gm · 8A`)? Draft shows both;
   co-pilot uses Camelot, rekordbox shows musical.
2. **Album art in v1?** — needs the cover-art URL pipeline; cheap to defer to a placeholder if you'd
   rather ship title+BPM+KEY first.
3. **Make BPM/KEY a reusable component now** (used again in ARRANGE), or inline for the deck first?
   Recommend: build it reusable now — it's the compounding win.

# Wireframe draft — deck-track-identity (deck bounded context)

Status: **APPROVED → BUILT** 2026-07-23 (per-module design gate, `nextgen-ui-architecture`). Shipped as
`components/DeckIdentity{,Model}.qml` + `primitives/NgBadge.qml` + 12 DESIGN.md key-wheel tokens
(commit 9a3890b). Owner approved all 3 open questions (both notations + wheel colour · art in v1 · reusable badge).
Capability: `cap-track-identity` (+ `cap-harmonic-key` for the KEY badge) in the capability catalogue.

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
│   └────────┘   │ 128.0 BPM│  │▎Gm · 8A  │                   │  ← reusable BPM/KEY badges
│                └──────────┘  └──────────┘                   │     KEY chip COLOUR-CODED by wheel*
│                                                             │
│                        −01:16                               │  ← DeckClock  (built)
│                      04:15 / 05:31                          │
│                                                             │
│                      [    PLAY    ]                         │  ← DeckTransport (built)
│                        ▶ playing                            │
└─────────────────────────────────────────────────────────────┘
   empty state →  [ ▢ ]  — no track —      -- BPM   -- KEY
   compact + tileable: this header stacks for 2/4/N decks (Traktor multi-deck)
```
\*Colour-coded key (Traktor learning): the KEY chip carries its Camelot/Open-Key **wheel colour**, so
harmonically-compatible tracks are scannable by colour. A *second* mixability signal (compatible vs the
**other** deck) is a later enhancement — v1 ships the wheel colour only; needs new DESIGN.md key-wheel tokens.

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

## Industry-trend grounding (4 references — `res/design/references/`)
The track-identity anchor is the **single most consistent element across DJ software** — art · title ·
artist · **BPM · KEY** · time appears on every deck in all four references:
- **Rekordbox 7** — art · title · artist · BPM · **KEY (musical, `Gm`)** · time, at the deck head.
- **Traktor Pro 4** — compact one-line header (title · −remaining · BPM), **KEY colour-coded** (Open-Key)
  in the browser → the concrete upgrade we adopt: **colour the KEY chip by its wheel position**. Four-deck
  grid → our header must be **compact + tileable**.
- **Serato DJ Pro** — same anchor, **BPM-first**, clean flat aesthetic (no skeuomorph chrome); djworx
  critiques its **big platters/BPM as wasted laptop real-estate** → we drop the platter, keep the row tight.
- **djay Pro 5 / landscape** (digitaldjtips) — "visual simplicity + Apple aesthetics" is the UX trend;
  and the roundup found **no competitor doing smart track suggestion** → our co-pilot is the whitespace.

**We adopt:** BPM + KEY as the always-visible lingua franca, KEY **colour-coded** (Traktor), compact +
tileable (Traktor), un-skeuomorphic/clean (Serato+djworx). **We diverge:** the co-pilot **scores
mixability** (tempo + Camelot) rather than leaving the DJ to compute it, and PERFORM carries **no
SYNC/MASTER/key-shift chrome** on the identity face (that's mode-scoped elsewhere).

## Engine bindings (proposed, verified feasible)
| Field | Source | Notes |
|---|---|---|
| title / artist / art | `Mixxx.PlayerManager.getPlayer(group).currentTrack?.{title,artist,coverArtUrl}` | read-only track object (precedent: `res/qml/Deck.qml`) |
| BPM | `[ChannelN],bpm` ControlProxy | numeric → format `128.0` |
| KEY | `[ChannelN],key` ControlProxy | numeric 1–24 → musical (`Gm`) + Camelot (`8A`) map in the ViewModel |

Split (invariant #2): dumb `DeckIdentity.qml` view (props: title/artist/artUrl/bpmText/keyText/hasTrack)
+ read-only `DeckIdentityModel.qml` ViewModel + a reusable `NgKeyBpmBadge` (deck + ARRANGE). Fixture-runnable.

## Open questions for review (owner value judgments)
1. **KEY notation + colour** — show musical (`Gm`), Camelot (`8A`), or both (`Gm · 8A`)? Draft shows both.
   Recommend **both + the Traktor-style wheel colour** on the chip (adds 12/24 key-colour tokens to
   DESIGN.md). co-pilot uses Camelot; rekordbox shows musical; Traktor colours it.
2. **Album art in v1?** — needs the cover-art URL pipeline; cheap to defer to a placeholder if you'd
   rather ship title+BPM+KEY first.
3. **Make BPM/KEY a reusable component now** (used again in ARRANGE), or inline for the deck first?
   Recommend: build it reusable now — it's the compounding win.

# Wireframe draft — PERFORM multi-deck layout (deck-strip tiling)

Status: **BUILT** 2026-07-23 (`components/DeckStrip.qml` + `performDecks` Repeater in main.qml; both demo
decks render). Realizes the deck-shell layout for
`cap-mode-shell` + composes `cap-track-identity`/`cap-deck-clock`/`cap-deck-transport`. Encodes the
owner's stated vision: **dual-deck default · vertical-stack flexibility to N · 4–6 playable at once.**

## Proposed module
Turn PERFORM from a single centred deck into a **vertical stack of deck strips**. Each deck is one
horizontal strip (identity · clock · transport); strips stack top-to-bottom; the set is a list
(`performDecks`) so 2 → 4 → 6 is a data change, not a rewrite. A new `DeckStrip` composite parameterized
by `group`.

## ASCII wireframe — PERFORM (dual-deck default)
```
┌─ PERFORM ──────────────────────────────────────────────── ⌘1 ─┐
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ [art] 128 BPM Am          [128.0 BPM] [▎Am·8A]      −01:16  │ │  DECK 1
│ │       Demo Deck A                      04:15/05:31 [ PLAY ] │ │
│ └────────────────────────────────────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ [art] 125 BPM Gm          [125.0 BPM] [▎Gm·6A]      −02:00  │ │  DECK 2
│ │       Demo Deck B                      00:30/03:20 [ PLAY ] │ │
│ └────────────────────────────────────────────────────────────┘ │
│           (flexible: performDecks = [C1,C2,(C3,C4…)] up to 6)   │
└──────────────────────────────────────────────────────────────────┘
```
Each strip: **identity left (fills width)** · **clock** · **transport right** — a consistent per-deck
row so the eye lands in the same place on every deck.

## Value-creation case
- PERFORM finally looks like a **real DJ setup** — two decks side-by-side (stacked) is the core mixing
  unit; everything the DJ does live is "this deck vs that deck."
- Reuses three already-approved components verbatim — highest value for lowest new risk.
- The list-driven design delivers the owner's **N-deck flexibility** (4–6) for free.

## Cognitive-load case
- **One row shape per deck**, repeated — learn it once, read any deck. Vertical stack = natural scan
  order (top = deck 1).
- No new interaction; strips are composed from known parts. Empty decks show the fail-quiet placeholder.
- Stays minimal: no per-deck chrome beyond the strip; add-deck is on-demand, not permanent.

## Industry-trend grounding
Traktor Pro 4 tiles **four decks** in a 2×2 with compact headers (`res/design/references/traktor-pro4`);
Serato offers a stacked/vertical deck view. The **compact, tileable deck header** is exactly what makes
multi-deck legible — our strip is that header. We diverge by stacking uniform full-width strips (cleaner
scan) rather than a dense grid, and by scaling as a data list (owner's unlimited-vertical vision).

## Build
`DeckStrip.qml` (composite: group → 3 models + 3 views in a RowLayout) → PERFORM renders a `Repeater`
over `root.performDecks` (default `["[Channel1]","[Channel2]"]`). Token-only; each strip fixture-runnable
via its children. Verified live against the dev test base (both demo decks visible at once).

## Open questions (surface, non-blocking)
1. **Default deck count** — 2 (recommend) or 4? The list makes it trivial to change.
2. **Add/remove deck UX + shortcut** — later module (`⌘⇧D`?), not in this first tiling.
3. **Deck strip order** — fixed [C1,C2] now; drag-reorder is a later enhancement.

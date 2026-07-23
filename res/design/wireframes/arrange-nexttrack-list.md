# Wireframe draft — ARRANGE: the next-track candidate list (the core differentiator)

Status: **DRAFT — in review** (per-module design gate). Realizes `cap-copilot-suggestion` (core) +
`cap-harmonic-key` + `cap-community-signal`, composed on the LIBRARY/`cap-library-crates` data. This is
**the product thesis made visible**: not a browser, but the co-pilot answering *"what do I play next?"*
under cognitive load. No code until approved.

## The job (the one friction that matters)
A DJ mid-set, one track playing, ~90 seconds to choose the next one in a loud room. Every rival shows a
*grid* the DJ must scan and reason over. ARRANGE inverts it: **rank the crate by mixability with what's
playing, lead with the co-pilot's pick, and show the *reason*** — so the choice is a glance, not a scan.

## ASCII wireframe — ARRANGE
```
┌─ ARRANGE ──────────────────────────────────────────────────── ⌘2 ─┐
│ NOW ▸ DECK 1 · 128.0 BPM · Am ▎8A            crate: [ House ▾ ]     │  context that drives the ranking
│                                                                    │
│ ┌─ ★ NEXT ─ co-pilot pick ───────────────────────────────────────┐ │
│ │ [art]  Rise Up                 128.0 ▎Am·8A    ✓ perfect match  │ │  HERO: top pick + why
│ │        Nicole                  ±0.0 BPM        ▲ 2.4M · 38 sets │ │
│ └────────────────────────────────────────────────────────────────┘ │
│ ── ranked candidates ──────────────────────────────────────────    │
│ [art] Oscillation      125.0 ▎Cm·5A   ✓ +1 key · −2%   ▲ 1.2M · 21 │  each row: identity + mixability + signal
│ [art] All Nighter      123.0 ▎Fm·4A   ~ energy lift    ▲ 900k · 14  │
│ [art] Ghetto Funk      129.0 ▎Fm·4A   ⚠ +1 BPM         ▲ 400k · 9   │
│ [art] Badge            125.0 ▎Em·9A   ✗ key clash      ▲ 220k · 3   │  clash → greyed, sorts last
│ ...                                                                 │
└──────────────────────────────────────────────────────────────────────┘
```
Row anatomy (reuses the deck's badges): art · title/artist · **BPM badge** · **colour-key badge** ·
**mixability tag** (the differentiator) · **community-signal chip** (later). The mixability tag is scored
vs the NOW deck: `✓ perfect` (same/adjacent Camelot + ≤±3% tempo) · `✓ +1 key` · `~ energy` · `⚠ tempo` ·
`✗ clash`. Ranked best-first; clashes de-emphasized.

## Value-creation case
- Hits the **one friction the whole product is about** — choosing the next track fast. Nothing else we
  build matters more to the DJ's night.
- **Whitespace**: the landscape roundup found *no* competitor doing smart suggestion (digitaldjtips).
  rekordbox ships "Related Tracks" but by static similarity, **not ranked by mixability with the live
  deck + a stated reason**. This is where Migx wins.
- Reuses the EXO co-pilot we already have (`tools/exo/copilot_why_next.py`: `tempo_compat` + Camelot).

## Cognitive-load case
- **The pick is the hero** — the DJ can trust the top card without reading the list at all (lowest
  possible load: one glance).
- **Reasons, not raw data** — `✓ perfect match` beats making the DJ compute `Am vs Cm`. The colour-key
  badge lets the eye pre-filter by hue before reading.
- **One row shape**, sorted by what matters (mixability), so scanning is ranked, not random.
- Non-modal, keyboard-first (↑/↓ to move the pick, Enter to load to the free deck).

## Industry-trend grounding (`res/design/references/`)
- **rekordbox 7** — Collection/Streaming Radar + Mood/Association prove the *demand* for "what next," but
  present it as suggestion lists without live-deck mixability scoring. We adopt the intent, beat the execution.
- **Traktor Pro 4** — colour-coded key in browser rows; we reuse that (our `NgBadge` key colour) and add
  the mixability verdict rekordbox/Traktor leave to the DJ's head.
- **Serato / djworx** — "smarter use of screen real-estate, prioritise vital info" → the pick + reason is
  exactly that: the vital decision, not a 15-column grid.

## First buildable slice (proposed — smallest strategic module)
`TrackRow.qml` (dumb view: art · title · artist · BPM/KEY badges · mixability tag · signal chip) +
`TrackRowModel`/list ViewModel + a shared `camelot.js` helper (extract the ChromaticKey→Camelot map from
`DeckIdentityModel` so both surfaces share one SSoT). v1 scores mixability **in QML** vs Deck 1's live
`bpm`/`key` COs; the ranked hero + community-signal chips layer on next.

## Open questions for review (owner value judgments)
1. **v1 data source** — rank the **whole library**, a **selected crate**, or start against the **dev
   fixtures + a small seed crate**? (Recommend: a selected crate, with the dev fixtures as the seed to
   test scoring live.)
2. **Scoring home** — compute mixability **in QML/JS** now (fast, self-contained) vs read a precomputed
   **EXO sidecar** (richer, but needs the pipeline)? (Recommend: QML v1, EXO enrichment later.)
3. **Community signal in v1** — show the `▲ listens · sets` chips now (needs Grok's data source) or ship
   mixability-only first and add signal as a fast-follow? (Recommend: mixability first, signal next.)
4. **Load action** — Enter/double-click loads the pick to the **first stopped deck** — correct default?

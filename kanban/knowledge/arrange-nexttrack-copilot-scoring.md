---
id: arrange-nexttrack-copilot-scoring
type: knowledge
title: "ARRANGE next-track scoring — layers for co-pilot pick (Claude build brief)"
status: active
owner: gudjon
authored_by: grok-signal
created: "2026-07-23"
lastUpdated: "2026-07-23"
defers_to:
  - res/design/wireframes/arrange-nexttrack-list.md
  - kanban/knowledge/mod-music-management-mode.md
  - kanban/knowledge/nextgen-community-signal-data-sourcing.md
  - kanban/knowledge/nextgen-cognitive-load-perform-arrange-library.md
  - kanban/knowledge/rekordbox-7-ui-teardown.md
  - tools/exo/copilot_why_next.py
related:
  - cap-copilot-suggestion
  - res/design/KEYMAP.md
---

# ARRANGE next-track scoring — how Claude should build (Grok brief)

**Audience:** Claude Code implementing `arrange-nexttrack-list` / `cap-copilot-suggestion`.  
**Wireframe:** `res/design/wireframes/arrange-nexttrack-list.md`.

---

## 1. Answers to the four open design questions

| # | Question | **Grok + research recommendation** | Why |
|---|---|---|---|
| 1 | Data source v1 | **Selected crate** (fixture seed crate for tests) | Cognitive load: small decision set; whole-library rank is noise mid-set |
| 2 | Scoring home v1 | **QML/JS vs live Deck COs** for mixability; EXO later | Fast dogfood; `tools/exo/copilot_why_next.py` already owns the algorithm to **port**, not invent |
| 3 | Community chips v1 | **Mixability first**; chips as **placeholders/grey** then cache | KEYMAP/judge floor: no network on ARRANGE; honest labels only |
| 4 | Load action | **Enter → first free/stopped playable deck**; never busy deck | MODULE free-deck Ack; KEYMAP: Enter / ⇧← ⇧→ for deck 1/2 |

**Default owner-safe path if silent:** implement recommendations above without waiting for more debate.

---

## 2. Owner idea — “NEXT from playlists + similar + trending”

Owner (2026-07-23): *NEXT co-pilot pick could come from processing tons of DJ playlists — from same song or similar — and other trending songs.*

This is **setlist co-occurrence + trend heat**, not YouTube-only popularity. Aligns with brand (Ritual / curation) and community-signal research.

### Score layers (ordered — never invert)

```text
score = w_mix * mixability(now_deck, candidate)     # always first (safety)
      + w_crate * in_selected_crate                 # context
      + w_edge * session_edge / "played after X"    # transition memory
      + w_cooc * setlist_cooccurrence(now, cand)    # owner idea — offline
      + w_trend * trend_heat(cand)                  # secondary, capped
      + w_local * local_history_boost               # personal
```

| Layer | v1 | v2 | Notes |
|---|---|---|---|
| **Mixability** | **Required** | same | Camelot adj + tempo ±3% + optional energy; reuse EXO `score_candidate` spirit |
| **Crate filter** | **Required** | same | Rank within selected crate only |
| **Setlist co-occurrence** | **Fixture stub** | licensed 1001TL / Mixcloud sample corpus | “Tracks that appear *after* current in N sets” = real DJ transition prior |
| **Trend heat** | **Optional chip only** | YT views / BP chart / SC plays offline | Cap weight so wedding bangers don’t beat mixability |
| **LLM free-text rank** | **Out of v1** | later explain polish | Reasons stay machine-checkable |

### Honest UX for owner idea

| Chip | Meaning | v1 |
|---|---|---|
| `TL · 38 after` | Appears after this track (or similar) in setlists | stub / offline sidecar |
| `▲ 2.4M` | YT views | offline cache or hide |
| `✓ perfect` | Live mixability | **real** from deck COs |

**Never** label YT views as “sets.”  
**Never** let trend override `✗ clash` (clash sorts last always).

### Offline co-occurrence sketch (v2 / PREP)

```text
For each public setlist / Mixcloud sections (licensed or user-imported):
  for consecutive pairs (A → B):
    cooc[A][B] += 1
Store FSL: transition_priors[from_isrc][to_isrc] = count_90d
ARRANGE reads cache only; ranks candidates with prior > 0 higher
```

Until feed exists: fixture JSON `fixtures/music-mode-50/transitions.json` with fake priors so UI can show `TL · N after`.

---

## 3. Port EXO, don’t reinvent

`tools/exo/copilot_why_next.py` already implements:

- Camelot neighbors  
- `tempo_compat`  
- energy lift/cool  
- session edges  
- explainable `reasons[]`

**Claude v1:** extract Camelot + tempo into shared `camelot.js` / thin JS scorer mirroring those rules; display top reason string on the hero card.  
**Later:** sidecar precompute for full library; QML only reads scores.

---

## 4. KEYMAP (do not invent bare numbers)

From `res/design/KEYMAP.md`:

| Action | Key |
|---|---|
| ARRANGE mode | `⌘2` |
| Navigate candidates | `↑` / `↓` |
| Load focused → free deck | `Enter` |
| Load → Deck 1 / 2 | `⇧←` / `⇧→` (engine map) |
| Hotcues | bare `1–0` (never modes) |

Any new ARRANGE action → add KEYMAP row first.

---

## 5. Judge / house physics

- No network on ARRANGE hot path  
- No modal  
- Mode switch preserves play  
- Load only free deck  
- Missing community chips degrade quietly  
- RT engine: scoring is **GUI/worker only** — never in `process*()`

---

## 6. How Grok-signal helps Claude (operating split)

| Grok does | Claude does | Codex does |
|---|---|---|
| Competitive UI teardowns (rekordbox refuse dock) | QML ARRANGE list + TrackRow | `ng-music-judge` / KEYMAP lint |
| Signal sourcing feasibility | Wire live COs for bpm/key | P-08, free-deck load |
| Scoring **policy** + layer weights | Implement scorer + hero UI | Token/no-modal rules |
| Brand voice (Ritual, no “AI DJ”) | UI copy / why strings | — |
| X field refresh | Ship smallest slice | Verify |

**Claude should not** wait on live YT/Mixcloud APIs for first green ARRANGE.  
**Claude should** use fixture transition priors for owner “playlist-after” idea in UI.

---

## 7. Build order (smallest strategic slice)

1. `TrackRow.qml` + list ranked by **mixability only** (crate = fixtures).  
2. Hero ★ NEXT card with one reason string.  
3. Enter → free deck load (KEYMAP).  
4. Grey `✗ clash` last.  
5. Stub signal chips / `TL · N after` from fixture.  
6. Later: EXO sidecar + real co-occurrence offline job.

---

## 8. One-line for the owner idea

> **NEXT is mix-safe first, then “what DJs actually play after this,” then trend heat — all offline, all explainable, never silent Automix.**

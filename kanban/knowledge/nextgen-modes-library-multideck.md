---
id: nextgen-modes-library-multideck
type: knowledge
title: "NextGen — booth modes, music-management surface, multi-deck flexibility, community signals"
status: proposal
owner: gudjon
authored_by: grok-signal
created: "2026-07-21"
lastUpdated: "2026-07-23"
defers_to:
  - kanban/knowledge/nextgen-agent-dj-shadow-product.md
  - kanban/knowledge/nextgen-dj-needs-and-leader-ui-map.md
  - kanban/knowledge/nextgen-music-management-mode.md
  - kanban/knowledge/nextgen-bakeoff-deck-strip-copilot.md
  - kanban/knowledge/nextgen-cognitive-load-perform-arrange-library.md
  - kanban/Strategy-Current.md
  - kanban/knowledge/world-model-experience-ontology.md
related:
  - initiative-ai-djing-product
  - initiative-ui-modernization
  - nextgen-music-management-mode
  - dj-shared-library-capability
  - nextgen-cognitive-load-perform-arrange-library
sources:
  - "X 2026: Serato crate search as workflow win; library UX = prep speed; Ora DJ prep canvas"
  - "Serato 4.0 library overhaul (crate search, colour, emoji ratings) — DDJT 2026"
  - "Lexicon DJ — external library mgmt, find mixable tracks"
  - "Owner thesis: arrangement/management is the hard problem; full-screen modes; multi-deck vertical; community signals"
  - "Discovery: AI silent setlist rejected; prep assist OK"
  - "Research deepen 2026-07-23: CLT + Endsley SA + dual-task → modes (see cognitive-load knowledge)"
---

# NextGen — modes, library, multi-deck, community graph

**Owner problem statement (2026-07-21):** The hard part of DJing is not “two faders exist.” It is **music arrangement and management** — under booth noise and cognitive load, **finding the next song to queue** fast enough that the room does not drop. NextGen should treat that as a **first-class full-screen mode**, not a skinny list under dual decks.

Performance decks stay necessary. The **differentiator surface** is the **music brain** of the set.

---

## 1. Cognitive model: busy club DJ

**Research SSoT (CLT / Endsley SA / dual-task / DJ HCI):**  
`nextgen-cognitive-load-perform-arrange-library.md` — why PERFORM capacity depends on LIBRARY schemas + ARRANGE projection.

| Load | What the brain is doing | UI implication | Science anchor |
|---|---|---|---|
| **Now** | Keep two (or N) channels musical | Perform mode: decks + mixer only, minimal chrome | Intrinsic load (CLT); dual-task continuous control |
| **Next 16–32 bars** | What loads when this phrase ends? | One-gesture **queue / stage** without leaving room awareness | SA Level-3 projection → ARRANGE |
| **Tonight’s arc** | Energy, genre, crowd read | Arrange mode: set flow + candidates | Goal-directed mental models |
| **Library memory** | “Where did I put that remix?” | Visual recognition + tags + playlist membership | External memory; recognition > recall |
| **Trust** | Will this track land? | Community / chart / set-appearance signals (not silent AI play) | Secondary chips only; honest sources |

**Product rule:** Never force the DJ to solve “next track” on a 12-row text table while also riding EQ (split-attention). Give them a **mode switch** as fast as controller bank buttons (keyboard, pad, touch edge).

---

## 2. Mode architecture (few clear screens)

Small set of **primary modes**. Instant toggle; audio never stops; state preserved.

```text
┌─────────────────────────────────────────────────────────────┐
│  MODE BAR (always 1-line; hotkey / pad / edge swipe)        │
│  [ PERFORM ]  [ ARRANGE ]  [ LIBRARY ]  · optional PREP     │
└─────────────────────────────────────────────────────────────┘
```

| Mode | Job | Layout | Cognitive budget |
|---|---|---|---|
| **PERFORM** | Ride the mix | Dual (or N) decks + mixer + mini now/next strip | Lowest — no dense lists |
| **ARRANGE** | Queue the next 1–5 tracks; see arc | Full-screen **staging canvas** + free-deck targets; thin “now playing” header | Medium |
| **LIBRARY** | Find / tag / browse identity | Full-screen **graphical crate** (covers, chips, signals) | High prep; mid-set only for rescue |
| **PREP** (optional daytime) | Tag, import, community enrich offline | Same library chrome + bulk tools | Offline / home |

### Mode switch rules

1. **One keystroke / one pad** between PERFORM ↔ ARRANGE (the critical path mid-set).  
2. LIBRARY is one more hop (or long-press ARRANGE).  
3. Switching modes **never** steals focus with modals (house non-modal rule).  
4. **Now playing** always visible as a **status ribbon** (title, bars left, free deck count) so ARRANGE/LIBRARY never feel “blind.”  
5. Co-pilot suggestions **live in ARRANGE** (and a collapsed rail on PERFORM), not as a chat that covers waveforms.

### Why full-screen ARRANGE (not just a panel)

Industry defaults bury library under decks (Serato/RB performance). Field feedback: **crate search / library UX is prep speed** — mid-set that becomes **panic speed**. A full-screen arrange mode is the Cursor-path idea applied to the *set*: Agent UI for “what next,” performance chrome for “what’s playing.”

```text
PERFORM (club literacy)          ARRANGE (set brain)
┌──────────┬──────────┐         ┌────────────────────────────┐
│ Deck A   │ Deck B   │         │ NOW: Track · 24 bars left  │
│ wave…    │ wave…    │         ├────────────────────────────┤
├──── XF ──┤          │         │ STAGED queue (1…5 cards)   │
│ mixer    │          │         │  → free deck / wait XF     │
└──────────┴──────────┘         ├────────────────────────────┤
                                │ CANDIDATES (visual grid)   │
                                │ why · tags · community     │
                                └────────────────────────────┘
```

---

## 3. Multi-deck flexibility (beyond fixed dual)

### 3.1 Thesis

Hardware trained everyone on **two decks + XF**. Software no longer has that constraint. NextGen should support:

| Layer | Count | Meaning |
|---|---|---|
| **Staging slots** | Soft-unlimited (UI virtual list) | Tracks staged for the set, not all audible |
| **Playable decks** | Cap **4–6** (engine + RT policy) | Concurrent audio paths, meters, CO groups |
| **Visible deck strips** | 2 default; scroll/stack for more | Vertical stack layout (Serato Stack DNA) |

**Vertical decks:** natural for laptop height and for “more than two” without shrinking waveforms to postage stamps. Unlimited **scrollable** deck columns/rows in UI; **playable** set gated by `max_playable_decks` (config + RT budget, not marketing).

### 3.2 Engine / house-physics note

- Each playable deck = CO group + RT cost. Cap is a **benchmark contract** (p99 buffer + underruns), not a guess.  
- Staging a track is **not** a playable deck (metadata + optional silent pre-decode offline) — keeps RT clean.  
- Load staged → free playable deck with Ack (same co-pilot rule).

### 3.3 UI patterns

| Pattern | Use |
|---|---|
| **Dual default** | Club literacy; 90% of gigs |
| **Stack / vertical strip list** | 3–6 decks; scroll; pin top two as “main” |
| **Deck pool** | Free / busy badges; ARRANGE loads into free pool slot |
| **Deck roles** | Main A/B, FX return, sample, loop deck — tags not separate products |

---

## 4. LIBRARY / ARRANGE surface — graphical UX for recognition

**Problem with classic tables:** 40 tracks of same genre look identical under stress. Recognition needs **visual + structural + social** identity.

### 4.1 Track card (atomic unit)

```text
┌──────────────────────────────────────────────────────┐
│ [art]  Title                              BPM  Key   │
│        Artist · Remixer                   energy ··· │
│  chips: #peak  #vocal  crate:PeakTime  crate:Closers │
│  signals: YT 12M · BP #4 Melodic · MC 48 sets · SC…  │
│  [ Stage ]  [ Load free ]  [ Why match ]             │
└──────────────────────────────────────────────────────┘
```

| Element | Purpose |
|---|---|
| **Artwork / waveform thumb** | Instant recognition |
| **Title / artist / remixer** | Primary text |
| **BPM / key / energy** | Mixability at a glance |
| **Playlist / crate chips** | “Where this track lives” in *your* system |
| **Tag chips** | Personal taxonomy (colour language like Serato) |
| **Community signals** | Social proof / heat (see §5) |
| **Stage / Load free** | Explicit — no silent hijack |

### 4.2 Layouts inside LIBRARY

| View | When |
|---|---|
| **Grid (cover-first)** | Fast visual scan |
| **Dense list + waveform strip** | Prep power users |
| **Graph / clusters** (later) | Energy/key neighbourhoods (EXO) |
| **Tonight’s path** | Ordered stage list = set spine |

### 4.3 Industry alignment (what leaders finally fixed)

| Signal | Implication for NextGen |
|---|---|
| Serato 4.0: crate search, colour, emoji ratings | Search + visual tags are **table stakes**, not polish |
| “Crate search changes prep speed” (X) | Search quality is product |
| Lexicon-class external tools | DJs leave apps to **organize** — bake management into NextGen modes |
| Ora / prep-canvas apps | Set planning is a **canvas**, not only a playlist list |
| OneLibrary / portable prep | FSL/EXO identity should survive tool hops long-term |

### 4.4 Mid-set LIBRARY rules

- Huge type, high contrast, dark booth tokens.  
- **No nested preference panels.**  
- Filter chips: energy band, key compatible with free deck, “in crate Peak,” “played tonight.”  
- Result set capped / virtualized (agent + human readable density).

---

## 5. Community signals (external heat graph)

**Goal:** Help the DJ answer “will this land?” without leaving the booth app for five browser tabs.

### 5.1 Signal classes (priority order)

| Signal | Source class | Booth use | Freshness |
|---|---|---|---|
| **Playlist membership (local)** | User crates / EXO | Highest trust | Local |
| **Key / energy / phrase match** | Analyzer + EXO | Mix safety | Local |
| **Beatport / chart position** | Charts by genre | Genre heat | Cached hours–days |
| **Setlist appearances** | Mixcloud / SoundCloud set scrapes or APIs | “How often DJs actually play it” | Cached |
| **YouTube views / engagement** | YT Data API / published stats | Mainstream recognition | Cached |
| **SoundCloud plays / reposts** | SC API | Underground / promo heat | Cached |
| **Internal play counts** | Migx history | Personal memory | Local |

### 5.2 UX of signals (critical)

- Show as **compact glyphs + numbers**, not walls of stats.  
- Always **sourced and dated** on long-press (“Beatport Melodic #4 · 2d ago”).  
- **Never auto-rank only on YouTube views** (wedding bangers vs club tools). Ranking = local compatibility first, community as **secondary chip**.  
- Offline booth: last cache is fine; grey out stale.  
- Respect licenses / ToS — prefer official APIs + user-owned exports over brittle scrapes.

### 5.3 “Appears in N DJ sets” (high value)

Aggregate concept: **setlist co-occurrence** — count of public mixes/sets containing this ISRC/title+artist within window (90d / 1y).

| Why DJs care | Product |
|---|---|
| Peer validation without following charts blindly | Chip: `MC 48 sets · 90d` |
| Find tools other DJs actually drop | Sort: setlist heat among key-compatible |
| Avoid overplayed festival IDs | Optional filter: heat band mid, not top 0.1% |

Implementation is a **sidecar / FSL enrichment job** (prep), not RT. UI only reads.

### 5.4 Data-sourcing reality (2026-07-21 research)

**SSoT:** `kanban/knowledge/nextgen-community-signal-data-sourcing.md` (closes federation research-request).

| Wanted chip | Feasible v1? | Source truth |
|---|---|---|
| YouTube views | **Yes** (cached `videoId` + `videos.list`) | Official YT Data API — batch offline |
| Beatport heat | **Yes** as **chart/rank**, not sets | Beatport catalog/charts API |
| SoundCloud heat | **Yes** as **playback_count**, not sets | SC track API |
| “N DJ sets” (MC/SC/BP) | **Not as stated** | No reverse setlist index; Mixcloud sections only if crawled |
| True setlist count | **v2** | 1001Tracklists-class feed (partner/license preferred) |

---

## 6. Co-pilot placement under this model

| Mode | Co-pilot role |
|---|---|
| PERFORM | Collapsed “next 1” chip; Ack expands to ARRANGE or loads free deck |
| ARRANGE | Full candidate grid with **why** + community chips |
| LIBRARY | Search assist / “more like this” — still Ack to stage |

Rules unchanged: **explain + Ack**, no silent master load, P-06 single writer, no AI setlist that replaces the DJ (discovery culture reject).

---

## 7. Module roadmap impact (extends prior maps)

| Order | Module | Closes |
|---|---|---|
| 0 | Shell + Theme + mode bar | Mode switch infrastructure |
| 1 | Deck strip + waveform (PERFORM) | Literacy |
| 2 | Thin load path | N2 |
| 3 | **ARRANGE mode** + stage queue | Next-track cognition |
| 4 | **LIBRARY mode** + track cards | Recognition + tags + crates |
| 5 | Multi-deck stack + playable cap | N>2 |
| 6 | Community signal sidecars (offline enrich) | Heat chips |
| 7 | Co-pilot ranking over EXO + signals | Agent DJ wedge |
| 8 | Full dual/N mixer parity | N6 complete |

Bake-off can stay **PERFORM strip + mini stage**; full ARRANGE/LIBRARY is the **product wedge** after dogfood.

---

## 8. Open decisions (owner)

1. **Default mid-set hotkey:** PERFORM ↔ ARRANGE only, or three-way? (Recommend two-way primary.)  
2. **Playable deck cap:** 4 vs 6 for M4 underrun contract.  
3. **Community signals v1:** Beatport + local only vs + Mixcloud setlist counts.  
4. **Cover art first vs waveform first** in grid (A/B dogfood).  
5. **Vertical stack default** for laptop vs dual horizontal default for controller.

---

## 9. Relationship to existing NextGen docs

| Doc | Role |
|---|---|
| `nextgen-dj-needs-and-leader-ui-map.md` | N0–N6 irreducible loop |
| `nextgen-bakeoff-deck-strip-copilot.md` | First dogfood unit |
| **This file** | **Modes + library-first product thesis + multi-deck + community graph** |
| `nextgen-agent-dj-shadow-product.md` | Cursor path / methods |
| EXO / FSL | Compatibility + sidecars for signals |

**Bottom line:** NextGen wins if the busy-club DJ can **full-screen into arrangement**, stage the next tracks with **visual identity + crate tags + community heat**, then snap back to a **flexible multi-deck PERFORM** surface — without AI taking the mix, and without a spreadsheet library under stress.

---
id: nextgen-bakeoff-deck-strip-copilot
type: knowledge
title: "NextGen bake-off unit — deck strip + co-pilot panel (industry trends)"
status: active
owner: gudjon
authored_by: grok-signal
created: "2026-07-19"
lastUpdated: "2026-07-23"
defers_to:
  - kanban/knowledge/nextgen-dj-needs-and-leader-ui-map.md
  - kanban/knowledge/nextgen-music-management-mode.md
  - kanban/knowledge/nextgen-ui-industry-trends-agent-design.md
  - kanban/knowledge/nextgen-agent-dj-shadow-product.md
  - kanban/knowledge/rekordbox-7-ui-teardown.md
  - kanban/Strategy-Current.md
  - kanban/knowledge/world-model-experience-ontology.md
related:
  - initiative-ai-djing-product
  - initiative-ui-modernization
  - design-md-ui-modernization
  - rekordbox-7-ui-teardown
sources:
  - "Serato display modes (vertical/horizontal/extended/stack)"
  - "Serato waveform: overview + main, frequency colour, hot-cue flags"
  - "rekordbox: vocal position on overview, cue culture, performance mode"
  - "rekordbox-7-ui-teardown: steal overview+zoom+cues; refuse library dock under decks"
  - "djay Neural Mix / stem pads on deck; VirtualDJ AI prompt + lyrics-on-waveform"
  - "Strategy: co-pilot in the mix flow, not bolted chat; EXO explain+Ack"
  - "Discovery: AI setlist ads rejected; prep assist OK; silent live load not OK"
---

# Bake-off unit: deck strip + co-pilot panel

**Owner refinement, 2026-07-21:** this bake-off is incomplete if it treats the library as a thin
fixture list forever. The primary DJ pain may be the full-screen **music management / arrangement**
mode: find and recognize the next song quickly, stage it, and load it with low cognitive load. The
deck strip remains the performance literacy object; music mode becomes the next-track decision object.

**Why this unit:** It is the smallest surface that proves **both** “we are a real DJ app” (deck strip) **and** “we are Agent DJ” (co-pilot). Industry already trains muscle memory on the first; the second is our differentiator — if it does not fight the first.

```text
┌──────────────────────────────── deck strip (literacy) ────────────────────────────────┐
│  [ overview waveform · cues · vocal marks ]                                           │
│  [ zoom waveform · playhead · beatgrid ]                                              │
│  [ ▶ ⏸ CUE  tempo  sync? ]   [ gain · HI/MID/LOW ]   [ hot-cue pads 1–8 ]            │
└───────────────────────────────────────┬───────────────────────────────────────────────┘
                                        │ CO bus (read/write rules)
┌───────────────────────────────────────▼───────────────────────────────────────────────┐
│  co-pilot panel (differentiator)                                                      │
│  next candidates · why · energy/key match · Ack/load · never silent mid-set write     │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Deck strip — industry trends (what leaders train)

### 1.1 Anatomy (converged across Serato / rekordbox / Traktor / djay / VDJ)

Almost every performance UI composes the same **vertical stack per deck**:

| Zone | Industry practice | User love / habit | Bake-off must |
|---|---|---|---|
| **Track header** | Title, artist, BPM, key, elapsed/remain | Glance identity | Yes |
| **Overview waveform** | Full-track skinny strip; playhead; cue flags | Structure at a glance | Yes |
| **Main / zoom waveform** | Playhead-centered or left-to-right zoom; beat markers | Phrase work, scrub | Yes (can stub scroll quality) |
| **Transport** | Play/pause, cue (set/return), sometimes reverse | Muscle memory | Yes |
| **Tempo** | Pitch fader + % / BPM readout; optional sync LED | Matching | Yes (sync optional off) |
| **Channel strip** | Gain + 3-band EQ (filter optional) | Mix verb | Yes (even on single-deck bake) |
| **Hot-cue pads** | 4–8 coloured pads mirrored on waveform flags | Jump + prep language | Yes (4 min, 8 ideal) |
| **Loop strip** | Auto/manual loop length | Performance depth | Phase 2 of strip |
| **Stem / Neural row** | 3–4 stem mute pads (expected 2025–26) | Creative love | **Not** bake-off v0 |
| **FX assign** | Slot or unit assign | Power users | Not bake-off v0 |

### 1.2 Layout trends (display modes)

| Trend | Who | Implication |
|---|---|---|
| **Horizontal dual-deck + center mixer** | Default Serato/RB performance | End-state layout; bake-off can be **one** strip first |
| **Vertical waveforms center** | Serato vertical mode | Alternate density; don’t bake-off two layouts |
| **Extended / minimized chrome** | Serato Extended | Waveform-first for laptop; DESIGN.md density tokens |
| **Stack** | Serato stack | Library-heavy workflows |
| **Controller-first hide** | Club / external mixer | UI still needs full strip for agent dogfood without HW |

**Bake-off choice:** one **horizontal deck strip** (Serato-clean density), not a full dual-deck skin. Second deck is copy of the same module.

### 1.3 Waveform trends (the strip’s soul)

| Trend | Evidence | Bake-off |
|---|---|---|
| **Overview + zoom pair** | Serato “main + overview”; universal | **Required** |
| **Frequency / EQ colour** | Serato spectrum colour; EQ-reactive prefs | Theme later; static colour ok v0 |
| **Hot cues as coloured flags** | Universal; colour-coded structure language | **Required** |
| **Vocal position band** | rekordbox AI vocal marks — strong pro love | **High-value stub** (marker layer even if offline analysis) |
| **Lyrics on waveform** | VirtualDJ AI 2026 | Out of scope |
| **Phrase / energy tint** | Rising prep tools | EXO energy as optional overlay later |
| **Stem visual lanes** | Neural Mix / stem UIs | After dual-deck dogfood |

**Performance trend:** waveforms stay **GPU-close**; never block audio. Bake-off judge includes “playhead moves under load without underrun.”

### 1.4 Transport + control trends

| Practice | Trend | Bake-off rule |
|---|---|---|
| Big primary **Play + Cue** | Always | 44×44+ touch targets; keyboard too |
| **Cue = set vs return** modes | Split across products | Document one behaviour; don’t invent third |
| Tempo as **% and BPM** | Universal | Both readouts |
| Sync visible, **not forced on** | Trust culture | Default off; LED state clear |
| Quantize for cues | Pro default often on | Prefer on for cue set |
| Pad banks (hot cue / loop / sample / stem) | Hardware-shaped software | Hot-cue bank only in v0 strip |
| Dark high-contrast | Booth | DESIGN.md dark-first |

### 1.5 What deck-strip UI is *not* trending toward

- Replacing the strip with a chat-only surface
- Hiding waveforms behind “smart” modes mid-set
- Modal dialogs on load fail (our house rule)
- WebView for the zoom waveform (Surface A native)

---

## 2. Co-pilot panel — industry + our differentiator

### 2.1 What the market does today (AI-adjacent)

| Product / pattern | AI UI shape | Live risk | Steal? |
|---|---|---|---|
| **VirtualDJ AI Prompt Folder** | Side/tool: “build me a 90s hip-hop set” | Prep / out-of-comfort gigs | **Prep** patterns yes |
| **VirtualDJ lyrics on waveform** | On-deck overlay | Clutter | No for v0 |
| **djay Neural Mix** | On-deck stem controls (creative, not “suggest next”) | Low if local | Stem row later, not “co-pilot” |
| **Spotify AI DJ** | Consumer radio + voice | **Not** pro dual-deck | Positioning anti-pattern |
| **rekordbox vocal / analysis** | On-waveform intelligence | Low | Marker quality yes |
| **DAW “Studio Copilot”** (music tools 2026) | Side panel: advice + commands, separate from transport | Good separation model | **Panel beside, not on** transport |
| **Generic chat bolted on** | Discord-in-the-corner | High distraction | **Reject** |

**Field truth from our discovery:** dance culture often **rejects** “AI plays the set.” Assist that **explains and waits for Ack** is the only live-safe shape. Prep-time intelligence is the wedge.

### 2.2 Strategy alignment (Migx)

From `Strategy-Current.md`: co-pilot **in the mix flow** (order, cues, transitions) — Cursor depth — **not** a bolted generic chat. Layer B: intents, ontology, “why next.”

| Differentiator | UI consequence |
|---|---|
| EXO / world model | Cards show **why** (key, energy, phrase), not just rank |
| Owned library first | Suggestions from **local/FSL**, not only stream |
| Explain + Ack | Primary actions: **Load to free deck**, **Queue**, **Dismiss** — never auto-play master |
| Multi-model later | Panel can show model/status strip; not v0 |
| Freemium | Panel visible free; depth gated later |

### 2.3 Co-pilot panel anatomy (recommended)

```text
┌─ Co-pilot ─────────────────────────────────────┐
│  Mode: Prep | Live (default Prep for dogfood)  │
│  Context: now playing A · free B · energy map  │
├─ Candidates (3–5 max) ─────────────────────────┤
│  #1  Artist – Title     BPM  Key  Δenergy      │
│      why: compatible key · phrase end in 16b   │
│      [ Ack → load B ]  [ Queue ]  [ Dismiss ]  │
├─ Transition hint (optional) ───────────────────┤
│  “EQ kill low on A at cue 3 · 8-bar blend”     │
│  (text only v0; no auto-EQ write)              │
├─ Trust ────────────────────────────────────────┤
│  last action · undo · “co-pilot cannot steal    │
│   single-writer CO of playing deck”            │
└────────────────────────────────────────────────┘
```

| Zone | Trend fit | Hard rule |
|---|---|---|
| **Collapsed by default mid-phrase?** | Optional later | Never cover waveform playhead |
| **Max 3–5 candidates** | Avoid VDJ feature density | Yes |
| **Why line always** | Differentiator vs Spotify DJ | Empty why = don’t show card |
| **Ack before load** | Live safety | Yes |
| **No write to playing deck transport** | P-06 / trust | Co-pilot loads **free** deck only |
| **Prep mode first** | Market acceptance | Ship Prep before Live suggest |

### 2.4 Spatial relationship (trends that fit us)

| Placement | Pros | Cons | Recommendation |
|---|---|---|---|
| **Right rail** (IDE-like) | Cursor/agent literacy; doesn’t fight dual-deck | Laptop width | **Default bake-off** |
| **Bottom drawer** | Phone/tablet | Hides mixer | No for desktop v0 |
| **Over waveform** | “Smart” overlays | Kills trust surface | Markers only (vocal), not chat |
| **Replace library tab** | Prep-centric | Loses crates mid-set | Co-pilot **beside** library, not instead |
| **Floating HUD** | Cool | Non-modal clutter | No |

Bake-off layout:

```text
┌──────────────┬────────────────────────┬────────────┐
│  Library     │  Deck strip (A)        │  Co-pilot  │
│  (minimal)   │  transport+wave+ctrls   │  panel     │
│              │                        │            │
└──────────────┴────────────────────────┴────────────┘
```

Single deck is enough for the earliest technical bake-off. For the product bake-off, the library must
graduate into `mod-music-management-mode`: search, tags, playlist memberships, visual recognition
cards, cached signal chips, next queue, and a one-action return to performance mode.

---

## 3. Why this pair is the right bake-off unit

| Criterion | Deck strip alone | Co-pilot alone | **Both** |
|---|---|---|---|
| Proves DJ literacy | ✓ | ✗ | ✓ |
| Proves Agent DJ story | ✗ | ✓ (hollow) | ✓ |
| Stresses DESIGN.md + Theme | ✓ | ✓ | ✓ |
| Stresses CO bind | ✓ | load intent | ✓ |
| Stresses Metal waveform path | ✓ | ✗ | ✓ |
| Separates Surface A vs B | A | B-capable | **boundary test** |
| Matches Cursor path | Editor chrome | Agent panel | **Agent on working base** |

Industry never ships “AI panel without a deck.” We should not either. Industry *is* shipping AI **beside** performance UI (VDJ prompt, DAW copilots) — we ship **smarter beside**, not **smarter instead**.

---

## 4. Bake-off acceptance (machine-checkable)

### 4.1 Deck strip (`mod-deck-strip` + `mod-waveform`)

| Check | Pass |
|---|---|
| Load track via list → header shows title/BPM | ✓ |
| Play/pause/cue round-trip on CO | ✓ |
| Overview + zoom waveform; playhead moves | ✓ |
| ≥4 hot-cue markers set/trigger | ✓ |
| Gain + 3-band EQ move CO | ✓ |
| Tempo % changes rate | ✓ |
| DESIGN tokens only (no free `#hex`) | ✓ |
| No `src/engine/**` drive-by | ✓ |
| 30s play, zero underrun (M4 dogfood) | ✓ |

### 4.2 Co-pilot panel (`mod-copilot` slice)

| Check | Pass |
|---|---|
| Shows ≤5 candidates with **why** text | ✓ |
| Ack loads **only free deck** (or queues) | ✓ |
| Dismiss removes card | ✓ |
| Cannot set play on master without Ack | ✓ |
| Panel does not cover playhead at default width | ✓ |
| Works offline with fixture/EXO stub if model down | ✓ (degraded empty state) |
| Independent review (P-08) | Codex |

### 4.3 Combined story (the demo script)

1. Launch NextGen → dark shell.
2. Pick track from thin library → deck strip loads.
3. Play; set two hot cues; see flags on overview.
4. Co-pilot shows next candidates with why.
5. Ack → second load path (even if deck B is stub) or queue list.
6. No modal; no underrun; no silent takeover.

---

## 5. Trends to follow vs ignore in this unit

### Follow

- Overview + zoom + cue flags
- Serato-clean transport density
- Vocal/structure **markers** (not full AI radio)
- Side **rail** co-pilot with explain + Ack
- Prep-first intelligence
- Same DESIGN.md for strip chrome + panel chrome

### Ignore / defer

- Stem pads on bake-off strip
- Lyrics on waveform
- Auto-mix / silent next-track
- Chat-first layout
- Full dual-deck + full mixer (comes after strip clones)
- Streaming browser inside co-pilot v0

---

## 6. Implementation notes (host split)

| Piece | Host | Why |
|---|---|---|
| Waveform + transport + EQ | **QML Surface A** | RT + Metal + CO |
| Hot-cue pads | QML | Bound to deck CO |
| Co-pilot list/cards | QML first; WebView later if chat-rich | Start QML so one Theme; shadcn island only if needed |
| Claude Design | Prototype **both** strip density + rail panel | Freeze into DESIGN.md before code |

**Claude Design prompt seed:**
“Dark booth dual-zone: left thin library, center one deck strip (overview+zoom waveform, transport, EQ, 8 cue pads), right co-pilot rail with 3 track cards each with why + Ack. Serato-clean, no purple AI slop, no modal.”

---

## 7. Module order update (bake-off scoped)

```text
Wave 0  DESIGN.md + Theme + shell
Wave 1  mod-music-management-mode (fixture library + tags/playlists + next queue + load free deck)
Wave 2  mod-deck-strip (transport + channel + pads) + mod-waveform
Wave 3  mod-copilot rail (prep candidates + Ack)
Wave 4  clone strip -> deck B + mini mixer  (full N5-N6)
```

Waves 1-3 = **bake-off unit**. Wave 4 = strangulation toward dual-deck product.

---

## 8. Bottom line

**Deck strip** is the industry-standard literacy object (transport + waveform + controls). Trends push richer **wave intelligence** (cues, colour, vocal marks) without abandoning the strip.

**Co-pilot panel** is our Agent DJ differentiator: a **side rail** with EXO-backed candidates, always-on **why**, and **Ack-to-load** — never Spotify-style silent DJ, never chat covering the playhead.

Baking them **together** proves the Cursor path: working performance chrome + agent surface on top, DESIGN.md-driven, judge-gated — the smallest unit that is still *obviously* Migx NextGen.

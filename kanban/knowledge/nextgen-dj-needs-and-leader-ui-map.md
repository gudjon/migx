---
id: nextgen-dj-needs-and-leader-ui-map
type: knowledge
title: "NextGen — DJ needs map + top-leader UI practices (what to build first)"
status: active
owner: gudjon
authored_by: grok-signal
created: "2026-07-19"
lastUpdated: "2026-07-19"
defers_to:
  - kanban/knowledge/nextgen-agent-dj-shadow-product.md
  - kanban/knowledge/nextgen-shadow-app-proposal.md
  - kanban/knowledge/nextgen-music-management-mode.md
  - kanban/knowledge/ui-framework-migration-map.md
  - kanban/Strategy-Current.md
  - kanban/knowledge/product-discovery-customer-leadership-migx.md
related:
  - initiative-ui-modernization
  - initiative-ai-djing-product
  - world-model-experience-ontology
  - dj-shared-library-capability
  - filesystem-driven-architecture
sources:
  - "Digital DJ Tips — Best DJ Software 2025/2026 + Who's Leading 2026"
  - "The DJ Revolution — Best DJ Software 2026"
  - "AlphaTheta rekordbox 7 feature pages (vocal waveform, stems)"
  - "X ethnography 2026-07 (stems love, library hate, vocal markers)"
  - "In-repo: x-interview rounds live reliability; EXO; FSL"
---

# NextGen — DJ needs map + leader UI practices

**Purpose:** Ground the Cursor-path NextGen shell in **what a DJ actually needs to complete a set**, then **what the top commercial products train users to love** — so module order is need-driven, not framework-driven.

**Product rule (owner):** all *new* UI work lands in NextGen; classic keep-alive only. This map orders those modules.

---

## 1. Core DJ job (the irreducible loop)

A working DJ session is not “a pretty skin.” It is a closed physical loop:

```text
OWNED MUSIC ON DISK  →  FIND / PREP  →  LOAD DECK  →  PLAY
                              ↑              ↓
                         CRATES/CUES    SECOND DECK
                              ↑              ↓
                         MIX / EQ / XFADER / SYNC
                              ↓
                         HEAR MASTER OUT (+ headphones cue)
```

Until that loop works **without AI**, NextGen is a demo. Co-pilot / EXO sits **on top** of a trustworthy loop, never instead of it.

### 1.1 Need stack (must → love → differentiate)

| Layer | Need | User-visible | Migx already has (engine) | NextGen UI module |
|---|---|---|---|---|
| **N0** | Sound path works | Audio in/out, no underrun | Engine + soundio | Launch + device strip (non-modal errors) |
| **N1** | **Filesystem / library** | Browse folders + library DB; import; search | Library, DAOs, scanners | `mod-music-management-mode` + folder access |
| **N2** | **Load a track** | Drag/double-click → deck has audio + waveform | Player/deck load CO | Load affordance on deck + browser |
| **N3** | **One deck transport** | Play/pause, cue, jog/seek, tempo | Engine deck controls | `mod-deck-strip` (single) |
| **N4** | **Waveform + position** | Overview + zoom; playhead; hot cues | Waveform render path | `mod-waveform` (Metal-close) |
| **N5** | **Second deck** | Same as N3–N4 on deck B | Multi-deck engine | Second `mod-deck-strip` |
| **N6** | **Mix them** | Channel EQ, gain, headphones cue, **crossfader**, optional sync | Mixer CO | `mod-mixer` / channel strip |
| **N7** | Prep intelligence | BPM/key/cues/energy, tags, playlist memberships, and community signal chips on tracks | Analyzer + FSL sidecar | Music mode cards + EXO chips |
| **N8** | Live assist (later) | Suggest next / transition hint | EXO, co-pilot | `mod-copilot` (after N6 green) |
| **N9** | Export / club path | USB, dual export, verify | Partial / strategy | Not NextGen v0 UI |

**v0 acceptance for “Agent DJ can mix”:** N0–N6 green on M4 dogfood, zero underruns, independent judge.

### 1.2 Filesystem access (N1 detail)

DJs need more than a pretty list:

| Capability | Why | UI practice leaders set |
|---|---|---|
| **Folder / volume browse** | Music lives on disk, external SSD, NAS | rekordbox / Serato tree + collection |
| **Import / watch** | Add without re-copying whole library | Watch folders, drag-in |
| **Search + crates/playlists** | Gig prep is crate work | Serato crates (loved); Serato 4.0 library overhaul (search, colour, emoji ratings) |
| **Analysis status** | BPM/key/waveform readiness | Progress without modal block |
| **Streaming later** | Apple Music / Spotify now table-stakes elsewhere | **v1+**; owned files first (Migx hybrid identity) |
| **Cross-app library later** | OneLibrary (RB/Traktor/djay) | FSL/EXO path; not day-1 UI |

**NextGen rule:** library is Surface B-capable (even WebView later) but **must** drive CO load into decks without leaving the app. Permission model: macOS folder access explicit; non-modal when denied.

### 1.3 Music management mode (N1/N7 detail)

Owner refinement, 2026-07-21: the library is not just a list under decks. NextGen needs a fast
full-screen **music-management mode** for arrangement and next-queue decisions. It should optimize for
recognition under pressure: track identity, version, tags, playlist memberships, key/BPM/energy,
mini-waveform, cue/vocal/phrase markers, and cached community signals.

This mode still belongs to the live product. It must preserve current playback, show compact deck
context, and return to performance mode with one action. External signals such as YouTube listens,
Mixcloud set appearances, SoundCloud activity, and Beatport metadata are optional cached context with
provenance, not live network dependencies.

### 1.4 Two decks + mix (N3–N6 detail)

Minimum dual-deck surface (industry-standard “performance mode”):

```text
┌──────────── Library / crates ────────────┐
│ search · playlists · columns · analysis  │
├──────── Deck A ───────┬────── Deck B ────┤
│ waveform overview     │ waveform overview│
│ zoom + cues           │ zoom + cues      │
│ play · cue · tempo    │ play · cue · tempo│
│ gain · 3-band EQ      │ gain · 3-band EQ │
├─────────── Mixer / master ───────────────┤
│ cue phones · master · CROSSFADER · sync  │
└──────────────────────────────────────────┘
```

| Control group | CO / engine reality | UI must not |
|---|---|---|
| Play/cue/tempo | Single-writer deck CO | Steal writers from hardware mapping |
| EQ / filter | Channel strip | Block RT |
| Crossfader | Mixer | Hide or bury (core mix verb) |
| Headphone cue | Cue/PFL | Force speakers-only dogfood fail |
| Sync (optional) | Engine sync | Auto-on by default mid-set (trust risk) |

**Strangle order inside NextGen (Cursor path):**
1. Theme + primitives
2. Music management mode (FS + search + tags + playlist memberships + next queue)
3. Single deck strip + load
4. Waveform
5. Second deck
6. Mixer / crossfader / cue
7. Prep chips (key/BPM/energy)
8. Co-pilot chrome

Do **not** start with co-pilot chrome before N6.

---

## 2. Top leaders (the “top 10” set)

Market-weighted set used for UI research (not a sales ranking):

| # | Product | Primary love / role |
|---|---|---|
| 1 | **rekordbox** (AlphaTheta) | Club standard, USB export, prep → CDJ path |
| 2 | **Serato DJ** | Clean performance UI, stems, scratch/working DJ feel |
| 3 | **Traktor Pro** | FX depth, remix/stems, flexible beatgrids (Pro 4) |
| 4 | **VirtualDJ** | Hardware breadth, AI/features velocity, stems quality |
| 5 | **djay Pro** (Algoriddim) | Innovation lead 2025–26, Neural Mix, Mac/iOS polish |
| 6 | **Engine DJ** | Standalone + stems on hardware, robust library |
| 7 | **Cross DJ** | Light/cross-platform rebuild, affordable stems |
| 8 | **Mixxx** | Open free path (us / upstream) |
| 9 | **DJ.Studio** | Prep/set planning UI (not live dual-deck center) |
| 10 | **Entry Lites** (Serato Lite, Traktor Play, free tiers) | Teach the dual-deck layout early |

Industry note (DDJT 2026): **innovation** leadership ≈ djay + VirtualDJ; **installed base / club** ≈ rekordbox + Serato; Traktor quieter on software, stronger on hardware cycles.

---

## 3. UI practices users love (cross-product)

### 3.1 Layout & information architecture

| Practice | Who trains it | User value | NextGen take |
|---|---|---|---|
| **Dual-deck + center mixer** is the mental model | All top live apps | Instant literacy | Default NextGen layout |
| **Library always reachable** without killing decks | Serato, RB, VDJ | Prep mid-set | Dock/split; never modal full-screen only |
| **Clean beginner surface, depth optional** | Serato Lite → Pro; Traktor Play | On-ramp | Progressive disclosure in DESIGN.md |
| **Performance vs Export/prep modes** | rekordbox | Club USB path vs laptop mix | Later; dogfood = performance first |
| **Dark, high-contrast, large transport** | All club-oriented UIs | Booth glanceability | Theme tokens: dark-first |

### 3.2 Waveforms (the trust surface)

| Practice | Evidence of love | NextGen |
|---|---|---|
| **Colour / EQ-reactive waveforms** | Serato EQ-coloured waveforms widely enabled | Theme + waveform prefs |
| **Overview + zoom** | Universal | Two-tier waveform module |
| **Hot cues on waveform** | Universal | Cue markers + colours |
| **Vocal position on overview** | Chris Lake et al. on rekordbox — “so so handy” | High-value EXO/analysis chip when ready |
| **Lyrics on waveform** | VirtualDJ AI lyrics 2026 | Optional later; not N0–N6 |
| **Phrase / structure hints** | Rising (energy/phrase tools) | EXO energy — prep columns first |

### 3.3 Library & filesystem

| Practice | Leader signal | NextGen |
|---|---|---|
| **Crates / smart playlists** | Serato identity | First-class crates |
| **Library search that doesn’t suck** | Serato 4.0 finally overhauling (crate search, colour, ratings) — “should have been standard years ago” | Search quality is product, not chrome |
| **Import cues from other apps** | djay 5.4 imports RB/Serato/Traktor cues | Migration trust; FSL import later |
| **OneLibrary-style portable prep** | AlphaTheta + NI + Algoriddim | Watch; FSL is our open answer |
| **Streaming in browser** | Apple Music + Spotify across leaders 2025 | Post dual-deck solid; owned FS first |
| **Cloud library** | RB cloud, VDJ CloudDrive | Optional; export integrity > cloud v0 |

### 3.4 Mixing & creativity UI

| Practice | Leader signal | NextGen |
|---|---|---|
| **4-stem pads (V/D/B/M)** | Expected 2026; Serato/VDJ quality praised; RB catching up | After N6; quality > checkbox |
| **Neural Mix / stem UX on hardware buttons** | djay + FLX10 Active Stem | Controller via CO later |
| **FX that feel pro** | Traktor reputation; VDJ 122+ FX catch-up | Engine effects, not UI first |
| **Flexible beatgrids** | Traktor Pro 4 selling point | Engine accuracy; UI shows grid lock |
| **Sync that doesn’t embarrass** | Universal anxiety | Off by default; visible state |

### 3.5 AI / assist (love vs reject)

| Practice | Field | NextGen |
|---|---|---|
| **AI prep assist** (set ideas, requests, outside comfort zone) | VirtualDJ AI Prompt Folder — positive for *gigs outside comfort zone* | Co-pilot **prep** first |
| **AI lyrics / karaoke** | VDJ | Niche segment |
| **Live AI next-track autopilot** | Public dance culture often rejects “AI DJ setlist” ads | Explain + Ack; never silent mid-set |
| **Vocal / structure analysis** | RB vocal markers loved | High trust visual, low risk |
| **Native rebuilds when RB hated** | “rekord spinner” style agent builds | Validate pain; still need load+mix first |

---

## 4. Per-leader UI snapshot (one line each)

| Leader | UI identity users buy | 2025–26 development trend |
|---|---|---|
| **rekordbox** | Club-shaped, export-first, familiar CDJ mental model | Streaming + OneLibrary + 4 stems + vocal waveform; innovation lag vs polish |
| **Serato** | Clean, fast performance, stems culture | Library 4.0 catch-up; streaming parity; stems quality loved |
| **Traktor** | Deep FX / remix / grid nerds | Hardware-led year; Pro 4 grids/stems; Play entry tier |
| **VirtualDJ** | Feature density + AI + video/karaoke | Strongest AI feature velocity (lyrics, prompt sets, FX pack) |
| **djay Pro** | Polished Mac/iOS, Neural Mix, modern UX | **Innovation leader** (hardware catch-up, Spotify return, OneLibrary, imports) |
| **Engine DJ** | Standalone robustness | Stems on hardware; streaming on standalone |
| **Cross DJ** | Simple/light | Full rebuild + stems, limited HW |
| **Mixxx** | Free/open, customizable | Our classic base; NextGen is the “Agent UI” graduate path |
| **DJ.Studio** | Set planning timeline | Prep UI ideas for co-pilot, not live deck chrome |
| **Lites** | Reduced dual-deck | Teach progressive disclosure |

---

## 5. Trends to follow vs ignore (for NextGen)

### Follow (table stakes or love)

1. **Dual-deck + mixer layout literacy**
2. **Waveforms as decision UI** (colour, cues, vocal markers)
3. **Library search/crates quality**
4. **Non-modal, dark, glanceable performance UI**
5. **Stems as expected** (quality bar; not fake 4 buttons)
6. **Prep intelligence on the track row** (BPM, key, energy, vocal)
7. **Import / portable library story** long-term (FSL/OneLibrary class)

### Follow carefully (after N6)

8. Streaming integrations
9. AI prompt set-builder (prep, not silent live)
10. Lyrics on waveform
11. Cloud sync

### Ignore / anti-goals for v0

- Mid-set modal dialogs (house rule)
- Feature-density VirtualDJ clone day one
- Electron dual-deck
- Automix as hero
- Second control plane (must stay CO)

---

## 6. Module roadmap (needs → NextGen packages)

| Order | Module | Closes need | Judge (machine-ish) |
|---|---|---|---|
| 0 | `mod-shell` + Theme + DESIGN.md | App launches dark | Launch smoke |
| 1 | `mod-music-management-mode` | N1 FS/search + next queue + N7 chips | Fixture library, tags/playlists, signal chips, queue/load-free-deck |
| 2 | `mod-deck-a` transport | N2–N3 | Load + play CO round-trip |
| 3 | `mod-waveform-a` | N4 | Playhead moves; cues render |
| 4 | `mod-deck-b` + waveform | N5 | Two independent playheads |
| 5 | `mod-mixer` | N6 | XF + EQ + cue phones audible path |
| 6 | `mod-track-chips` | N7 | BPM/key/energy columns from FSL |
| 7 | `mod-copilot` | N8 | Suggest + Ack only; no silent load |
| 8 | Stems / FX depth | Love layer | After dual-deck dogfood |

**Bake-off unit (preferred first product slice):** single **deck strip** (transport + waveform + controls) **+ co-pilot rail** — literacy + Agent DJ differentiator in one dogfoodable surface. Detail + acceptance: `nextgen-bakeoff-deck-strip-copilot.md`. Full dual-deck/mixer follows once the strip module clones cleanly.

**Product wedge beyond bake-off (owner 2026-07-21):** booth **modes** (PERFORM / ARRANGE / LIBRARY), multi-deck vertical flexibility (stage unlimited, play 4–6), and **graphical music-management** with crate tags + community signals — see `nextgen-modes-library-multideck.md`. Arrangement/next-queue is the cognitive bottleneck; decks alone are table stakes.

Each module: SPEC → CLAIM → BUILD → JUDGE → REVIEW → FLAG → STRANGLE (see nextgen methods §7).

---

## 7. Open product questions (owner)

1. **Music mode or deck chrome first?** Recommendation: **music mode + load + one deck** together as wave 1 (otherwise deck is a toy and the next-track job is under-modeled).
2. **How much Serato-clean vs Traktor-dense?** Recommendation: Serato-clean default; Traktor depth via progressive panels.
3. **Vocal markers before stems UI?** Recommendation: **yes** — high love, lower RT risk than live stems.
4. **Streaming in v1?** Recommendation: **no** until N6 solid.

---

## 8. Relationship to other docs

| Doc | Role |
|---|---|
| This file | **What DJs need + what leaders train users to love** |
| `nextgen-agent-dj-shadow-product.md` | How we ship (Cursor path, methods) |
| `nextgen-shadow-app-proposal.md` | Fleet discussion / ADR-007 |
| `ui-framework-migration-map.md` | Engine/host choice |
| Discovery interviews | Reliability/USB/AI-reject evidence (Opp-A/C) |

**Bottom line:** NextGen’s first job is **filesystem → two decks → mix**, with a **clean dual-deck + mixer** surface and **waveforms/library quality** that match what Serato/rekordbox users already trust — then differentiate with EXO chips and co-pilot **on top** of that loop, the way Cursor put Agent UI on top of a working editor base.

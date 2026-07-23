---
id: rekordbox-7-ui-teardown
type: knowledge
title: "rekordbox 7 UI teardown — steal / refuse map for Ritual NextGen modes"
status: active
owner: gudjon
authored_by: grok-signal
created: "2026-07-23"
lastUpdated: "2026-07-23"
defers_to:
  - kanban/knowledge/nextgen-modes-library-multideck.md
  - kanban/knowledge/nextgen-cognitive-load-perform-arrange-library.md
  - kanban/knowledge/nextgen-bakeoff-deck-strip-copilot.md
  - kanban/knowledge/mod-music-management-mode.md
  - kanban/knowledge/migx-brand-positioning-experience-designer.md
  - kanban/architecture/nextgen-ui-architecture.md
related:
  - initiative-ui-modernization
  - initiative-ai-djing-product
  - design-md-ui-modernization
sources:
  - "Screenshot study: rekordbox Performance dual-deck + library dock (2026-07-23)"
  - "https://cdm.link/rekordbox-7/ — cleaner UI, CPU, prep features (Kirn 2024)"
  - "https://rekordbox.com/en/feature/overview/ — v7 official feature matrix"
  - "X/field: curation sacred; AI-replace anxiety; library/crate search as workflow"
---

# rekordbox 7 UI teardown → Ritual / NextGen

**Job:** Competitive UI study. What to **steal**, **adapt**, or **refuse** for Migx NextGen modes (PERFORM / ARRANGE / LIBRARY) and brand **Ritual**.

**Subject layout (Performance mode):** dual decks + FX + overview waveforms + zoom waveforms + pads + **library docked under** (Collection Radar, Tree/Column, track list with mini-waves).

---

## 1. What this UI is (product role)

| Role | rekordbox strength |
|---|---|
| **CDJ prep + export** | Primary reason the product exists in the field |
| **Controller / laptop performance** | Full dual-deck grammar, stems, pads, FX |
| **Hardware-aligned chrome** | Matches Pioneer/AlphaTheta booth muscle memory |
| **Not** | Full-screen night-design / next-track-only brain |

CDM: lives dual life (prep tool + DJ software); **prep is where it lives or dies**. v7 sold: cleaner UI, ~56% less CPU vs v6, column view, dual player in export, Collection/Streaming Radar, intelligent cue creation, collaboration (plan-gated).

---

## 2. Layout anatomy (from screenshot)

```text
┌─ Mode / LINK / Professional ─────────────────────────────────┐
├─ FX1 │ FX2 │ CFX ───────────────────────────────────────────┤
├─ Overview waveform deck1 ───────────────────────────────────┤
├─ Overview waveform deck2 ───────────────────────────────────┤
├─ Deck1 header + zoom wave + cues │ Deck2 header + zoom wave ┤
├─ Phrase labels │ jog/pitch/EQ/stems │ jog │ pad FX ────────┤
├─ MIX / LEVEL / channel assign ──────────────────────────────┤
├─ Browser icons │ Collection │ Tree/Column │ Track list ─────┤
│  Radar/Mood…   │ mini-waves │ genre tree │ art+meta rows   │
└─────────────────────────────────────────────────────────────┘
```

**Cognitive cost:** continuous control (decks) + discrete decision (library) share one attention budget → **split-attention** (see cognitive-load knowledge).

---

## 3. Steal / adapt / refuse matrix

### 3.1 PERFORM (deck literacy)

| Pattern | Verdict | Ritual / NextGen action |
|---|---|---|
| Overview + zoom waveform pair | **STEAL** | Bake-off deck strip required pair |
| Hot cue colors A–H on overview + list | **STEAL** | Cue flags + pad colors; consistent language |
| Phrase labels (Intro / Drop / Break / Outro) | **STEAL** | EXO/structure layer; optional auto then edit |
| Vocal / stem mute strips (DRUMS VOCAL INST) | **STEAL (later)** | After dual-deck dogfood; not v0 if scope tight |
| BPM / key / KEY SYNC / BEAT SYNC / MASTER | **STEAL** | Deck header badges; single-writer CO rules apply |
| Jog + pitch ring + EQ 3-band | **STEAL** | Club literacy; match controller expectations |
| Pad FX bank | **ADAPT** | Secondary; don’t default-max chrome on PERFORM |
| Dual overview always both full width | **ADAPT** | Default dual; stack/vertical for N>2 decks |
| FX1/FX2 always top strip | **ADAPT / hide** | Collapse FX in PERFORM minimal; expand on demand |
| “Professional” density as default | **REFUSE as only mode** | Expert full chrome optional; not the only perform layout |

### 3.2 ARRANGE (next-track / night design)

| Pattern | Verdict | Ritual / NextGen action |
|---|---|---|
| Library always under decks | **REFUSE** | Full-screen ARRANGE hop; thin now-ribbon only |
| Track list with mini-wave previews | **STEAL** | Track cards / list mode in ARRANGE+LIBRARY |
| Rank / rating / streaming icons columns | **ADAPT** | Personal history + crates first; stream badges optional |
| Collection Radar (similar in *my* library) | **STEAL (assist)** | Co-pilot / radar as **why** chips; Ack to stage |
| Streaming Radar | **ADAPT** | Prep/LIBRARY only; never mid-set dependency |
| Intelligent Playlist auto-fill | **ADAPT carefully** | Suggest for stage queue; never silent load (Automix enemy) |
| Dual Player for mix-point audition (export) | **STEAL for PREP** | Prep/ARRANGE offline audition; not RT dual-analyze spam |
| Intelligent Cue Creation | **ADAPT** | Prep assist; learn from user playlist; always editable |
| No dedicated “stage 1–5 next” canvas | **GAP → OWN** | Ritual differentiator: staged queue + free-deck load |
| No function-crate roles (opener/peak/reset) | **GAP → OWN** | Field + brand: role chips over genre-only |

### 3.3 LIBRARY (prep / organize)

| Pattern | Verdict | Ritual / NextGen action |
|---|---|---|
| Column View (Finder hierarchy) | **STEAL** | Optional LIBRARY layout |
| Tree View + genre folders | **STEAL** | Plus **function crates** as first-class |
| Collection Filter (date/genre/artist/album) | **STEAL** | Fast filters; add energy/key/played-tonight |
| Media browser icon rail | **ADAPT** | Sparse icons; booth-sized hit targets |
| Artwork-forward streaming browse | **STEAL** | Cover-first grid in LIBRARY |
| Sub-browser dual collection panes | **ADAPT** | Power-user prep; not mid-set default |
| Collaborative playlists | **WATCH** | Nice for B2B; privacy + plan complexity |
| Cloud analysis / CloudDirectPlay | **REFUSE as required** | Local-first brand (X field); cloud optional later |
| Paywall on organization features | **REFUSE culture** | Don’t gate basic arrange/library on subscription maze |

### 3.4 Intelligence / brand alignment

| Pattern | Verdict | Ritual |
|---|---|---|
| Soft “software learning” not “AI DJ” | **STEAL tone** | Quiet intelligence; never hero “AI DJ” |
| Vocal AI on overview | **STEAL if accurate** | Structure at a glance |
| Subscription maze for pro features | **REFUSE** | Clear value; instrument trust |
| Hardware unlock to free features | **WATCH** | Ecosystem play; not our model |

---

## 4. Mode mapping (accept / reject rows)

### PERFORM — accept

- Overview + main waveform, playhead, beatgrid  
- Cue flags + phrase marks  
- Header: title, artist, BPM, key, remain, sync/master  
- Transport, pitch, EQ, gain  
- Optional: stems, pad FX (progressive disclosure)  
- Thin **next-1** chip (not full library)

### PERFORM — reject

- Full collection tree + multi-column browser  
- Radar discovery chrome  
- Dense dual FX always visible as default  
- Modal overlays on transport  

### ARRANGE — accept

- Full-screen candidates (grid/list) with mini-wave or art  
- Stage queue 1–5  
- Free-deck target + Ack load  
- Filters: key-compat, energy, role crate, played-tonight  
- Co-pilot / radar-like “similar” with **why**  
- Now ribbon (what’s playing, bars left)

### ARRANGE — reject

- Full dual-deck jogs as primary chrome  
- Live network / streaming required  
- Auto-play next without Ack  

### LIBRARY — accept

- Column + tree + filter  
- Cover grid  
- Function crates + tags  
- Offline enrich / analysis  
- Intelligent cue *suggestions* (editable)

### LIBRARY — reject

- Must stay under perform decks  
- Cloud-only analysis as default path  

---

## 5. DESIGN.md / visual tokens (steal carefully)

| rekordbox cue | Ritual DESIGN direction |
|---|---|
| Dark booth base | Keep (already NextGen path) |
| Blue accent “calm pro” | Optional accent family — not Pioneer clone |
| High-contrast wave (blue/gold spectrum) | Frequency-color optional; legibility first |
| Dense 11–12pt controls | **Bump type** mid-set (cognitive-load) |
| Icon-heavy left rail | Prefer labeled mode bar (PERFORM / ARRANGE / LIBRARY) |

---

## 6. Competitive one-slide

```text
rekordbox:  excellent perform + CDJ prep workstation
            library is a dock, not a mode
            intelligence assists prep; plan maze costs trust

Ritual:     perform literacy (steal waveforms/cues)
            + full-screen ARRANGE (own next-track under load)
            + LIBRARY as schema factory (function crates)
            + judgment-serving assist (never Automix hero)
```

---

## 7. Implementation priority for Claude (from this teardown)

1. **PERFORM strip** — overview+zoom+cues+header (bake-off).  
2. **Mode shell** — switch; now ribbon; no library under decks by default.  
3. **ARRANGE cards** — mini-wave/art, stage 1–5, free-deck Ack.  
4. **LIBRARY column/filter** — plus function crates.  
5. **Assist chips** — similar-in-collection / vocal mark — offline, explainable.  

Judge acceptance remains `mod-music-management-mode` + bake-off contracts.

---

## 8. Claims

| Claim | Confidence |
|---|---|
| Overview+zoom+cues is table-stakes PERFORM literacy | high |
| Docked library under dual decks is split-attention debt | high (CLT + field) |
| Collection Radar class features are good *assist*, bad *autopilot* | med–high |
| Ritual differentiates on mode architecture + night design, not denser FX | high |

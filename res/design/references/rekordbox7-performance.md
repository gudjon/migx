# Reference analysis — Rekordbox 7, Performance view (2-deck)

Industry reference for the NextGen design gate (`nextgen-ui-architecture` → per-module design gate).
Rekordbox is the market-leading DJ software; v7 (2024–25) is the current design-trend baseline. We
**learn the trends, we do not clone the density.** This is the SSoT wireframe drafts cite as
"industry-trend grounding."

## What's on the screen (top → bottom)
1. **Global toolbar** — mode dropdown (PERFORMANCE), view/FX/pad/mixer/REC toggles, LINK, license
   badge ("Professional"), settings, master meter, clock. ~30 controls before any music.
2. **FX rack (FX1 / FX2 + CFX)** — 3 chained FX per deck (DELAY/ECHO/SPIRAL), colour FX, stem targets.
3. **Dual scrolling waveform** (the visual center) — two decks stacked, beat-aligned, **frequency- and
   stem-coloured**, with a live **beat/bar countdown to the next cue** ("17.1 Bars") and phase meter.
4. **Per-deck identity row** — art · **title** · **artist** · **BPM** · **KEY** · **time
   (−remaining / elapsed / total)** · KEY SYNC · BEAT SYNC · MASTER · key-shift (`< Gm ±0 >`).
5. **Per-deck summary waveform** — whole-track overview with **named hot-cue flags (A–H)** and a
   **phrase/structure colour bar** (Intro/Drop/Break… as coloured segments) + stem mute (DRUMS/VOCAL/INST).
6. **Deck controls** — **named hot-cue grid** (A Intro, B Phase A1, C Break, D Drop 1, … H Outro),
   beatjump, jog (BPM + pitch %), CUE, Q(uantize), play, EQ mixer (HIGH/MID/LOW + stem TRIM), Pad-FX list.
7. **Mixer** — headphone CUE mix/level, channel assign, crossfader, master out + REC.
8. **Browser (huge)** — **Track Suggestion** tree (Collection Radar, Streaming Radar, Era, Mood,
   Association) | Collection grid (rank · **preview mini-waveform** · title/artist · BPM · KEY · art) |
   genre tree | playlist. Loaded tracks highlighted **green**.

## Adopt — trends that match the DJ mental model / lower load
- **Track-identity anchor per deck**: art · title · artist · **BPM · KEY** · time. The always-visible
  "what am I playing / is it mixable?" answer. Universal across Serato/Traktor/VirtualDJ/djay too.
- **BPM + KEY are the lingua franca** — shown on decks, browser rows, *and* suggestions. Tempo + harmony
  is how DJs reason about the next track. (Our EXO co-pilot already speaks this: `tempo_compat` + Camelot.)
- **Named, colour-coded structural hot cues** (Intro/Drop/Break/Outro) — the song's roadmap as text +
  colour. A large load reducer vs recalling timings.
- **Phrase/structure colour bar** under the overview — song sections at a glance.
- **Related-track intelligence** (Collection/Streaming Radar, Mood, Association) — rekordbox already
  ships "what to play next." This validates our ARRANGE/co-pilot thesis; the market is moving here.
- **Per-track preview mini-waveform + stars + BPM/KEY in browser rows** — decide without opening a track.
- **Loaded-track highlight** in the library — instant "where am I in the crate."
- **Stems (DRUMS/VOCAL/INST) first-class** — the 2024–25 trend.

## Reject / diverge — our lower-load, non-modal, agent thesis
- **Density**: ~200 controls, tiny targets, everything at once. We show **fewer, bigger, mode-scoped**
  (PERFORM/ARRANGE/LIBRARY separate concerns to cut per-screen load).
- **Chrome weight**: license badges, MIDI toggles, permanently-visible knob banks. Our **admin chrome is
  minimal + on-demand** (hover/help), never permanent clutter.
- **Manual harmonic reasoning**: rekordbox *shows* key; the DJ still computes compatibility in their head.
  Our **co-pilot scores it** (tempo + Camelot) and surfaces the call — the suggestion is the hero, not a
  15-column grid the DJ must scan.
- **Modal everything**: dialogs mid-set. We are **non-modal by law** (invariant #5).

## Implications for our build order
- **Track-identity anchor is the next deck module** — cheap, universal, lowest-load, and it **unblocks
  ARRANGE** (title/artist/BPM/KEY is the same vocabulary the browser + co-pilot use → build the badge
  once, reuse on both surfaces).
- **BPM/KEY badge** should be a reusable primitive/component (deck + ARRANGE row + co-pilot chip).
- **Structural hot cues + phrase colours** = a later, higher-value deck module (needs analysis data).
- **ARRANGE** should lead with **related-track intelligence + BPM/KEY/energy + community signal**, beating
  rekordbox by making the *recommendation* the hero rather than a dense grid.

## Bindings this reference implies (verified in our QML)
- title/artist/art: `Mixxx.PlayerManager.getPlayer(group).currentTrack?.{title,artist,coverArtUrl,color}`.
- BPM: `[ChannelN],bpm` (CO). KEY: `[ChannelN],key` (CO, numeric 1–24 → musical + Camelot in the ViewModel).

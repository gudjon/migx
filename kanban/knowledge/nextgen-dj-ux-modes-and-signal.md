---
id: nextgen-dj-ux-modes-and-signal
type: knowledge
title: "NextGen DJ UX — full-screen modes, multi-deck flexibility, community signal (owner-DJ evidence)"
status: active
owner: gudjon
created: "2026-07-21"
lastUpdated: "2026-07-23"
evidence_kind: owner-DJ first-hand friction (DC-PDCL CustomerEvidenceCaptured)
related:
  - nextgen-agent-dj-shadow-product.md
  - nextgen-shadow-app-proposal.md
  - copilot-product-assumptions.md
  - world-model-experience-ontology.md
  - ui-non-modal-error-ux
---

# NextGen DJ UX — modes, multi-deck, community signal

First-hand DJ direction from the owner (2026-07-21). This is real customer evidence (DC-PDCL-1.1), not a
guess — treat it as load-bearing for the NG module roadmap and the co-pilot.

## The core job: reduce cognitive load, find the next track fast
The hardest part of DJing at a **busy club is not the mixing mechanics — it is music arrangement and
management under cognitive load**: deciding and finding *what to cue next*, fast, while performing. NG's
UX exists to minimize that load. (This **confirms co-pilot open-assumption A4** — track selection *is*
the job — see `copilot-product-assumptions`.)

**Research deepen (2026-07-23):** frameworks + measure probes + anti-patterns live in  
`nextgen-cognitive-load-perform-arrange-library.md` (CLT / Endsley SA / dual-task / DJ HCI / X field).

## Full-screen modes the DJ switches between (not one cluttered screen)
Clear, purpose-built full-screen contexts, entered/exited fast, so nothing extraneous competes for
attention (and nothing blocks the flow — `ui-non-modal-error-ux`):

1. **Performance mode (multi-deck)** — the live mix surface; transport-first; minimal load.
2. **Music-management mode** — the differentiator: the next-track finder. High graphical UX so songs are
   **instantly recognizable** (artwork, waveform/energy preview, key/bpm), plus **tags**, **which
   playlists a song is in**, and **community signal** (below).
3. *(later modes: set prep/planning = the set-planner, FX, etc.)*

The current mode is unmistakable; switching is instant and low-friction.

## Multi-deck flexibility
- **Dual-deck is the default**, but decks scale: **vertical deck layout, N loaded decks** — effectively
  unlimited *loaded* capacity (technology is not the constraint).
- **Max simultaneously *playable* ~4–6** — a real mixing constraint, not a tech one.
- Layout adapts 2 → N without a mode change; the DJ scales deck count to the moment.

## Community signal — a new EXO dimension
To help choose the next track, the management surface shows **social-proof / popularity** per track:
- YouTube listens/views.
- Number of DJ-set playlists the track appears in on **Mixcloud, SoundCloud, Beatport**.

These become an EXO ontology property (`community_signal`) that feeds **both** the visual management
screen **and** the co-pilot's "why next" ranking, alongside harmonic/tempo/energy.

**Data pipeline (researched 2026-07-21):** SSoT `nextgen-community-signal-data-sourcing.md` + chip
schema in `mod-music-management-mode.md` §4. **YT views feasible offline;** MC/SC/BP do **not** yield a
clean reverse “N sets” index — v1 chips = YT + Beatport chart + SC plays + local; true setlist heat =
licensed 1001Tracklists-class feed (v2). UX/ontology slot remains; enrich is PREP/offline only.

## How this feeds the build
- **First-module candidate:** the **music-management mode** is the strongest first NG module — it is the
  core differentiator (find-next-track / cognitive-load) and where the co-pilot + EXO + community signal
  converge. (For the *engine bake-off* specifically, a smaller **deck strip** may still be the cleaner
  apples-to-apples unit — decide in ADR-007.)
- **Co-pilot extension:** add a `community_signal` term to `score_candidate` once the data exists —
  declared an **open assumption** until validated (weighting community proof vs harmonic/tempo is untested).
- **EXO schema:** add an optional `community_signal` block to `migx.song-ontology`; the
  `ontology_from_sidecar` bridge maps it through when present.

## Discovery scorecard update
- **Confirms:** track-selection-under-cognitive-load is the job (co-pilot A4 → confirmed by owner evidence).
- **Adds:** community signal as a decision input (new co-pilot dimension + management-screen surface).
- **Reshapes:** NG module priority leans toward the music-management mode.

---
id: capability-catalogue
type: architecture-ddd
title: "Migx capability catalogue — product domain map (DDD)"
status: active
owner: gudjon
created: "2026-07-23"
lastUpdated: "2026-07-23"
defers_to:
  - kanban/architecture/README.md
  - kanban/architecture/nextgen-ui-architecture.md
  - kanban/architecture/decisions/ADR-005-open-core-plus-proprietary-intelligence.md
related:
  - res/design/references/rekordbox7-performance.md
  - res/design/references/serato-djpro-performance.md
  - res/design/references/traktor-pro4-performance.md
---

# Capability Catalogue — Migx product domain map

The **product / capability** view of Migx: *what the software does for the DJ*, decomposed into bounded
capabilities. Complementary to the **technical** context roster in [`README.md`](../README.md) (how the
code is organized around the real-time boundary). Each capability maps **down** to one or more engine
contexts (`arch-*`) and **up** to a NextGen UI module + a mode (PERFORM / ARRANGE / LIBRARY / chrome).

**Read with:** the capability set is the category baseline (digitaldjtips "best software" roundup, 14
areas) plus our differentiator. UI/UX stance for every capability is grounded in
`res/design/references/` (rekordbox 7 · Serato DJ Pro + djworx · Traktor Pro 4) and the NextGen
invariants (token-only, dumb-view + ViewModel, non-modal, minimal chrome, design-gate-first).

## DDD subdomain classification (where we invest — ADR-005)
- **Core** (the differentiator; invest most): the **Intelligence** subdomain — co-pilot track
  suggestion (EXO), harmonic/energy reasoning, community signal. The landscape roundup found **no**
  competitor doing AI/smart recommendation ("remains emergent") — this is our whitespace.
- **Supporting** (table-stakes; do *well*, lower-load than rivals): Playback, Mixing, Collection.
- **Generic** (commodity; correct + minimal): Output, Integration, Chrome.

Strategy follows: the co-pilot is where design effort and originality concentrate; supporting
capabilities win on **cognitive load** (the djworx critique — "smarter use of screen real estate,
prioritise vital info over hardware duplication"), not feature count.

## Separation-of-concerns law
Each capability **owns exactly one concern** and names what it does **not** own. Capabilities never reach
into each other's internals — they compose via the ControlObject `[Group],key` bus, typed props/signals,
and shared kernel (`Theme` tokens + primitives). One writer per CO (P-06). A capability's UI is a bounded
NextGen module (its own dir + `MODULE.md`); its truth (bindings, tokens, keymap, wireframe) lives at the
SSoT paths named in its card — cited, never copied (MG-3).

## Verification notes (Codex 2026-07-23)
- Engine-context mappings name existing `arch-*` bounded contexts only. External feeds, EXO tools, and
  future services can appear in SSoT notes, but not as invented context IDs.
- The ControlObject bus is an implicit seam for QML modules. List `arch-control-messaging` only when the
  capability owns input/binding semantics; otherwise name the context that owns the underlying product
  truth.
- Intelligence is core under ADR-005. Supporting/generic capabilities may feed Intelligence, but they do
  not become core unless they create the co-pilot/session-planning advantage.

## Roster
| id | subdomain | class | UI mode | engine context(s) | UI module (status) |
|---|---|---|---|---|---|
| cap-deck-transport | Playback | supporting | PERFORM | arch-engine-realtime, arch-mixer-decks | components deck-transport (**built**) |
| cap-track-identity | Playback | supporting | PERFORM | arch-track-model | components deck-identity (**built**) |
| cap-deck-clock | Playback | supporting | PERFORM | arch-engine-realtime | components deck-clock (**built**) |
| cap-waveform | Playback | supporting | PERFORM | arch-waveform-render, arch-rendergraph | planned (Metal-pinned) |
| cap-hotcues | Playback | supporting | PERFORM | arch-engine-realtime (cue) | planned |
| cap-loops | Playback | supporting | PERFORM | arch-engine-realtime (loop) | planned |
| cap-tempo-sync | Playback | supporting | PERFORM | arch-engine-realtime | planned |
| cap-mixer-eq | Mixing | supporting | PERFORM | arch-mixer-decks | planned |
| cap-fx | Mixing | supporting | PERFORM | arch-effects-chain | planned |
| cap-stems | Mixing | supporting | PERFORM | arch-engine-realtime, arch-analyzer | planned |
| cap-headphone-cue | Mixing | generic | PERFORM | arch-mixer-decks | planned |
| **cap-copilot-suggestion** | **Intelligence** | **core** | ARRANGE | arch-library-db, arch-track-model, arch-analyzer | planned (tools/exo/ exists) |
| **cap-harmonic-key** | **Intelligence** | **core** | ARRANGE/LIBRARY | arch-analyzer, arch-track-model | partial — colour-coded KEY badge **built**; compatibility scoring planned |
| cap-energy-structure | Intelligence | core | ARRANGE | arch-analyzer | planned |
| cap-community-signal | Intelligence | core | ARRANGE | arch-musicbrainz, arch-library-db, arch-track-model | planned (Grok sourcing) |
| cap-library-crates | Collection | supporting | LIBRARY | arch-library-db | planned |
| cap-analysis-prep | Collection | supporting | LIBRARY | arch-analyzer, arch-sources-decode | planned |
| cap-streaming | Collection | generic | LIBRARY | arch-library-db, arch-sources-decode | planned |
| cap-recording | Output | generic | chrome | broadcast+recording (cross-cutting) | planned |
| cap-broadcast | Output | generic | chrome | broadcast+recording (cross-cutting) | planned (non-modal fix landed) |
| cap-controllers-midi | Integration | generic | chrome | arch-controllers-mapping | planned |
| cap-keyboard-shortcuts | Integration | generic | all | arch-controllers-mapping, arch-qml-ui | built (KEYMAP + ng-ui-lint) |
| cap-sampler | Integration | generic | PERFORM | arch-engine-realtime (samplers) | planned |
| cap-mode-shell | Chrome | supporting | all | arch-qml-ui | main.qml shell (**built**) |

## Capability cards (concern · SSoT · UX stance)
Format per card: **owns / not** · **SSoT** · **UX stance** (grounded in references).

### Playback (PERFORM · supporting)
**cap-deck-transport** — *owns*: play/pause intent per deck. *not*: tempo, cue, load. *SSoT*:
`[ChannelN],play` + `track_loaded`; `res/qml/nextgen/components/` MODULE.md. *UX*: one big action, state
cue, no skeuomorphic platter (djworx: platters waste laptop real-estate). **Built.**

**cap-track-identity** — *owns*: "what's loaded / is it mixable" — art · title · artist · **BPM · KEY**.
*not*: transport, waveform, suggestion. *SSoT*: `currentTrack.{title,artist,coverArtUrl}` + `[ChannelN],bpm`/`key`;
`res/design/wireframes/deck-track-identity.md`. *UX*: universal anchor (3/3 apps); **KEY is colour-coded**
(Traktor); compact + tileable for multi-deck; reusable KEY/BPM badge shared with ARRANGE. **Built.**

**cap-deck-clock** — *owns*: elapsed/remaining/total time. *not*: transport, tempo. *SSoT*: `[ChannelN],duration`+`playposition`;
deck MODULE.md. *UX*: **−remaining is the loud number** (rekordbox/Traktor both lead with it), red at mix-out. **Built.**

**cap-waveform** — *owns*: the scrolling track visual + beat alignment. *not*: transport/cue writing.
*SSoT*: arch-waveform-render; DESIGN.md waveform colours. *UX*: **RGB frequency colouring** table-stakes
(Serato-pioneered); vertical (Serato) vs horizontal (rekordbox/Traktor) is a deliberate module choice.
Metal-pinned — planned post-unpin. **Planned.**

**cap-hotcues** — *owns*: preset jump points. *not*: loops (sibling). *SSoT*: `[ChannelN],hotcue_N_*`; KEYMAP.
*UX*: **colour-coded**, support **named (rekordbox structure) and numbered (Serato pads)**; pad-legible. **Planned.**

**cap-loops** — *owns*: repeatable sections (auto + manual). *SSoT*: `[ChannelN],loop_*`; KEYMAP. *UX*: Traktor
"industry-leading looping" is the bar; keep controls low-load, beat-quantised. **Planned.**

**cap-tempo-sync** — *owns*: pitch/tempo + beat-sync + master. *not*: EQ. *SSoT*: arch-engine-realtime;
`[ChannelN],rate`/`sync_*`/`bpm`. *UX*: sync visible but not dominant; no oversized BPM (djworx critique). **Planned.**

### Mixing (PERFORM · supporting)
**cap-mixer-eq** — *owns*: per-channel gain/HI-MID-LO/filter/fader/crossfader. *SSoT*: arch-mixer-decks;
`[ChannelN],volume`/`pregain`/`filter*`/`[Master],crossfader`. *UX*: Traktor's internal mixer is the model
for laptop/controllerless play; **mode-scoped / on-demand knobs**, not always-on knob-walls. **Planned.**

**cap-fx** — *owns*: effect units + assignment. *SSoT*: arch-effects-chain. *UX*: rekordbox/Traktor FX racks
are dense; we surface fewer, larger, per-need. **Planned.**

**cap-stems** — *owns*: real-time DRUMS/BASS/OTHER/VOCALS separation + mute/level. *SSoT*: arch-analyzer +
arch-engine-realtime. *UX*: 2024–25 trend (rekordbox 7, Traktor 4, VirtualDJ); 4 clear lanes. **Planned.**

**cap-headphone-cue** — *owns*: pre-listen routing/mix. *SSoT*: arch-mixer-decks; `[ChannelN],pfl`. *UX*: minimal. **Planned.**

### Intelligence (ARRANGE · **core — the differentiator**)
**cap-copilot-suggestion** — *owns*: "what to play next" — ranked candidates with *reasons*. *not*: playback,
raw library CRUD. *SSoT*: `tools/exo/` (copilot_why_next, set_planner, ontology_from_sidecar) + arch-library-db.
*UX*: **the recommendation is the hero** — we score mixability (tempo + Camelot) and surface the call, vs
rivals who show key and leave the DJ to compute. Non-modal, glanceable chips. **The core bet.** **Planned.**

**cap-harmonic-key** — *owns*: key detection → Camelot/Open-Key + **compatibility scoring**. *SSoT*:
arch-analyzer + `tools/exo` key→Camelot. *UX*: **colour-coded key** everywhere (Traktor) — deck badge,
ARRANGE rows, co-pilot chips; compatible = scannable by colour. **Planned (badge in deck-track-identity).**
Boundary: harmonic-key owns the reusable key representation and pairwise compatibility primitive; the
co-pilot owns ranked recommendations that consume it.

**cap-energy-structure** — *owns*: energy/vibe + song structure (intro/drop/break). *SSoT*: arch-analyzer.
*UX*: feeds structural hot cues + set-arc planning. **Planned.**
Boundary: energy-structure owns derived track facts; the co-pilot owns set-level choices that consume
those facts.

**cap-community-signal** — *owns*: cached external popularity/heat chips with provenance. *SSoT*:
offline sidecars/cache + arch-library-db/track-model persistence + arch-musicbrainz-style async worker
patterns; Grok sourcing notes. *UX*: signal chips per track; v1 YT/BP/SC/local heuristics only, true
setlist appearances require licensed v2 feed. **Planned.**

### Collection (LIBRARY · supporting/generic)
**cap-library-crates** — *owns*: collection/playlists/crates browse + organize. *SSoT*: arch-library-db.
*UX*: loaded-track highlight; preview mini-waveform + BPM/KEY per row (all three rivals). **Planned.**

**cap-analysis-prep** — *owns*: pre-gig analysis (BPM/key/beatgrid/waveform/energy). *SSoT*: arch-analyzer.
*UX*: rekordbox's "unrivalled prep" is the bar; run ahead-of-time, never mid-set. **Planned.**

**cap-streaming** — *owns*: streaming-service tracks. *SSoT*: arch-library-db + arch-sources-decode adapters. *UX*: uniform
with local rows. **Planned (generic).** Boundary: when streaming grows beyond source/decode + library
adapters, create a real network-services bounded context instead of reusing an unnamed pseudo-context.

### Output · Integration · Chrome (generic)
**cap-recording** / **cap-broadcast** — *owns*: set capture / live stream. *SSoT*: broadcast+recording
cross-cutting. *UX*: **non-modal** status only — the broadcast modal-error was the anti-pattern we fixed
(`ui-non-modal-error-ux`). **Planned / fix landed.**

**cap-controllers-midi** — *owns*: hardware mapping. *SSoT*: arch-controllers-mapping + `res/keyboard/`+KEYMAP
(one binding, two surfaces). **Planned.**

**cap-keyboard-shortcuts** — *owns*: keyboard action declarations, collision hygiene, and QML shortcut
coverage. *SSoT*: `res/design/KEYMAP.md` + `res/keyboard/en_US.kbd.cfg` + `just ng-ui-lint`. *not*:
hardware MIDI/HID mapping. **Built.**

**cap-sampler** — *owns*: one-shot/loop sample slots. *SSoT*: arch-engine-realtime samplers. **Planned.**

**cap-mode-shell** — *owns*: the mode switcher + non-modal surface + minimal chrome. *SSoT*: `res/qml/nextgen/main.qml`;
KEYMAP (⌘1/2/3 + Tab). *UX*: minimal admin chrome, on-demand hints. **Built.**

## How a new capability enters (the iterated process)
1. Add/confirm its row here (concern, SoC, SSoT, engine context, class).
2. Design-gate draft in `res/design/wireframes/<module>.md` (wireframe + value + cognitive-load + trend
   grounding citing `res/design/references/`) → owner review.
3. On approval, build the bounded module (token→primitive→view/ViewModel→MODULE.md→judge), verify, commit.
4. Update this card's status; harvest durable UX learnings into the reference/DESIGN.md/KEYMAP SSoT.

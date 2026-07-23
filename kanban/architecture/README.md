---
id: migx-architecture-map
type: architecture-index
title: "Migx architecture map — bounded contexts & domain charters"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/architecture/DDD-BUILDOUT-PLAN.md
  - AGENTS.md
---

# Migx Architecture Map

The living map of Migx's bounded contexts (DDD cards) and per-domain charters (`src/**/AGENTS.md`).
Tool-agnostic — Claude Code, Codex, and Grok all read the same map. **Pointers, never copies** (MG-3):
a card names relationships and invariants; what the code *is* stays in the code.

The load-bearing axis is the **real-time boundary**, not deployment — every card declares its
`thread_domain` (rt-audio | gui | gpu-render | worker | any) and `rt_safety` (hard | soft | none),
because the two ways a change silently breaks Migx are (1) violating the audio deadline and (2)
botching Qt ownership.

**Platform floor:** macOS **26.\*+** · Apple Silicon only ([ADR-006](decisions/ADR-006-platform-scope-apple-silicon.md)).  
**Refactor map (feature-preserving Apple-native waves):**  
[`kanban/knowledge/architecture-apple-silicon-macos26-refactor-map.md`](../knowledge/architecture-apple-silicon-macos26-refactor-map.md).

- Cards: `ddd/bounded-contexts/<id>.md` (template: `_TEMPLATE.md`)
- **Product-capability view** (what Migx does for the DJ, mapped to these contexts + NextGen UI modules +
  UI/UX guidelines): [`ddd/capability-catalogue.md`](ddd/capability-catalogue.md)
- Seam docs: `ddd/boundaries/<slug>.md`
- Context-relationship narrative: `ddd/context-map.md`
- Buildout plan (format, full roster, lint): `DDD-BUILDOUT-PLAN.md`
- The roster table below should be **generated** from card frontmatter in Phase 3 (`ddd/gen-index.py`).

## Bounded-context roster (16)

<!-- ddd-roster:start -->
| id | src paths | thread_domain | rt_safety | status |
|---|---|---|---|---|
| arch-engine-realtime | src/engine/, src/engine/sync/ | rt-audio | hard | authored |
| arch-effects-chain | src/engine/effects/, src/effects/ | rt-audio + gui | hard | authored |
| arch-mixer-decks | src/mixer/ | rt-audio + gui | hard | authored |
| arch-vinylcontrol | src/vinylcontrol/ | rt-audio | hard | authored |
| arch-audio-io | src/soundio/ | rt-audio origin | hard | authored |
| arch-sources-decode | src/sources/, src/encoder/ | worker | none | authored |
| arch-control-messaging | src/control/ | any | soft | authored |
| arch-controllers-mapping | src/controllers/ | worker + gui | none | authored |
| arch-library-db | src/library/, src/database/ | gui + worker | none | authored |
| arch-track-model | src/track/ | any (read) | soft | authored |
| arch-analyzer | src/analyzer/ | worker | none | authored |
| arch-musicbrainz | src/musicbrainz/, src/network/ | worker | none | authored |
| arch-waveform-render | src/waveform/ | gpu-render | soft | authored |
| arch-rendergraph | src/rendergraph/, src/shaders/ | gpu-render | none | authored |
| arch-skin-widgets | src/skin/, src/widget/ | gui | none | authored |
| arch-qml-ui | src/qml/, res/qml/ | gui | none | authored |
<!-- ddd-roster:end -->

Cross-cutting (not contexts, see `ddd/cross-cutting.md`): broadcast+recording, preferences,
util+coreservices (the composition root).

## Domain charters (per-folder AGENTS.md)

Priority order (risk × agent-touch): engine → control → soundio → mixer → effects → library →
controllers → waveform → track, then the second wave. Each charter cites the root `/AGENTS.md` hard
rules and its DDD card; it never restates them.

| src folder | charter | status |
|---|---|---|
| src/engine/ | src/engine/AGENTS.md | authored |
| src/control/ | src/control/AGENTS.md | authored |
| src/soundio/ | src/soundio/AGENTS.md | authored |
| src/mixer/ | src/mixer/AGENTS.md | authored |
| … | (per priority order) | planned |

## The RT signal chain (one-screen mental model)

```
sources/decode ──> engine (mix/scale/effects) ──> soundio (SoundManager callback) ──> device
                        │  ▲                                   (RT callback ORIGIN)
   control ────────────┘  │ (lock-free tap)
   (any thread, the bus)  └──> waveform/rendergraph (gpu, display-clock driven)
```
The audio callback originates in `soundio` and drives `engine`; `control` crosses every context as the
string-keyed bus; `waveform` taps engine state lock-free and renders on the display clock, never the
audio clock.

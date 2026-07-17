---
id: migx-ddd-buildout-plan
type: plan
title: "Architecture knowledge layer — DDD cards + per-domain AGENTS.md buildout plan"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/AGENTS.md
  - AGENTS.md
---

# Architecture Knowledge Layer — Buildout Plan

Make Migx legible to any codegen agent (Claude Code, Codex, Grok) via (a) a DDD bounded-context map
under `kanban/architecture/ddd/` and (b) a per-domain `AGENTS.md` inside each `src/<domain>/`.
Principle: **pointers, never copies** — a card/charter names relationships and invariants; what the
code *is* stays in the code (MG-3). Every doc ≤~120 lines.

**The one big adaptation:** the reference keyed cards on a distributed edge/cloud axis. Migx's real
dominant invariant is the **real-time boundary** — RT-audio thread vs GUI vs GPU-render vs worker. So
the card schema is keyed on `thread_domain` + `rt_safety`, not deployment locus.

## DDD-card format (lean)

Cards: `kanban/architecture/ddd/bounded-contexts/<id>.md`; seams:
`kanban/architecture/ddd/boundaries/<slug>.md`; template `bounded-contexts/_TEMPLATE.md`.
IDs: `arch-<domain>-<facet>`.

Frontmatter (de-overloaded — each field answers one question):
`id · type: ddd-bounded-context · title · owns: [src paths] · exclude: [carved-out paths] ·
thread_domain: rt-audio|gui|gpu-render|worker|any · rt_safety: hard|soft|none ·
subdomain: core|supporting|generic · upstream: [ids] · downstream: [ids] ·
maturity: scaffold|developing|operational|hardened · fork_delta: upstream-tracking|migx-divergent|migx-new ·
agents_md: src/<domain>/AGENTS.md · last_audited`.
Body (~5 sections): one-para responsibility+edge · Key aggregates/classes (table, ≤10) · **Invariants
an agent MUST respect** (RT boundary first) · Ubiquitous language (terms precise *inside* this context) ·
Boundaries (edges by id) · Key patterns cited (P-NN, root AGENTS.md) — never restated.

`fork_delta` is Migx-native and valuable: how far this context has diverged from upstream Mixxx.

## The 16 bounded contexts (grouped by thread_domain)

**RT-audio (`rt_safety: hard` — highest risk):**
1. `arch-engine-realtime` — src/engine/ (EngineMixer, EngineBuffer, channels/, bufferscalers/, sync/, filters/, cachingreader/)
2. `arch-effects-chain` — src/engine/effects/, src/effects/ (EffectsManager, backends/, chains/)
3. `arch-mixer-decks` — src/mixer/ (PlayerManager, Deck, Sampler, PreviewDeck, Microphone) — straddles RT+GUI
4. `arch-vinylcontrol` — src/vinylcontrol/ (timecode signal processing)

**Audio-IO:**
5. `arch-audio-io` — src/soundio/ (SoundManager, SoundDevice*, portaudio/pipewire/network) — the callback origin
6. `arch-sources-decode` — src/sources/ + src/encoder/ (SoundSource*, decoders/encoders) — worker

**Control/messaging:**
7. `arch-control-messaging` — src/control/ (ControlObject, ControlProxy, ControlValue) — the cross-thread seam; `thread_domain: any`

**Controllers:**
8. `arch-controllers-mapping` — src/controllers/ (midi/, hid/, bulk/, scripting/ QJSEngine)

**Library/data:**
9. `arch-library-db` — src/library/ + src/database/ (TrackCollection, DAOs, LibraryTableModel)
10. `arch-track-model` — src/track/ (Track, beats, cues, keys) — read on RT + GUI (careful)
11. `arch-analyzer` — src/analyzer/ (beat/key/gain analysis) — worker
12. `arch-musicbrainz` — src/musicbrainz/ + src/network/

**Render/UI:**
13. `arch-waveform-render` — src/waveform/ (renderers/, WaveformWidgetFactory) — GPU + RT hand-off
14. `arch-rendergraph` — src/rendergraph/ + src/shaders/ — GPU scene graph (likely `migx-divergent`; Metal north-star lives here)
15. `arch-skin-widgets` — src/skin/ + src/widget/ (legacy QWidget UI)
16. `arch-qml-ui` — src/qml/ + res/qml/ (new Qt Quick UI; likely `migx-new`)

**Cross-cutting notes (not contexts):** `arch-broadcast-recording` (src/broadcast+recording), `arch-preferences` (src/preferences), `arch-util`+`arch-coreservices` (src/util, coreservices.cpp — the composition root). Documented in `ddd/cross-cutting.md`.

## Per-domain AGENTS.md

At `src/<domain>/AGENTS.md`, ≤~80 lines, **tool-agnostic** (no CC-specific wording). The card is the
*map*; the charter is the *operational contract*. Sections: header (→ DDD card, → root /AGENTS.md,
→ /CONTRIBUTING.md) · Purpose · Key files (≤10) · **Invariants you MUST respect** (RT thread first) ·
Build/test entry points (real cmake/ctest commands) · Forbidden edits · Cross-references. Cites root
/AGENTS.md hard rules; never restates them.

**Priority order** (risk × agent-touch-frequency):
1. src/engine/ 2. src/control/ 3. src/soundio/ 4. src/mixer/ 5. src/effects/ 6. src/library/
7. src/controllers/ 8. src/waveform/ 9. src/track/ — then second wave: qml, rendergraph, analyzer,
sources, preferences, skin+widget, vinylcontrol.

## The index & discovery

- `kanban/architecture/README.md` — lean orientation: the 16-context roster table (`id | title | src
  paths | thread_domain | maturity | fork_delta`) + a one-screen context-map diagram (RT chain
  sources→engine→soundio; the control seam; the render tap engine→waveform). **Generated** from card
  frontmatter, not hand-maintained.
- `kanban/architecture/ddd/context-map.md` — the relationship narrative (the *why* of each seam).
- Root `/AGENTS.md` gains a "Domain charters" pointer list (src/engine/AGENTS.md, …) + a pointer to
  `kanban/architecture/README.md`. Bidirectional: card `agents_md:` ↔ charter header.

## Minimal lint (3 scripts, not the reference's fleet) — Phase 3

- `verify-agents-md-present.py` — every context's `agents_md:` file exists.
- `verify-owns-paths-exist.py` — every `owns:`/`exclude:` path exists; every src/ folder claimed by
  exactly one context (coverage + no-overlap).
- `verify-index-fresh.py` — generated roster matches the cards. Plus `ddd/gen-index.py` (~50 lines).

## Authoring order
`_TEMPLATE.md` + `README.md` skeleton → cards for the RT core (engine, control, soundio, mixer) +
their seam docs (control-to-engine, engine-to-soundio, engine-to-waveform) → `src/engine|control|soundio/AGENTS.md`
→ remaining cards + charters by priority → gen-index + lint (Phase 3).

**CUT from reference** (non-transferable): NATS subject graph, source_domain/runtime_locus/supervision/
instance_scope, sim/live mode-profiles, 4-way authority split, TEC entity model, the 493-script lint
suite + _graph.json compiler + readiness scorecard, deployment/promotion/fleet docs. Migx keeps the
*shape* (one-home cards, frontmatter+why, boundaries, generated index, minimal lint) and swaps the
distributed axis for the RT-thread-safety axis.

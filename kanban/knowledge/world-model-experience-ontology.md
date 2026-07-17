---
id: world-model-experience-ontology
type: knowledge
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
source: >
  oz-platform World-Model prior art:
  kanban/planning/26-03-12-world-model-playbook/ (AGENTS.md; 01-WORLD-MODEL-CORE/01.02-entity-state-space-schema.md,
  01.03-causal-state-graph.md, 01.01-hybrid-usd-lpg-architecture.md; 03-ARCHITECTURE-INTEGRATION/03.02-ssot-filesystem-registry.md;
  00-FOUNDATION/00.04-anti-patterns-vs-patterns.md), kanban/initiatives/initiative-world-model-2026-q1.md,
  kanban/patterns/P-170-one-predictor-per-entity.md, P-48-in-code-agent-knowledge-layer.md, P-142, P-3.
  Migx data model (evidence read directly): src/track/cueinfo.h (CueType enum), src/track/keyutils.h
  (KeyNotation::Lancelot = Camelot, getCompatibleKeys, keyToOpenKeyNumber, shortestStepsToCompatibleKey),
  src/track/track.cpp, src/track/beats.cpp, src/analyzer/ (AnalyzerBeats/Key/Gain/Ebur128/Waveform/Silence — no
  section/energy analyzer), src/track/AGENTS.md.
  Migx docs: kanban/architecture/ddd/bounded-contexts/arch-track-model.md, arch-analyzer.md, arch-library-db.md;
  kanban/knowledge/filesystem-driven-architecture.md (sidecar-as-SSoT, ontology.json home);
  kanban/knowledge/claude-code-capabilities.md; kanban/patterns/P-06, P-16, P-17, P-20;
  kanban/architecture/decisions/ADR-002-hard-fork-no-upstream-merge.md; README.md (AI-DJing thesis).
related: [filesystem-driven-architecture, claude-code-capabilities, arch-track-model, arch-analyzer,
  arch-library-db, arcflow-filesystem-m4]
---

# World-Model experience ontology for Migx (the differentiator)

**Thesis.** A **song** and a **DJ session** are a **flow of experience** — a timeline-based ontology with
a **property graph** of typed edges — that a coding/agent tool (Claude Code, Codex, …) can **read** and,
in a live set, safely **affect**. This makes Migx a **Claude-Code-compatible DJ instrument**: the agent is
an experience-design co-pilot in the loop, not a plugin behind an API. This note designs that ontology,
grounds every field in what Migx actually computes today, names the new analysis that must be built, and
recommends the flagship initiative + first spike.

The ontology's on-disk home is already decided: it lives in **`ontology.json` inside each track's
`Song.migx/` sidecar** (`filesystem-driven-architecture.md` §3a), with the SQLite DB as a **rebuildable
index**. This note builds *on* that decision, it does not relitigate it.

---

## 1. The transferable World-Model technique (distilled from oz-platform)

oz-platform's World-Model Playbook (`26-03-12-world-model-playbook/`) models multi-camera sensor systems.
**Drop the robotics/sensor domain wholesale** — geometry (`position[3]`, PTZ, FOV), OpenUSD, POMDP camera
control, NATS. What transfers is the **modelling technique**, which is domain-neutral by its own first
principle (00.04 #2: "`focus_entity` not `ball`"). Nine techniques carry over:

| # | oz technique (source) | What it is | Migx translation |
|---|---|---|---|
| T1 | **Three-layer hybrid stack** (01.01) | physical geometry (USD) → semantic/causal graph (LPG) → declarative behaviour overlay (Playbook JSON) | **audio/DSP layer** (samples, beatgrid, waveform) → **experience graph** (sections, energy, harmonic edges) → **mixing-skill overlay** (an agent's transition plan / co-pilot intent) |
| T2 | **Typed entity-state-space with stable IDs** (01.02) | one canonical data model, shared contract across all layers; every node has a stable `id`, a `type` enum, timestamps | one `ontology.json` schema shared by analyzer (writer), graph index (deriver), agent (reader); stable IDs per song/section/cue |
| T3 | **`_domain_extensions` map** (00.04 #2, CACAO) | core stays neutral; domain data in an extension map the loader ignores if unknown | keep a neutral core (`section`, `energy`, `marker`) + a `_ext` map for genre-specific or tool-specific data — forward-compatible without schema breaks |
| T4 | **State-space + transition function** (01.02 §State Space) | `S(t) = (E, C, I, P)`; approximate `P(S'|S,a)` — given state + action, predict next state; a tick loop observe→evaluate→resolve→assign→execute→log | a **session** is a trajectory; the agent reasons `P(next-track-experience \| current-deck-state, transition)` — "if I mix into X here, what happens to the energy/harmony?" |
| T5 | **Typed causal edges** (01.03) | first-class `:CAUSES`, `:TRIGGERS`, `:AFFORDS`, `:SUPERSEDES`, `:RESOLVES_TO` — the graph models **why**, not just what | Migx's mixing edges (`mixes-into`, `harmonically-compatible`, `contrasts`, …, §4). **Affordances** (Gibson) map cleanly: "what can I do with this track *right now*" = `affords: mixable-out-of-drop`, `affords: harmonic-lift-to-9A` |
| T6 | **Fact classification: observed / inferred / predicted + confidence** (01.03, 00.04 #9) | every assertion is explicitly one of the three, never silently mixed; carries `confidence` | an edge is **observed** (a mix you actually performed, logged), **inferred** (harmonic compatibility computed from keys), or **predicted** (agent-proposed next track). Confidence gates the co-pilot's suggestions |
| T7 | **Intent lifecycle** (01.02, 00.04) | `proposed → active → expired / superseded`, TTL-bounded; capability-based assignment, not device IDs | the co-pilot's suggestions are **intents** with the same lifecycle (§5); it proposes a transition, the human/engine accepts (`active`), a newer suggestion `supersedes`. Maps directly onto ControlObject single-writer |
| T8 | **Single authority per fact / one-predictor-per-entity** (P-170, SSoT 03.02, 00.04 #4) | exactly one component predicts a given entity's future; everyone else **reads** it, never re-derives — a second predictor "drifts silently with no error signal" | the **engine** is the sole authority for playhead/phase/beatgrid; the agent **reads** it and must never run a parallel playhead estimate that drifts. Matches Migx `P-06`/`P-07` exactly |
| T9 | **Filesystem-as-DB + registry, greppable, git-native** (03.02, 00.04 #4) | every fact in one authoritative file; `index.json` registry; agent reads/writes files naturally | already Migx's chosen substrate (`filesystem-driven-architecture.md`): `ontology.json` per track, a derived graph index, `git` history over a crate |

Two more cross-cutting practices transfer: **bitemporal time** (01.03 — *belief time* "when it was true in
the mix" vs *assertion time* "when the agent recorded it" — lets you replay a set), and **`_llm_guidance`
annotations** (00.04 — human-readable hints on complex nodes so an agent needs no external doc), which is
the same instinct as oz's `P-48` in-code knowledge layer and Migx's per-domain `AGENTS.md`.

**What we deliberately do NOT clone:** the physical/geometry layer, POMDP/reward machinery, NATS IPC,
capability-vs-camera-id indirection (Migx has decks, not a camera array), and the USD payload format. The
keepers are: *typed timeline ontology, typed causal/experiential edges, fact classification, single-writer
/ single-predictor, intent lifecycle, filesystem-SSoT.*

---

## 2. SONG ontology — a song as an experience timeline

A song is a **timeline** annotated with **sections**, an **energy curve**, a **harmonic identity**, a
**phrase/bar grid**, and **cues as experiential markers** — grounded in the `Track` aggregate
(`arch-track-model`: `Track`, `Beats`, `Cue`, `Keys`, `ReplayGain`).

### 2a. Have-today vs must-build (evidence-grounded)

| Ontology field | Migx today | Evidence | Gap |
|---|---|---|---|
| **Beatgrid / tempo** | ✅ `AnalyzerBeats` → `Beats`/`BeatsPointer`, `Bpm` | `src/analyzer/analyzerbeats.cpp`, `src/track/beats.cpp` | none |
| **Phrase / bar structure** | ⚠️ *derivable* from `Beats` (group beats → bars of 4 → 8/16/32-bar phrases); not materialised | `Beats` gives beat positions | **BUILD (cheap)** — a pure derivation, no DSP |
| **Key + Camelot wheel** | ✅ `AnalyzerKey` → `Keys` (`ChromaticKey`, 24 keys); **Camelot already supported** as `KeyNotation::Lancelot`; harmonic helpers exist | `src/analyzer/analyzerkey.cpp`; `src/track/keyutils.h`: `keyToOpenKeyNumber`, `getCompatibleKeys`, `shortestStepsToCompatibleKey`, `keyToCircleOfFifthsOrder` | none for a single global key |
| **Loudness (integrated)** | ✅ `AnalyzerGain` / `AnalyzerEbur128` → `ReplayGain` | `src/analyzer/analyzergain.cpp`, `analyzerebur128.cpp` | none — but this is **one integrated number, not a curve** |
| **Energy curve (time-varying)** | ❌ nothing computes per-phrase energy over time | no `AnalyzerEnergy` under `src/analyzer/` (grep negative) | **BUILD — `AnalyzerEnergy`** (RMS / spectral-flux / onset-density per phrase) |
| **Sections (intro/build/drop/breakdown/outro)** | ❌ no structural segmentation | no `AnalyzerStructure` (grep negative) | **BUILD — `AnalyzerStructure`** |
| **Intro / Outro markers** | ⚠️ partial: `CueType::Intro`, `CueType::Outro`, `N60dBSound` audible-range cues exist | `src/track/cueinfo.h:18-20`; set from `AnalyzerSilence` | reuse as section anchors; enrich |
| **Cues (hotcue/loop/main/jump)** | ✅ `Cue` with typed `CueType{HotCue,MainCue,Loop,Jump,Intro,Outro,N60dBSound}` | `src/track/cueinfo.h:11-22`, `src/track/cue.cpp` | none — reinterpret as experiential markers |
| **Mood / genre / valence** | ❌ genre is a free-text tag only; no mood/valence | `TrackRecord` metadata | **BUILD or import** (tag-derived v1; embedding later) |
| **Harmonic journey (key changes over time)** | ❌ Migx stores one global key | `Keys` is global | **BUILD (optional/late)** — most DJ tracks are single-key; global key + Camelot suffices for v1 |

**Net:** the harmonic and beat layers are *done and rich* (Camelot + compatible-key math already ship).
The **one real DSP gap is time-varying structure + energy** — `AnalyzerStructure` and `AnalyzerEnergy`, two
new worker-thread passes under `src/analyzer/`, following `arch-analyzer` invariants (worker-only `P-17`,
results into the canonical `Track` `P-07`, fail-loud `AP-16`, result-is-a-contract `AP-02`). Phrase/bar
structure is a *free derivation* from `Beats`. Sections can be **hand-authored** in the sidecar to unblock
the ontology/agent work before the analyzer lands (the sidecar is agent-writable — that is the point).

### 2b. `ontology.json` — the Song schema (in `Song.migx/`)

Lives next to `track.toml` in the sidecar (`filesystem-driven-architecture.md` §3a). `track.toml` holds the
raw SSoT facts (bpm/key/gain/beatgrid/cues); `ontology.json` holds the **experience interpretation** derived
from them. Positions are in **beats** (stable under tempo edits; resolvable to seconds via `Beats`).

```jsonc
{
  "schema": "migx.song-ontology/1",
  "id": "song--0b3f…",                 // stable; T2
  "ref": "../track.toml",              // SSoT facts live there; T9 cross-ref-by-path
  "duration_beats": 512,
  "bpm": 126.0,
  "key": { "chromatic": "Am", "camelot": "8A", "open_key": "1m" },  // KeyUtils::Lancelot
  "phrases": { "beats_per_bar": 4, "bars_per_phrase": 8 },          // derived from Beats (T2, cheap-build)

  "sections": [                         // BUILD: AnalyzerStructure (or hand-authored)
    { "id": "sec--intro",     "type": "intro",     "start_beat": 0,   "end_beat": 64,  "energy": 0.25,
      "mixable": true,  "_llm_guidance": "32-bar beat-only intro — safe to mix over" },
    { "id": "sec--build",     "type": "build",     "start_beat": 64,  "end_beat": 128, "energy": 0.55 },
    { "id": "sec--drop",      "type": "drop",      "start_beat": 128, "end_beat": 256, "energy": 0.95,
      "_llm_guidance": "main drop — do NOT mix a new element in here" },
    { "id": "sec--breakdown", "type": "breakdown", "start_beat": 256, "end_beat": 320, "energy": 0.40 },
    { "id": "sec--outro",     "type": "outro",     "start_beat": 448, "end_beat": 512, "energy": 0.20,
      "mixable": true }
  ],

  "energy_curve": {                     // BUILD: AnalyzerEnergy — one value per phrase
    "unit": "phrase", "method": "rms+onset-density",
    "samples": [0.22, 0.28, 0.5, 0.6, 0.95, 0.93, …]     // fact_type: observed (measured DSP)
  },

  "markers": [                          // reinterpret existing Cue rows as experiential markers
    { "id": "cue--mix-in",  "beat": 0,   "role": "mix-in",   "from_cue": "Intro" },   // CueType::Intro
    { "id": "cue--drop",    "beat": 128, "role": "impact",   "from_cue": "HotCue:1" },
    { "id": "cue--mix-out", "beat": 448, "role": "mix-out",  "from_cue": "Outro" }     // CueType::Outro
  ],

  "mood": { "labels": ["hypnotic", "driving"], "valence": 0.4, "fact_type": "inferred", "confidence": 0.6 },
  "genre": "melodic techno",
  "_ext": { }                           // T3 domain/tool extension map
}
```

Every energy/section value carries an implicit or explicit **`fact_type`** (T6): DSP-measured = `observed`,
tag/heuristic = `inferred`, agent-proposed = `predicted`. The agent must not treat an inferred mood as
ground truth.

---

## 3. SESSION / PLAYLIST ontology — the flow of experience across songs

A session is a **trajectory over songs**: an ordered walk that shapes an **energy arc**, respects
**harmonic continuity**, and strings **transitions** into a **narrative**. It is oz's `S(t)` state trajectory
(T4) applied to a set. Stored as a session sidecar `sets/<name>.migx/session.json` (its own registry entry).

```jsonc
{
  "schema": "migx.session-ontology/1",
  "id": "session--2026-07-17-warmup",
  "narrative": "slow hypnotic warm-up → peak-time drive → melodic cool-down",  // _llm_guidance for the whole set
  "energy_arc": { "shape": "rise-plateau-release", "target_peak_at": 0.7 },     // fraction through the set
  "tracks": [                                                                    // ordered = the `follows` chain
    { "seq": 0, "song": "song--0b3f…", "played_at": null },
    { "seq": 1, "song": "song--a91c…" },
    { "seq": 2, "song": "song--77de…" }
  ],
  "transitions": [                                                               // one per adjacent pair
    { "id": "tx--0-1", "from": "song--0b3f…", "to": "song--a91c…",
      "type": "harmonic-blend",                // beat-match | harmonic-blend | echo-out | cut | loop-roll | filter-fade
      "from_marker": "cue--mix-out", "to_marker": "cue--mix-in",
      "bars": 16, "energy_delta": +0.15, "camelot_move": "8A→9A",   // energy-boost mix
      "fact_type": "predicted", "confidence": 0.82,                 // proposed by the co-pilot; becomes observed when performed
      "_llm_guidance": "lift a semitone up the wheel on the outro→intro overlap" }
  ],
  "crowd_response": [                          // OPTIONAL, late — observed feedback loop (T4 reward signal)
    { "at_seq": 1, "signal": "peak", "source": "operator-tag" }
  ]
}
```

**Session concepts and where each is grounded:**
- **Energy arc** — the target curve the set should trace; each transition's `energy_delta` steps along it.
  Buildable *today* from per-track integrated `ReplayGain` as a coarse proxy; sharpens once `AnalyzerEnergy`
  (§2a) gives per-section energy so the arc reasons about *which part* of each track lands where.
- **Harmonic mixing** — computed *free* from `KeyUtils::getCompatibleKeys` / `shortestStepsToCompatibleKey`
  over each pair's Camelot key: same key, ±1 on the wheel (energy up/down), or relative major/minor.
- **Transition types** — a small closed vocabulary anchored to the two songs' `markers` (mix-out of A ↔
  mix-in of B) and a bar count; validated against phrase structure (§2) so the overlap is phrase-aligned.
- **Narrative** — the `_llm_guidance` the agent reasons over; the human's intent for the set.
- **Crowd response** — optional late feedback (operator tag or, later, a signal), the "reward" that closes
  oz's observe→log flywheel (T4) for learning better sets.

---

## 4. The property graph — nodes, typed edges, storage, queries

The ontology *is* a property graph; §2–3 are its serialisation. Making the graph explicit is what lets an
agent **plan a set as experience-design** rather than sort a list.

### 4a. Node types
`Song`, `Section`, `Phrase` (optional), `Cue`/`Marker`, `Transition`, `Mood`, `Genre`, `Session`, and (live
only) `DeckState`. Each has a stable `id` and `type` (T2). `Section`/`Cue`/`Mood` are *contained* by a
`Song`; `Transition` connects two `Song`s; `Session` contains an ordered `Song` list.

### 4b. Edge types (typed, directional, fact-classified — T5/T6)

| Edge | From → To | Meaning | Source / how derived |
|---|---|---|---|
| `has-section` | Song → Section | structural containment | `AnalyzerStructure` (BUILD) |
| `has-marker` | Song → Cue | experiential marker | existing `Cue` rows (`cueinfo.h`) |
| `exhibits-mood` | Song → Mood | affective identity | inferred (tags/embedding) |
| `mixes-into` | Song → Song | a transition (proposed or performed) | `predicted` by co-pilot → `observed` when played; carries `Transition` props |
| `harmonically-compatible` | Song ↔ Song | Camelot-compatible keys | **inferred, computed free** from `KeyUtils::getCompatibleKeys` |
| `same-energy` / `next-energy` | Song → Song | energy adjacency (±ε / +step) | inferred from `energy_curve` / `ReplayGain` |
| `follows` | Song → Song | session ordering (curated) | `observed` from `session.json` track order |
| `contrasts` | Song → Song | deliberate energy/mood break ("reset") | inferred (large energy_delta, mood flip) |
| `affords` | Song/Section → Affordance | "what can I do here now" (Gibson, T5) | inferred, e.g. `affords: mix-out@outro`, `affords: harmonic-lift-to-9A` |
| `sampled-from` | Song → Song | shared motif/sample | future; hand-authored or audio-fingerprint |
| `transition-at` | Transition → (Section, Section) | anchors a mix to outro-of-A ↔ intro-of-B | derived from `markers` + phrase grid |

### 4c. Storage — sidecar SSoT + a derived, rebuildable graph index

Following oz's "materialise the playbook into the LPG" (01.03 graph-loading) and P-142 (offline serialisation
of a live graph), split **authoritative** from **derived**:

- **Authoritative (in sidecars, SSoT):** *intrinsic* edges — `has-section`, `has-marker`, `exhibits-mood`
  (in `ontology.json`), and *curated/observed* cross-song edges — `follows`, performed `mixes-into`
  (in `session.json`). One writer each (`P-06`); one canonical home (`P-07`).
- **Derived (rebuildable index, NOT SSoT):** the *computed* edges — `harmonically-compatible`,
  `same/next-energy`, `contrasts`, `affords` — are **materialised by scanning all sidecars** into a graph
  index. This is the DB's job in `filesystem-driven-architecture.md` (DB-as-index): a scan builds an
  in-memory / SQLite-backed adjacency so "what mixes well next" is one indexed query, not a 10k-file grep.
  Delete it, rescan the `.migx/` tree, and it rebuilds — the graph index is disposable, exactly as the DB is.

An `index.json` registry (oz 03.02) maps `song-id → sidecar path` and `session-id → session path` so the
graph loader and the agent can resolve nodes without walking the whole tree.

### 4d. Queries it enables
- **"What mixes well after this at this energy?"** → songs with a `harmonically-compatible` edge to the
  current key **AND** `next-energy` within the arc's target step **AND** a phrase-compatible `mix-in` marker.
- **"Find a breakdown→drop lift into 9A at 124–128 BPM"** → filter by key-move + BPM window + section types.
- **"Build a 60-min chill→peak→release set from this crate"** → **path-find** over the graph: a walk whose
  `energy_delta`s trace the `energy_arc`, every hop harmonically legal, minimising harsh `contrasts`.
- **"Why does this transition work?"** → traverse the causal edges (`harmonically-compatible` +
  `next-energy` + `transition-at` phrase alignment) and surface the `_llm_guidance` — an *explainable* mix.

---

## 5. The agent layer — AGENTS.md descriptors + Skills, and the safe live read/write path

This is the "Claude-Code-compatible" surface: the same `AGENTS.md`-per-domain + `pat-*`-skill pattern Migx
already runs for its C++ (`src/track/AGENTS.md`), applied to songs and sessions.

### 5a. Descriptors (AGENTS.md-inspired — the human/agent-facing charter)
- **Per song** — an optional `Song.migx/SONG.md`: a thin, greppable charter that *cites* `ontology.json`
  (does not restate it), mirroring how `src/track/AGENTS.md` cites its DDD card. It says, in prose: the
  track's arc, the safe mix-in/mix-out windows, "don't mix into the drop," harmonic neighbours. The machine
  reads `ontology.json`; a human/agent skims `SONG.md`. (`_llm_guidance` fields cover the inline case.)
- **Per session** — `sets/<name>.migx/SESSION.md`: the set's narrative, energy-arc intent, and house rules
  ("keep it under 128 BPM until the peak"). This is the set's `AGENTS.md`.

### 5b. Skills (Claude-Code-Skills-inspired — what the agent *invokes*)
Under `.claude/skills/`, auto-loaded by `description` like the `pat-*` skills:
- **`dj-harmonic-mix`** — given the current key + energy, return Camelot-compatible next tracks (wraps
  `KeyUtils::getCompatibleKeys` semantics + the energy edge).
- **`dj-plan-transition`** — given two songs' `ontology.json`, propose a `Transition` (type, bar count, which
  markers to align, energy_delta, Camelot move) — the §4d "why it works" explanation.
- **`dj-build-arc`** — path-find a set over a crate to hit a target `energy_arc`.
- **`dj-read-session`** — read the live session mirror (§5c) and reason about the *next* move in context.

### 5c. Live read/write — the co-pilot, honouring house physics
The killer use case: Claude Code running *beside* a live set, reading it and affecting it. Split it exactly
along oz's **observer vs production** sensor roles (01.02) and Migx's RT invariants:

**READ path — a filesystem "session mirror" (observer).** Migx exports live state — active deck, playhead
position (in beats), loaded tracks, cues, upcoming crate, the current graph neighbourhood — to a
**read-only mirror on disk** (or an IPC snapshot), refreshed off the RT thread on the GUI/worker cadence.
The agent `grep`s/`cat`s this the way it reads any sidecar (`filesystem-driven-architecture.md` §1; the model
already speaks Unix). **Crucially, the agent READS the engine's playhead/phase — it never runs its own
playhead predictor** (T8 / P-170: one predictor per entity; the engine is the sole authority, a second
estimate drifts silently). The mirror is a *projection* of engine state, never a control input.

**WRITE path — an intent inbox reconciled through ControlObject (production).** The agent never writes a
file the engine reads on the RT thread, and never touches a `QObject` from off its thread (`P-20`). Instead
it drops a **proposed intent** — "set hot-cue 2 at beat 128," "queue song-77de next," "start the mix-out at
bar 449" — into an **intent inbox** (a file/IPC queue) with the oz **intent lifecycle** (T7:
`proposed → active → expired / superseded`, TTL-bounded). A Migx-side **reconciler on the GUI/worker thread**
validates the intent (schema + house-physics: is it phrase-aligned? harmonically legal?) and applies it as
the **single authoritative writer** to the relevant `[Group],key` **ControlObject** (`P-06`) — which is the
*only* path that reaches the RT engine (`P-16` lock-free hand-off, `P-20` affinity). The human can gate
`proposed → active` (accept the suggestion) or let low-risk intents auto-apply under a confidence threshold
(T6). Every intent is a diffable file → `git`-auditable co-pilot actions (`filesystem-driven-architecture.md`
§1).

```
 live set  ─(off-RT export)→  session-mirror/   ──read──►  Claude Code + dj-* skills
   ▲                                                             │ proposes
   │ ControlObject (single writer, P-06/P-16/P-20)               ▼
 Migx reconciler (GUI/worker) ◄── validate + lifecycle ──── intent-inbox/  (proposed→active→…)
```

This is the concrete differentiator: an agent co-pilot **in** the session, bounded by the same house physics
as any Migx code — never on the RT thread, one writer per control, the engine the sole authority for phase.

---

## 6. Feasibility + composition with the harness

**It composes natively with the harness (everything-is-code, MG-2).** `ontology.json`, `SONG.md`,
`session.json`, `dj-*` skills, and the intent inbox are all **greppable files** — the ontology is versioned,
diffable, agent-readable, tool-agnostic (Claude Code / Codex / Grok read the same tree), exactly as the code
harness is. It sits directly on the already-decided sidecar substrate: `ontology.json` is the named sibling
of `track.toml` (`filesystem-driven-architecture.md` §3a) and rides the same perf layer
(`arcflow-filesystem-m4.md`: mmap + page cache for many-small-file reads).

**Dependencies (honest):**
1. **The sidecar spike** (`filesystem-driven-architecture.md` §6, prefix `FSL`) must land first — `FSL-04`
   explicitly hands off to this work. The ontology needs a real sidecar to live in.
2. **New analysis** — `AnalyzerStructure` (sections) and `AnalyzerEnergy` (energy curve) are the one genuine
   build item (§2a). Worker-thread, `rt_safety: none`, following `arch-analyzer` invariants (`P-17`, `P-07`,
   `AP-16`, `AP-02`). Phrase/bar structure is a *free* derivation from `Beats`; harmonic edges are *free*
   from `KeyUtils`. **The harmonic half of the differentiator already ships** (Camelot = `KeyNotation::Lancelot`,
   `getCompatibleKeys`, `shortestStepsToCompatibleKey`) — a major head start.
3. **The live co-pilot** (§5c) needs the session-mirror export + intent-inbox reconciler — a bigger,
   later phase gated on the read path proving out. It reuses existing ControlObject machinery (`P-06`) and
   adds no RT-path risk if built to `P-16`/`P-20`.

**ADR-002 sanctions this.** A hard fork with no upstream merge means adding an agent-native experience
ontology and an intent-inbox to the core is *the* intended divergence, not a cost (`fork_delta` records
heritage only). README already states the thesis: Migx as the AI-DJing instrument where "an AI agent in the
loop of the … flow of experience."

**Risk to watch:** don't let the agent become a second predictor of engine state (T8). The mirror is
read-only; the engine owns phase; the agent proposes, ControlObject disposes.

---

## 7. Recommendation — the flagship initiative + first spike

This is **almost certainly THE Migx differentiator** and warrants a **flagship standing initiative**, not a
one-off. It is the ontology behind every headline claim in the README.

**Proposed initiative:** `initiative-experience-ontology` — the World-Model experience ontology + the
agent co-pilot surface. **Register the 3-letter prefix `EXO`** (EXperience Ontology). *(Alt: `WLD`; `EXO`
preferred — it names the differentiator, whereas `WLD` reads as generic and collides conceptually with
oz's world-model work.)*

**First spike dossier (prefix `EXO`, research + spike — no production RT code):** model **one real song**
and a **3-track session**, and prove an agent reasons a transition from files alone.

- **EXO-01 — Schema.** Define `migx.song-ontology/1` (§2b) + `migx.session-ontology/1` (§3) as JSON Schemas
  in-repo. Hand-author `ontology.json` for one real track (sections + energy curve by ear) to validate the
  shape before any analyzer exists — proving the sidecar is genuinely agent-authorable.
- **EXO-02 — Minimal analysis / derivation.** Derive phrase/bar from `Beats` (free); populate Camelot from
  `KeyUtils` (free); stub `AnalyzerEnergy`/`AnalyzerStructure` output (or hand-annotate) for 3 tracks. Defer
  full DSP; the goal is a populated graph, not production analyzers.
- **EXO-03 — Derived graph index.** Scan the 3 sidecars, compute `harmonically-compatible` + `next-energy`
  edges (`KeyUtils` + energy curve), materialise a query index; answer "what mixes well after track 1 at
  this energy?" (§4d).
- **EXO-04 — Agent reasons a transition (the acceptance proof).** Ship `dj-plan-transition` + `SONG.md`
  descriptors; have Claude Code, reading *only* the sidecars, propose a phrase-aligned, harmonically-legal
  transition **with an explanation** (key move + energy step + which markers to align). Independent
  evaluator checks the proposal against the ground-truth ontology (generator ≠ evaluator).
- **Deferred to a follow-on dossier (EXO wave 2):** the live session-mirror + intent-inbox co-pilot (§5c),
  and the real `AnalyzerStructure`/`AnalyzerEnergy` passes, once the offline read path pays off.

Keep it research + spike until EXO-04 proves an agent reasons a transition from the sidecars; promote to the
standing initiative on that evidence. Sequence it **after / with `FSL`** (the sidecar spike it depends on).

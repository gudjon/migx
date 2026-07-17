---
id: signal-2026-07-18-experience-ontology-flow-songs-relations
type: signal-brief
from: grok-signal
date: "2026-07-18"
relevance: actionable
topics: [exo, ontology, flow, session, song, co-pilot, layer-b]
mapped_to:
  - initiative-experience-ontology
  - PS-EXO-01
  - world-model-experience-ontology
  - ADR-005
  - Strategy-Current P3
  - FSL
sources:
  - kanban/knowledge/world-model-experience-ontology.md
  - kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/
  - kanban/initiatives/initiative-experience-ontology.md
  - kanban/Strategy-Current.md
  - results/TRANSITION-PROOF.md + COPILOT-WHY-NEXT.md (P-08 PASS)
---

# Research map — EXO: songs, flow, and relations

Field-internal research (repo SSoT + prior oz World-Model technique). No `src/**` edits.

## One sentence
A **song** is a timeline of experience; a **session** is a **flow** (trajectory) over songs; **typed
edges** are the relations an agent plans with — stored as greppable JSON, never as RT state.

## Relation diagram (product)

```text
                    LAYER C  Intelligence (rank, plan, explain)
                              │ reads ontology + session graph
                    LAYER B  Agent seams  ←── EXO lives here
                              │ intents (proposed→active)
                    LAYER A  Instrument (engine, decks, CO)
                              │ sole authority: playhead/phase (P-06/P-07)
                              ▼
┌──────────── Song.migx / fixtures ────────────┐
│  track facts (bpm/key/cues)  │  ontology.json │
│  (SSoT numbers)              │  (experience)  │
└───────────────┬──────────────────────────────┘
                │ has-section / has-marker / energy
                ▼
┌──────────── Session (flow) ──────────────────┐
│  order[]  ·  edges[]  ·  policy  ·  prep     │
│  follows · next-energy · harmonic · sequence │
└──────────────────────────────────────────────┘
```

## Song relations (within one track)

| Concept | Role in flow | Status in Migx |
|---|---|---|
| **sections** intro→build→drop→breakdown→outro | Narrative beats of the song | Hand-authored fixtures; **AnalyzerStructure** still BUILD |
| **energy / energy_curve** | Intensity along the timeline | Hand-authored stub; **AnalyzerEnergy** still BUILD |
| **key / Camelot** | Harmonic identity | **Shipped** (`KeyUtils` Lancelot + compatible keys) |
| **phrases** | Bar/phrase grid for legal overlaps | Derivable from Beats (cheap) |
| **markers/cues** | mix-in, mix-out, impact | Cue types exist; ontology reinterprets as experience |
| **_llm_guidance** | Agent-facing prose on a node | In fixtures |
| **source / playback** | local vs Spotify rights | Hybrid policy: multi-deck only when allowed |

**Song is not a row in a crate list** — it is a **mini world-model** an agent can query offline.

## Session = flow of experience (across songs)

| Concept | Meaning | Fixture example |
|---|---|---|
| **order** | Curated walk (`follows`) | hybrid_prep: 01→02→spotify→03 |
| **energy_arc / next-energy** | Set climbs then releases | 01 low → 02 peak → 03 cool |
| **harmonically-compatible** | Camelot-legal hop | 8A→9A proof (P-08 PASS) |
| **planned-transition** | Human/agent plan edge | cool-down after peak |
| **sequence-only** | Identity + prep **without** dual-stream mix | local→Spotify URI rows |
| **prep** | Session-local cues/notes/roles | opener / peak / bridge / closer |
| **policy** | Product law on the flow | `spotify_multi_deck: false` |

**Flow ≠ playlist sort.** Flow is a **trajectory** with harmonic + energy constraints and explicit
transition semantics (oz T4 state trajectory applied to a set).

## Typed edge vocabulary (the “relations”)

From knowledge + session schema (authoritative vs derived):

| Edge | Kind | Who writes |
|---|---|---|
| `follows` / `order` | curated observed | session author / DJ |
| `harmonically-compatible` | inferred (math) | rebuildable graph index / agent |
| `next-energy` / `same-energy` | inferred | energy curves / ReplayGain proxy |
| `planned-transition` | predicted → observed | co-pilot / human |
| `sequence-only` | policy edge | hybrid prep (Spotify law) |
| `contrasts` | inferred break | large energy/mood flip |
| `affords` | Gibson affordance | e.g. mix-out@outro |
| `mixes-into` | transition event | predicted then observed when played |

**Fact types (T6):** observed / inferred / predicted + confidence — never silently mix ground truth
with agent guess.

## Closed loop (how relations close product value)

```text
Trigger   agent or DJ asks "what next?"
Capture   song ontology + session graph (files / FSL sidecars)
Intel     rank edges: harmonic ∩ energy ∩ policy ∩ order
Adjust    intent proposed → human Ack → single CO writer (never RT invent phase)
Enrich    performed mix becomes observed mixes-into / edge confidence up
```

Proved offline: `TRANSITION-PROOF.md` (01→02) + `COPILOT-WHY-NEXT` (02→spotify sequence-only).

## Relations to other Migx systems

| System | Relationship to EXO |
|---|---|
| **FSL / Song.migx** | Storage home for production ontology (spike still hand-authored fixtures) |
| **Library DB** | Rebuildable **index**, not SSoT of experience |
| **ControlObject** | Live write path only; engine owns phase |
| **QML Co-Pilot chrome** | Layer B UI dogfood of why-next JSON |
| **Spotify path** | URI as **identity** in ontology; sequence-only until partner |
| **Analyzer** | Future writer of observed sections/energy (worker, P-17) |
| **MTL/DSP** | Layer A performance trust so co-pilot never glitches audio |
| **Federation** | Agents hand off EXO research/impl without sharing RT |

## Gaps (honest)

1. Production `AnalyzerStructure` / `AnalyzerEnergy` not built — energy/sections often **inferred/hand**.  
2. Live session-mirror + intent→CO reconciler (co-pilot wave 2) not sealed.  
3. Session edge vocabulary still blurs strict Camelot vs narrative cool-down (noted in P-08 eval).  
4. Graph index (materialised harmonic/energy edges) not a product service yet — fixtures are the proof.  
5. EXO dossier not sealed at `91-LOOP-CLOSURE` despite green proofs.

## What Grok should scout next (field)
- Set-planning / energy-arc UX in modern AI-DJ products (not DRM hacks).  
- Time-varying structure models that could feed AnalyzerStructure later.  
- **Not** dual Spotify multi-deck; **not** RT phase prediction.

## What Claude should implement next (when free)
1. Seal or successor EXO: edge vocab fix from P-08 note.  
2. Intent-inbox → CO single-writer path (Layer B).  
3. FSL hardening so real tracks gain `ontology.json` without hand fixtures.

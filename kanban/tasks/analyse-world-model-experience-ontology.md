---
id: analyse-world-model-experience-ontology
type: task
title: "Analyse a World-Model experience ontology for songs & DJ sessions (Claude-Code-compatible, property-graph + AGENTS.md/Skills-driven)"
status: done
owner: gudjon
priority: high
initiative: initiative-apple-silicon
parent_dossier: ""
related: [analyse-filesystem-driven-architecture, design-md-ui-modernization, learn-oz-audio-engine]
authored_by: claude-code
authored_kind: agent
triggered_by: "gudjon request 2026-07-17 — learn from World Models: song/DJ-session as a flow of experience, timeline-based ontology, property-graph edges, AGENTS.md + Skills-driven, Claude Code compatible as Migx's differentiator"
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  A proposal note (kanban/knowledge/world-model-experience-ontology.md) that:
  - LEARNS from World-Model prior art, incl. /Users/gudjon/code/oz-platform world-model work
    (kanban/planning/26-03-12-world-model-playbook, kanban/initiatives/initiative-world-model-2026-q1,
    and any graph/ontology patterns) — distill the transferable modelling technique, drop robotics domain,
  - defines a SONG ontology: a timeline-based "experience" model — sections (intro/build/drop/breakdown/
    outro), an energy curve, harmonic/key journey (Camelot), phrase/bar structure, cue points as
    experiential markers, mood/genre — grounded in Migx's real data (arch-track-model: Track/Beats/Cues/Keys),
  - defines a SESSION/PLAYLIST ontology: the flow of experience across songs — energy arc, harmonic-mixing
    edges, transition types, narrative/journey, crowd-response,
  - specifies a PROPERTY GRAPH: node types (song, section, cue, transition, mood, session) + edge types
    (mixes-into, harmonically-compatible, same/next-energy, follows, contrasts, sampled-from), and how it's
    stored (relates to the filesystem-driven sidecar question — [[analyse-filesystem-driven-architecture]]),
  - proposes AGENTS.md-inspired + Claude-Code-Skills-inspired files: e.g. a per-song / per-session
    descriptor an agent reads, and skills an agent uses to reason about mixing/experience-building — so
    Migx runs SIDE BY SIDE with Claude Code (the "Claude Code compatible DJ platform" differentiator),
  - assesses feasibility + how it composes with the harness (everything-is-code, greppable ontology),
  - recommends the initiative + first spike dossier (register a prefix, e.g. EXO / WLD).
---

# World-Model experience ontology for Migx (the differentiator)

**Vision:** Migx represents a **song** and a **DJ session** as a **flow of experience** — a timeline-based
ontology with a property graph of edges/connections — authored and reasoned over via **AGENTS.md-inspired
descriptors + Claude-Code-Skills-inspired** setup, so Migx is **Claude Code compatible** and can run side
by side with coding agents. That agent-native experience model is Migx's difference from Mixxx.

## The killer use case (the "why") — live agent co-piloting
In a live DJ session, run **Claude Code alongside the session, even affecting it**: analyse cue points,
suggest/set the next songs' order, flag harmonic/energy mismatches, propose transitions — in real time.
This requires Migx to expose the session as an agent-readable/writable surface (via ControlObject and/or
a filesystem/IPC mirror of the live state + the ontology) so an agent can both **read** (current deck,
position, cues, upcoming crate, the experience graph) and **write** (set a cue, reorder the queue,
suggest a track) safely, respecting house physics (never on the RT thread; changes marshalled to the
engine via ControlObject — `P-06`/`P-20`). This is the concrete differentiator: **Migx as a
Claude-Code-compatible DJ instrument** with an agent co-pilot in the loop.

## The three layers to design
1. **Song = an experience timeline** — sections, energy curve, harmonic journey, phrase structure, cues as
   experiential markers; its own ontology, grounded in `arch-track-model` (Track/Beats/Cues/Keys) +
   `arch-analyzer`.
2. **Session = a flow of experience** — the bigger ontology: how songs connect into a journey (energy arc,
   harmonic mixing, transitions, narrative). "How to build up experience."
3. **Property graph** — nodes + typed edges connecting songs/sections/cues/transitions/moods/sessions;
   the connective tissue that lets an agent plan a set as experience-design.

## Why it fits the harness
Everything-is-code (MG-2) applied to the DJ domain: the ontology is greppable, versioned, agent-readable.
AGENTS.md/Skills for songs+sessions mirror exactly what we built for the codebase — Migx becomes a
first-class citizen of the Claude Code world. Learn the World-Model *technique* from oz-platform (distill,
don't clone). Composes with [[analyse-filesystem-driven-architecture]] (where the ontology lives on disk)
and [[design-md-ui-modernization]] (markdown-as-SSoT).

## Recommendation
Almost certainly a **flagship standing initiative** (`initiative-experience-ontology` or similar) for a
major release — likely THE Migx differentiator. Start with a research + spike dossier: model one song's
experience timeline + one 3-track session flow as a property graph + an AGENTS.md-style descriptor an
agent can read, and prove an agent can reason a transition from it. Resolve storage (sidecar vs DB vs
graph) with the filesystem-driven analysis first. Research/architecture — no implementation yet.

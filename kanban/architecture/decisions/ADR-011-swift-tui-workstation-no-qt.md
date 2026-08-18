---
id: ADR-011
type: decision
title: "Migx is a Swift TUI workstation on Apple Silicon — Qt out, harness in"
status: accepted
owner: gudjon
created: "2026-08-18"
lastUpdated: "2026-08-18"
supersedes: []
amends: [ADR-002, ADR-007, ADR-009]
related: [ADR-006, ADR-008, ADR-010, P-02, P-11, P-34, arch-cli-commands]
---

# ADR-011 — Swift TUI workstation, no linked Qt

**Status: accepted 2026-08-18 (Gudjon).** Direction stated repeatedly and unambiguously across the
design conversation: Swift-first, Apple Silicon only, Qt out, TUI as the surface.

Accepting the ADR is reversible — it is a status field. **Deleting `src/` is not**, and this ADR does
not do it. The Mixxx tree stays on disk until a dossier removes it against acceptance, so the
irreversible half remains a separate, explicit decision.

## Context

`ADR-002` framed Migx as a hard fork of Mixxx. `ADR-009` moved the CLI/TUI to Swift. Two things have
since made the fork framing the expensive part rather than the useful part:

**The product is TUI-first.** Of Mixxx's ~30 `src/` domains, `qml`, `skin`, `widget`, `waveform`,
`rendergraph` and `shaders` render a GUI this product does not ship. `library`, `database` and the DAO
are indexes we have already declared derived and deletable. That is most of the fork carrying no
product weight.

**Every serious C++ problem this year was Qt or buildenv, not audio.** `just configure` hard-failing on
`BUILDENV_URL` so the suite had never run; two mapping tests failing on static-Qt QML plugin linkage;
the one real engine defect being a `Qt::DirectConnection` race in `EngineBuffer::notifyTrackLoaded`; an
11 GB dependency bundle and a 122 MB test binary. Meanwhile the audio ceiling we hit — no live
crossfader — was `ffplay`, not the platform: `AVAudioEngine` gives per-deck gain,
`AVAudioUnitTimePitch` and sample-accurate scheduling directly.

## Decision

**Migx is a Swift TUI workstation on Apple Silicon. No linked Qt.**

The distinction that makes this safe is **linked vs subprocess**, not "Qt vs Swift":

| Shape | Verdict |
| --- | --- |
| Mixxx code **linked into** the product | debt — drags Qt, vcpkg, DAO, a build environment |
| Mixxx code **behind a JSON subprocess** | fine — same relationship as `chafa` and `ffmpeg` |

`migx-analyze` is already the second shape: a headless binary emitting one JSON object per line. It
stays. **Analysis is not reimplemented** — BPM and key detection is years of accumulated DSP
correctness, and a Swift rewrite is invisible work with a real chance of being worse.

### Shape

    HUMAN (TUI)  ≡  AGENT        same tools, same IDs, no second surface
             │
             ▼
      HARNESS  ← the product: permissions · sandbox · transcript · tools · skills
             │
        ┌────┴────┬──────────────┐
        ▼         ▼              ▼
    FILESYSTEM  AUDIO CORE   INTELLIGENCE
    Collection/ AVAudioEngine  proposes only,
    .migx/      separate proc  never writes a fader
    Crates/     no songs, no DB

Three processes, two hard interfaces: audio exposes atomics and a socket; intelligence emits typed
proposals with provenance. Nothing else crosses.

### What this kills

- **`EPL`** (peel Qt off `process()`) — pointless if that `process()` goes. Deletes the program's
  flakiest acceptance criteria with it.
- **`BRG`** (unpark EngineBridge) — deferred indefinitely; returns only for club-grade DVS/timecode.
- The **two-audio-engines** contradiction: there is one audio core, and one analysis helper that is not
  an engine.
- The **session-state-home** question: state lives in Application Support, not on the music volume.

### What survives unchanged

Collection/crate/playlist · sidecar-as-SSoT with deletable indexes · domain never on `process()` ·
one command table with many adapters (`ADR-008`) · copilot proposes, DJ writes · APFS hardlinks ·
USB pack. All of it is *more* correct under this model.

## Consequences

- **Migx stops being a Mixxx fork.** It becomes a new product that uses one Mixxx binary. That is the
  real cost of this ADR and the reason it is `proposed`.
- **The 1,298 C++ tests go with the engine.** Coverage drops sharply and must be rebuilt around our own
  code. This is the largest concrete loss.
- Vinyl/DVS, timecode, broadcasting and recording are out. For a TUI-first prep-and-perform tool, none
  of those is the product.
- `ADR-007`'s QML shell is moot. `ADR-009` extends from "CLI language" to "the whole product".

## Non-goals

Rewriting the engine in Swift · treating `AVAudioEngine` as Mixxx's `process()` · a SwiftUI booth
before the TUI is Swift · MCP · reimplementing analysis · a graph database as the library.

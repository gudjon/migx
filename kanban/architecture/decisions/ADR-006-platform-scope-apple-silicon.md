---
id: ADR-006
type: decision
title: "Platform scope — macOS 26+ on Apple Silicon only"
status: accepted
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
supersedes: []
amends: []
related: [ADR-002, ADR-004, initiative-apple-silicon, strategy-current]
---

# ADR-006 — Platform scope: macOS 26+ · Apple Silicon only

## Context
DJs who matter for Migx run **macOS on Apple Silicon**. Multi-OS, multi-arch support multiplies
audio backends, packaging, CI, GUI paths, and code-signing for little audience. Migx’s north-star is
**M4/M5 performance** (Metal, Accelerate, Core Audio, arm64-native) under house physics (`P-02`,
`P-24`).

Owner decision (2026-07-17, refined): the **supported product** is exclusively:

> **macOS 26.\* and later, on Apple Silicon (arm64) only.**

No Intel Mac. No Rosetta. No Windows/Linux product surface. Future platforms (e.g. iPad) would be a
**new decision**, not implied support.

## Decision

1. **Sole supported target:** **macOS ≥ 26.0** on **Apple Silicon arm64**.  
   - Deployment target: `CMAKE_OSX_DEPLOYMENT_TARGET=26.0`  
   - Architecture: `CMAKE_OSX_ARCHITECTURES=arm64` only (`P-24`)  
   - Audio: Core Audio first  
   - Packaging: single path (DMG + notarize)  
   - CI: macOS arm64 only when enabled  

2. **Out of support (not maintained, not a design driver):**  
   - macOS **&lt; 26**  
   - **Intel** Mac (x86_64 / Rosetta)  
   - **Windows** desktop  
   - **Linux** desktop  
   - **Android**  
   - **iOS / iPadOS** as a shipping target (research/watch only until a future ADR)  

3. **Build system:** configure **fails** if Darwin + non-arm64. Prefer fatal messages over silent
   multi-arch universal binaries.

4. **OS 26 audio stack:** product may use OS 26 APIs (see
   `kanban/knowledge/apple-audio-frameworks-os26-wwdc25.md`); RT engine still obeys house physics.

## Consequences

- **Massive simplification:** one OS major floor, one arch, one packaging story.  
- **Perf work compounds** on the only machine class we care about (M4/M5).  
- **Upstream Mixxx portability paths** (Win/Linux/Intel) go dormant; prune when touched (`P-11`).  
- Re-opening another platform requires a **new ADR**, not a casual `#ifdef`.

## Enforcement surfaces

| Surface | What |
|---|---|
| This ADR | Decision SSoT |
| `CMakeLists.txt` | `CMAKE_OSX_DEPLOYMENT_TARGET=26.0`, arm64-only |
| `README.md` | Platform table |
| `kanban/runbooks/build-setup-macos-m4.md` | Build profile |
| `justfile` `configure` | Passes deployment target + arm64 |
| `P-24` | arm64-native pattern |

---
id: ADR-006
type: decision
title: "Platform scope — Apple Silicon first: macOS now, iPad next; Windows later, Linux only-if-embedded"
status: accepted
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
supersedes: []
amends: []
related: [ADR-002, ADR-004, initiative-apple-silicon, strategy-current]
---

# ADR-006 — Platform scope: Apple Silicon first

## Context
DJs run **macOS predominantly**, **some Windows**, and **effectively none on Linux desktop**.
Supporting three desktop OSes across two architectures multiplies the compatibility surface — audio
backends, packaging, CI, GUI paths, code-signing — for near-zero audience gain. That is the opposite of
the Cursor-style focus Migx is built on ([ADR-002](ADR-002-hard-fork-no-upstream-merge.md): free to
prune).

Migx's north-star is already **Apple Silicon performance** (Metal, M4/M5). That investment — native
arm64, Metal render/DSP, CoreAudio — **transfers directly to other Apple-GPU devices**, most naturally
**iPad** (A/M-series SoC, Metal, arm64). So the platform bet is *Apple Silicon*, not merely *macOS*.

Gudjon's decision (2026-07-17): narrow hard to Apple Silicon to simplify massively on compatibility.

## Decision
1. **Sole current target: macOS on Apple Silicon (arm64).** Native arm64 only — no x86_64 / Rosetta
   (reinforces `P-24`). CoreAudio-first. Single-arch, single-packaging (DMG + notarize), macOS-only CI.
2. **iPad / iPadOS is the sensible next platform.** Same SoC / Metal / arm64 foundation — the
   render and DSP optimization work is meant to compound toward it. Keep the `ios/` seam warm; do not
   invest execution there yet.
3. **Windows: deferred ("later").** Some DJs run it; it may return as a deliberate future bet. Not
   maintained now and not a design driver. Don't burn portability where it's cheap, but do no Windows
   work (the `packaging/wix/` surface goes dormant, not actively removed).
4. **Linux desktop: dropped.** Not the DJ audience. The *only* conceivable future is an
   **embedded / appliance** build — e.g. Jetson with integrated DJ hardware — which is **explicitly out
   of scope now**. Retire Linux desktop build / packaging / CI (flatpak, debian, PPA) as those paths
   are touched.
5. **Android: out of scope** — not part of the DJ-device thesis.

## Consequences
- **Simplification unlocked:** one audio backend (CoreAudio), one arch, one packaging path, macOS-only
  CI, and opportunistic removal of Windows/Linux `#ifdef` churn as code is touched.
- **Faster iteration, smaller test/compat surface** — the whole point.
- **iPad is the growth path** the Apple-Silicon work already compounds toward; the perf dossiers
  (`initiative-apple-silicon`, MTL-*) double as iPad readiness.
- **Windows / embedded re-entry later is a deliberate future bet, not free** — accepted.

The execution (pruning Linux desktop build/packaging/CI, quieting Windows CI) is scoped as a task, not
done in this ADR.

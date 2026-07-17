---
id: P-15
type: pattern
title: "Trace the affected call paths file:line before touching a subsystem"
status: active
severity: SHOULD
domain: harness
related: [P-11, P-16, P-26]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-15 — Trace the affected call paths file:line before touching a subsystem

## Statement
Before modifying an engine subsystem, trace the call paths the change touches to concrete
`file:line` references — who calls it, what it calls, which thread each runs on — and record that trace
as part of the change. Don't refactor what you haven't mapped.

## Why
The engine is a dense graph with hard cross-thread rules (`P-02`, `P-16`, `P-20`); a change that looks
local often reaches `process()` through a path you didn't see, or is called from both the GUI and the
RT thread. Tracing first is what turns "I think this is safe" into "here are the exact reachable paths
and their threads." It's the precondition for migrating all callers and deleting cleanly (`P-11`), and
it's exactly the navigation a compile database makes exact (`P-26`).

## How to apply
- Enumerate callers and callees to `file:line` (clangd/grep across `src/`), and annotate which thread
  each site runs on — especially whether any path is reachable from `process*()`.
- Capture the trace in the PR/dossier so the reviewer checks the same map you did.
- Use the trace to size the migration (`P-11`): every caller you found is one you must port or delete.
- If the trace surfaces an RT-reachable path, the cross-thread rules (`P-16`, `P-20`, `AP-14`) apply.

## Example — wrong
> Renamed and re-signatured a `EngineBuffer` helper "it's only used here," missing two call sites — one
> of them on the audio callback. Compiles; regresses house physics.

## Example — right
> Trace before touch: `enginebuffer.cpp:412` (GUI thread) and `enginebufferscale.cpp:88` (RT thread)
> call it; RT path must stay alloc-free (`P-02`). Both ported in the same change (`P-11`).

## Detection
Review: an engine refactor with no recorded call-path trace; a missed caller found after merge; a
cross-thread reach discovered late.

## Cross-references
Precondition for `P-11`; surfaces the cross-thread paths governed by `P-16`/`P-20`; made exact by the
compile database `P-26`.

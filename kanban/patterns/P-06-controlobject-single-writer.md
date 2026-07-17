---
id: P-06
type: pattern
title: "Each ControlObject has a single writer"
status: active
severity: MUST
domain: ssot
related: [AP-03, P-16, P-20]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-06 — Each ControlObject has a single writer

## Statement
For each `[Group], key` ControlObject, exactly one component is the authoritative **writer**; every
other component reads it through a `ControlProxy`. Ownership of who-writes-what is decided once and
documented.

## Why
ControlObject is Migx's inter-component bus (MG-6): a shared, thread-safe value addressed by a string
key. It's a single-source-of-truth surface (MG-3) — but only if it has a single writer. Two writers
race: their values fight, the reader can't tell which is authoritative, and the bug is
non-deterministic and timing-dependent (the worst kind to debug in a real-time app). A single writer
makes the value's meaning unambiguous and its history traceable to one place.

## How to apply
- When you add a control, name its writer in the owning component and treat every other reference as
  read-only via `ControlProxy`.
- If two components "need" to write the same control, that's a design smell — introduce an explicit
  arbiter that owns the write, or split into two controls.
- Cross-thread writes still go through the control's atomic path, not a back-channel (see `P-16`).

## Example — wrong
```cpp
// EngineBuffer writes [ChannelN],rate; and a controller script ALSO writes it directly.
// Two writers → the deck rate flickers between engine-computed and script-set values.
```

## Example — right
```cpp
// EngineBuffer is the sole writer of [ChannelN],rate. The controller writes [ChannelN],rate_set
// (an input control); EngineBuffer reads that, arbitrates, and writes the authoritative rate.
```

## Detection
Review: grep the `[Group],key` literal across `src/` and `res/` — more than one `set()`/write site
outside the owning component is a violation. Phase-3 lint can flag multi-writer controls.

## Cross-references
Violation is `AP-03` (second-writer-on-a-controlobject). Cross-thread mechanics: `P-16`. Thread
affinity: `P-20`.

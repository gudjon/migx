---
id: AP-03
type: antipattern
title: "Second writer on a ControlObject"
status: active
severity: MUST-NOT
domain: ssot
related: [P-06, P-20]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-03 — Second writer on a ControlObject

## What it looks like
Two or more components call `set()` on the same `[Group], key` ControlObject. The value flickers
between what each writer believes it should be; a reader (`ControlProxy`) sees a non-deterministic,
timing-dependent value it can't attribute to any single source.

## Why it's harmful
ControlObject is a single-source-of-truth surface (MG-3, `P-06`). Two writers make its meaning
ambiguous and the bug non-reproducible — it depends on thread interleaving and buffer timing, the
hardest class to debug in a real-time app. It also hides intent: the next agent can't tell which
component "owns" the value.

## What to do instead
- Give the control exactly one authoritative writer (`P-06`); every other component reads via
  `ControlProxy`.
- If two components genuinely need to influence the value, split into an *input* control they write
  and an *authoritative* control the single owner computes and writes, or introduce an explicit arbiter.

## Detection
Grep the `[Group],key` literal across `src/` and `res/`: more than one write site outside the owning
component is the smell. Phase-3 lint flags multi-writer controls.

## Cross-references
Violates `P-06` (single-writer). Related thread hazard: `P-20`.

---
id: P-11
type: pattern
title: "Change in place or migrate-all-callers-and-delete; never add a _v2 beside"
status: active
severity: SHOULD
domain: harness
related: [P-15, P-12, AP-07]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-11 — Change in place or migrate-all-callers-and-delete; never add a _v2 beside

## Statement
To change behavior, either edit the canonical implementation in place, or add the replacement, migrate
**all** callers to it, and delete the old one in the same change. What you must not do is leave a
`_v2`/parallel path standing beside the original "to clean up later." Every add deletes.

## Why
A parallel path is a second source of truth for behavior (MG-3): now there are two implementations,
two sets of bugs, and every caller-site is a coin flip about which one is live. "Clean up later" almost
never happens, so the layer calcifies and the next agent can't tell which path is authoritative. In an
RT engine this is especially costly — a stale second path can still be reachable from `process()` and
silently regress house physics. Deleting as you go keeps the graph traceable (`P-15`) and the codebase
one-implementation-per-behavior.

## How to apply
- Prefer editing in place when the change is contained.
- When you must introduce a new implementation, treat "migrate every caller + delete the old" as part
  of the *same* task, not a follow-up — trace the callers first (`P-15`).
- If you genuinely can't migrate all callers now, that's a signal to freeze the old path as a golden
  (`P-12`) and scope the migration explicitly — not to leave two live paths unlabeled.

## Example — wrong
```cpp
double gain(double x);      // original, still called in 30 places
double gain_v2(double x);   // "better" version, called in 3 — both live, nobody deletes gain()
```

## Example — right
```cpp
// Change gain() in place, OR: add the new impl, port all 33 callers, delete the old gain() —
// one change, one implementation left standing.
```

## Detection
Review: a new `*_v2`/`*New`/parallel function or class added without deleting its predecessor; two live
implementations of one behavior. Grep for the old symbol post-change — nonzero callers means unfinished.

## Cross-references
Requires the caller trace `P-15`; when full migration must wait, freeze via `P-12`. Its violation is
`AP-07`.

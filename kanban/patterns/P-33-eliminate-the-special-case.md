---
id: P-33
type: pattern
title: "Eliminate the special case, don't just handle it"
status: active
severity: SHOULD
domain: engine
related: [P-11, AP-07]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-33 — Eliminate the special case, don't just handle it

## Statement
When you reach for `if (edge_case) { special path } else { normal path }`, first ask whether the data
structure or algorithm can be reshaped so the edge case **is** the normal path. Prefer designs where the
special case disappears over designs that branch to handle it ("good taste," per Linus Torvalds).

## Why
Special-case branches multiply: each new edge adds a path that interacts with every other path
(quadratic, like layering — `AP-07`). Every branch is a place a bug hides, and on the real-time audio
path a mispredicted or extra branch is also a cost. Removing the special case — a sentinel node, a
uniform representation, an invariant that makes the edge impossible — leaves one path that is easier to
read, test, and keep correct. The classic example: deleting a list node with a "prev-pointer-to-pointer"
so the head is not a special case.

## How to apply
- Before adding a branch, ask: *can I change the data so this edge is handled by the general code?*
  (sentinels, empty-object patterns, normalizing inputs at the boundary, an invariant enforced upstream).
- Prefer one code path with uniform handling over two paths that must stay in sync.
- On the RT engine path especially, fewer branches = fewer bugs and better predictability.

## Example — wrong
```cpp
if (channels == 1) { /* mono special-case copy */ } else { /* stereo path */ }   // two paths to keep in sync
```

## Example — right
```cpp
// Normalize to a uniform interleaved layout at the boundary; the process loop has ONE path.
```

## Detection
Review + audit: clusters of `else if` / special-case flags. Migx inherits large upstream branch
clusters (e.g. `src/engine/controls/cuecontrol.cpp` ~2930 lines / ~21 `else if`,
`loopingcontrol.cpp`) — this pattern is the forward-looking guard when *touching* such code. As a true
hard fork (`ADR-002`) a deliberate rewrite is allowed, but behind a build+test gate — favor eliminating
the special case as you touch the code over a risky wholesale rewrite.

## Cross-references
Sibling of `P-11` (refactor-over-layer); avoiding it tends toward `AP-07`. Encodes the
eliminate-special-cases craft principle (see `kanban/knowledge/craft-principles-audit.md`).

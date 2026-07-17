---
id: AP-13
type: antipattern
title: "QObject without a parent"
status: active
severity: MUST-NOT
domain: qt-ownership
related: [P-19, P-17]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-13 — QObject without a parent

## What it looks like
A `QObject` created via `make_parented`/`parented_ptr` (or `new`) never receives a valid parent in
the Qt object tree before its holder goes out of scope — an orphan with ambiguous ownership.

## Why it's harmful
Migx uses `parented_ptr` precisely to assert tree ownership (MG-6, `P-19`). An orphan defeats it: the
lifetime is owned by neither the tree nor a clear deleter, producing a leak, or a double-free when both
the tree teardown and a manual `delete` try to reclaim it. These surface as crashes under load — the
worst time.

## What to do instead
- Set the parent at construction: `make_parented<T>(parent, ...)` with a live QObject parent (`P-19`).
- If the parent isn't known at construction, `setParent` it before the holder can destruct — never let
  the scope end with an orphan.
- Don't mix manual `delete` with tree-owned objects.

## Detection
Review: a `make_parented`/`parented_ptr`/`new QObject` whose object never gets a parent; Qt/ASan leak
reports in widget and engine tests.

## Cross-references
Violates `P-19`; interacts with RT lifetime `P-17`.

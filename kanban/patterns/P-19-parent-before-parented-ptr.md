---
id: P-19
type: pattern
title: "A QObject gets a parent before its parented_ptr destructs"
status: active
severity: MUST
domain: qt-ownership
related: [AP-13, P-17, P-20]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-19 — A QObject gets a parent before its parented_ptr destructs

## Statement
Any `QObject` held by a `parented_ptr` (via `make_parented`) must acquire a valid parent in the Qt
object tree before that `parented_ptr` goes out of scope. Establish ownership at construction.

## Why
`parented_ptr` is Migx's guard for Qt's object-tree ownership model (MG-6): it asserts the object has
a parent so the tree, not the pointer, owns the lifetime. If the object never gets a parent, you get
ambiguous ownership — a leak, or a double-free when both the tree and a raw delete try to reclaim it.
The whole point of the idiom is defeated if the parent is never set. The repo-root `AGENTS.md` is the
SSoT for this house rule.

## How to apply
- Pass the parent at construction: `make_parented<T>(parent, ...)` where the parent is already a live
  QObject in the tree.
- If construction can't know the parent yet, set it (`setParent`) before the `parented_ptr` can
  destruct — do not let the scope end with an orphan.
- Don't mix manual `delete` with parent-owned objects; let the tree own it.

## Example — wrong
```cpp
auto w = make_parented<WWidget>(nullptr);   // never re-parented → orphan; leak or double-free
```

## Example — right
```cpp
auto w = make_parented<WWidget>(this);      // parent set at construction; tree owns lifetime
```

## Detection
Review: a `make_parented`/`parented_ptr` whose object never receives a parent; Qt/ASan leak reports in
widget/engine tests.

## Cross-references
Violation is `AP-13`. RT-lifetime interaction: `P-17`. Thread affinity: `P-20`.

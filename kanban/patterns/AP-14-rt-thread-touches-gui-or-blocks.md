---
id: AP-14
type: antipattern
title: "RT thread touches GUI or blocks"
status: active
severity: MUST-NOT
domain: engine
related: [P-02, P-16, P-17, P-20]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-14 — RT thread touches GUI or blocks

## What it looks like
Code reachable from the audio callback (`process*()`) mutates a GUI `QObject`, synchronously receives
a signal / calls a slot via `Qt::DirectConnection`, takes a mutex, or otherwise blocks on another
thread.

## Why it's harmful
The audio thread runs on a hard deadline (`P-02`, MG-6). Any of these can allocate, lock, page-fault,
or run arbitrary slot code on the callback — causing priority inversion and underruns (audible
dropouts). It's the concrete mechanism behind most "faster on average, glitches under load"
regressions (`AP-02`).

## What to do instead
- RT → GUI: *emit* a Qt signal (queued delivery) or write a `ControlObject`; never call a GUI method or
  mutate a GUI object directly (`P-20`).
- GUI → RT: hand data across via the lock-free path (ring buffer / atomic double-buffer / ControlObject,
  `P-16`); do allocation/lifetime off the RT thread (`P-17`).
- Never `QMutex`/`std::mutex`/blocking queued connections on any `process()`-reachable path.

## Detection
Review: GUI mutation, `DirectConnection` across the RT boundary, or a lock/blocking call reachable from
`process*()`; ThreadSanitizer + an allocation-counting allocator on engine tests (`P-32`).

## Cross-references
Violates `P-02`, `P-20`; the safe alternatives are `P-16` and `P-17`; contributes to `AP-02`.

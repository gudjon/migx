---
id: P-02
type: pattern
title: "Never allocate or lock on the real-time audio thread"
status: active
severity: MUST
domain: engine
related: [AP-02, P-03]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-02 — Never allocate or lock on the real-time audio thread

## Statement
While code executes on the real-time audio callback path (the engine thread), it shall not allocate
heap memory, take a mutex, do file/network I/O, or otherwise block. It may emit Qt signals but must
not receive them synchronously.

## Why
The audio callback runs on a deadline (a buffer period — often <3 ms). A single `malloc`, lock
contention, or page fault causes an underrun — an audible click or dropout. On Apple Silicon this is
sharper: an optimization that improves *average* throughput but occasionally allocates on the RT path
is a **regression**, because DJ software is judged on worst-case glitch-free playback, not averages.
This is house physics (MG-6); the repo-root `AGENTS.md` is its SSoT.

## How to apply
- Pre-allocate all buffers outside the callback; reuse them.
- Communicate with the RT thread via lock-free ring buffers / `ControlObject` atomics, never mutexes.
- Do parameter changes and object lifetime on the GUI/worker thread; hand results to the RT thread
  through a lock-free channel.
- For SIMD/Accelerate optimizations (the north-star), keep the fast path allocation-free — set up
  `vDSP` state and scratch buffers once, at construction.

## Example — wrong
```cpp
// In an EngineBuffer/EngineEffect process() on the RT thread:
std::vector<float> scratch(bufferSize);   // heap allocation on the audio thread — underrun risk
QMutexLocker lock(&m_mutex);              // lock on the audio thread — priority-inversion risk
```

## Example — right
```cpp
// Allocated once at construction; reused every callback:
m_scratch.resize(kMaxBufferSize);         // outside the RT path
// process() on the RT thread only reads/writes preallocated storage, lock-free.
```

## Detection
- Review: any `new`/`malloc`/`std::vector` ctor/`QMutex` inside a `process*()` on the engine path.
- Tooling (Phase 3): a clang-tidy/annotation check flagging allocation in RT-annotated functions;
  a benchmark that asserts zero allocations on the callback (e.g. an allocation-counting allocator in
  a GoogleTest harness).

## Cross-references
Risks `AP-02`. The evaluation contract that guards it: `P-03`.

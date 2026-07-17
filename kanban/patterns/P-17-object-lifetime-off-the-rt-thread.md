---
id: P-17
type: pattern
title: "Object lifetime happens off the real-time thread"
status: active
severity: MUST
domain: engine
related: [P-02, P-16, P-19, AP-14]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-17 — Object lifetime happens off the real-time thread

## Statement
Engine objects and buffers are constructed and destroyed on the GUI/worker thread. The real-time
audio thread only *uses* already-allocated objects; ownership transfers to and from the RT thread via
a lock-free swap, never via `new`/`delete`/`make_parented` on the callback path.

## Why
`new`/`delete` take the allocator lock and can page-fault — both fatal on the audio deadline
(`P-02`). The RT thread must run allocation-free. So allocation and destruction are pushed to a thread
that *can* block; the RT thread receives a ready-made object by pointer swap and never owns the
allocation lifecycle.

## How to apply
- Pre-allocate every buffer and working object outside the callback (at construction or on parameter
  change), sized for the worst case; the RT path reuses them.
- To swap in a new object (e.g. a rebuilt filter, a resized buffer), build it on the GUI/worker
  thread, then hand it to the RT thread with an atomic pointer swap (`P-16`); reclaim the old one back
  on the GUI thread after the RT thread has released it.
- Never call `delete` or let a `parented_ptr`/`unique_ptr` destruct on the RT path.

## Example — wrong
```cpp
void EngineX::process(...) {
    auto tmp = std::make_unique<Buffer>(size);   // allocation + destruction on the RT thread
}
```

## Example — right
```cpp
// Constructed once, off the RT thread; process() reuses m_scratch, which is never (re)allocated here.
EngineX::EngineX() { m_scratch.resize(kMaxBufferSize); }
```

## Detection
Review: any allocation/free/smart-pointer destruction reachable from `process*()`; an
allocation-counting allocator asserting zero RT allocations in engine tests (`P-32`).

## Cross-references
Serves `P-02`; uses `P-16` for the swap; Qt ownership is `P-19`; violation is `AP-14`.

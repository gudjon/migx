---
id: P-16
type: pattern
title: "GUI↔engine data crosses via a lock-free handoff"
status: active
severity: MUST
domain: engine
related: [P-02, P-17, AP-14, P-06]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-16 — GUI↔engine data crosses via a lock-free handoff

## Statement
When data crosses between the real-time audio thread and any other thread, it crosses via a lock-free
mechanism — an SPSC ring buffer, an atomic double/triple-buffer swap, or a `ControlObject` atomic —
never a mutex, a queued blocking call, or a shared container guarded by a lock.

## Why
A lock on the audio callback is the direct path to priority inversion and underruns (`P-02`, MG-6):
the RT thread can be blocked by a lower-priority thread holding the lock, miss its buffer deadline,
and glitch. Lock-free handoff lets the RT thread make progress unconditionally. Migx already provides
the primitives — `util/fifo.h` (ring buffers) and the `ControlObject` atomic path — so there's no
excuse to reach for a mutex on the hot path.

## How to apply
- Producer/consumer across the RT boundary → an SPSC ring (`util/fifo.h`). The RT side never waits;
  if the ring is full/empty it degrades gracefully (drops or reuses last), it does not block.
- Parameter snapshots the RT thread reads → an atomic double-buffer: the writer fills an inactive
  buffer and atomically flips a pointer; the RT thread reads the current one, wait-free.
- Single scalar values → `ControlObject`/`ControlProxy` (already atomic), respecting `P-06`.
- Never `QMutex`, `std::mutex`, `QMetaObject::invokeMethod(..., BlockingQueuedConnection)`, or a
  `QQueue` under a lock on any path reachable from `process()`.

## Example — wrong
```cpp
// In an engine process() path:
QMutexLocker lock(&m_paramMutex);   // RT thread can block on the GUI thread → underrun
m_params = m_pendingParams;
```

## Example — right
```cpp
// GUI thread fills m_params[inactive] then: m_active.store(inactive, std::memory_order_release);
// RT thread: const auto& p = m_params[m_active.load(std::memory_order_acquire)];  // wait-free
```

## Detection
Review: any lock/blocking call reachable from a `process*()`; ThreadSanitizer on engine tests (`P-32`).

## Cross-references
Serves `P-02`; pairs with `P-17` (lifetime off the RT thread); violation is `AP-14`.

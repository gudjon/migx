---
description: "Real-time audio-thread safety — the house physics that a perf change must never break"
paths:
  - src/engine/**
  - src/effects/**
  - src/vinylcontrol/**
  - src/soundio/**
---

# Rule — real-time audio safety

You are editing code that may run on the **real-time audio callback thread**. This is Migx's most
load-bearing invariant (MG-6). SSoT of the substance: repo-root `AGENTS.md`. Pattern cards:
`kanban/patterns/P-02`, `P-16`, `P-17`, `P-20`, `AP-02`, `AP-14`.

## Hard rules on any `process*()`-reachable path
- **No allocation** — no `new`/`malloc`, no `std::vector` growth/resize, no smart-pointer construction
  or destruction. Pre-allocate at construction; reuse. (`P-02`, `P-17`)
- **No locks / no blocking** — no `QMutex`/`std::mutex`, no blocking queued connections, no file/network
  I/O. Cross-thread data crosses lock-free: ring buffer (`util/fifo.h`), atomic double-buffer, or
  `ControlObject`. (`P-16`)
- **No GUI touch** — the RT thread may *emit* Qt signals but must never receive one synchronously,
  call a slot via `Qt::DirectConnection`, or mutate a GUI QObject. (`P-20`, `AP-14`)
- **One writer per ControlObject** — `[Group],key` has a single authoritative writer; others read via
  `ControlProxy`. (`P-06`, `AP-03`)

## For performance work (the Apple Silicon north-star)
A speedup that violates any rule above is a **correctness regression, not an optimization** (`AP-02`).
Perf claims need a benchmark contract: p99/max buffer time + zero underruns vs a pinned baseline, not a
mean (`P-03`, `P-18`, `AP-11`). Set up SIMD/Accelerate/Metal state and scratch buffers **once**, at
construction — keep the fast path allocation-free.

## Before you commit
Confirm no allocation/lock/GUI-touch was added to an RT path; run `pre-commit run --files <changed>`.
Engine tests: `ctest --test-dir build -R Engine`. Domain charter: `src/engine/AGENTS.md`.

---
id: P-20
type: pattern
title: "Respect QObject thread affinity; the RT thread never touches a QObject"
status: active
severity: MUST
domain: qt-ownership
related: [P-02, P-16, AP-14, P-19]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-20 — Respect QObject thread affinity; the RT thread never touches a QObject

## Statement
A `QObject` lives on the thread that created it; cross-thread communication uses queued signal/slot
connections. The real-time audio thread must never mutate a QObject, never synchronously receive a
signal, and never call a slot that runs on it — it may only *emit* signals (delivered queued to
another thread).

## Why
Qt's event and signal machinery is not real-time safe: a direct cross-thread slot call, a queued
connection's event allocation, or mutating a GUI object from the audio thread can allocate, lock, or
race (`P-02`, MG-6). Migx's engine thread is allowed to *emit* Qt signals (fire-and-forget) but cannot
*receive* them — receiving would run arbitrary slot code on the audio deadline. Affinity keeps GUI
state on the GUI thread and audio work on the audio thread.

## How to apply
- Create QObjects on the thread that will own them; don't hand a QObject to the RT thread to mutate.
- RT → GUI: emit a signal (queued delivery) or write a `ControlObject`; never call a GUI method
  directly.
- GUI → RT: hand data across via the lock-free path (`P-16`), not by invoking a method on an RT object
  from the GUI thread.
- Never `connect(..., Qt::DirectConnection)` across the RT boundary.

## Example — wrong
```cpp
// On the audio thread:
m_pLabel->setText("playing");                 // mutating a GUI QObject from the RT thread
connect(src, &S::sig, this, &T::slot, Qt::DirectConnection); // slot would run on the RT thread
```

## Example — right
```cpp
// RT thread emits; the slot runs on the receiver's (GUI) thread via a queued connection:
emit playStateChanged(true);                  // fire-and-forget, RT-safe
```

## Detection
Review: RT-reachable code mutating a QObject or using `DirectConnection` across threads;
ThreadSanitizer on engine tests (`P-32`).

## Cross-references
Serves `P-02`; cross-thread data uses `P-16`; ownership is `P-19`; violation is `AP-14`.

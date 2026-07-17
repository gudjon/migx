---
id: P-30
type: pattern
title: "Controller scripts reach the engine only via ControlObject"
status: active
severity: MUST
domain: controllers
related: [P-06, P-16, P-20, AP-15]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-30 — Controller scripts reach the engine only via ControlObject

## Statement
Controller JavaScript (the `*-scripts.js` run by the QJSEngine in `src/controllers/scripting/`) reaches
the engine **only** through ControlObject — `engine.setValue`/`engine.getValue`/`makeConnection` on a
`[Group],key`. It never blocks the real-time audio thread and never touches an engine or GUI object
directly.

## Why
Controller scripts run on the controller's own thread, driven by hardware input at unpredictable times.
ControlObject is the thread-safe, atomic bus built exactly for this cross-thread reach (MG-6, `P-16`) —
it lets a script influence the engine without a lock, a direct call, or a QObject hop across threads
(`P-20`). If a script could call engine methods directly it would race the audio callback or block it,
producing the priority-inversion dropouts the whole house physics exists to prevent (`P-02`). The
ControlObject boundary keeps the script sandbox loosely coupled and RT-safe.

## How to apply
- From JS, use `engine.setValue([Group],key,v)` / `engine.getValue` / `engine.makeConnection`; treat
  the control as the only interface to the engine.
- Respect single-writer (`P-06`): a script writes *input* controls; the engine arbitrates and writes
  the authoritative ones — two writers on one key is `AP-03`.
- Never reach for an engine/GUI object pointer from script, and never do blocking work that could stall
  a control the RT thread reads.
- Keep device constants in the mapping data (`P-29`), not baked into the script logic (`AP-15`).

## Example — wrong
```js
// Pretending to reach past the bus (or busy-waiting on the engine):
engine.getEngineBuffer("[Channel1]").setRateDirectly(1.03);   // no such path — would bypass the CO bus
```

## Example — right
```js
// Through the ControlObject bus, on the script thread, non-blocking:
engine.setValue("[Channel1]", "rate", 0.03);      // writes an input control; engine arbitrates (P-06)
```

## Detection
Review: controller JS attempting direct engine/GUI access or blocking work; a script writing a control
the engine also writes (`AP-03`). All script→engine traffic should be `engine.*` ControlObject calls.

## Cross-references
Uses the lock-free bus `P-16` under single-writer `P-06`; respects thread affinity `P-20`; mappings
stay data per `P-29`. Baking constants into the script is `AP-15`.

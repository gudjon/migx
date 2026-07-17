---
id: P-29
type: pattern
title: "MIDI/HID mappings live in declarative data, not C++"
status: active
severity: SHOULD
domain: controllers
related: [P-30, AP-15]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-29 — MIDI/HID mappings live in declarative data, not C++

## Statement
A controller mapping — which MIDI/HID message drives which control, and the light/soft-takeover
behavior around it — lives in the declarative mapping files under `res/controllers/` (`*.midi.xml` +
its `*-scripts.js`), not hardcoded into engine or C++ code.

## Why
`res/controllers/` is the SSoT for controller behavior (MG-3, `P-07`): a mapping is data the app loads,
so a user can add or tweak hardware support without recompiling, and hundreds of devices coexist as
files rather than branches in C++. Hardcoding a device's message→control wiring into C++ forks that
model — the behavior is now invisible to the mapping system, un-overridable by users, and the C++ grows
a special case per device. Keeping mappings as data is what makes the controller subsystem scale.

## How to apply
- Express message→control bindings in the device's `*.midi.xml`; put any non-trivial logic in the
  paired `*-scripts.js`, which reaches the engine only via ControlObject (`P-30`).
- Add a new device by adding files under `res/controllers/`, not by editing C++.
- Constants a mapping needs (channels, LED values, thresholds) live in the XML/JS, not baked into C++
  (`AP-15`).

## Example — wrong
```cpp
// In C++: special-case a specific controller's note number.
if (status == 0x90 && note == 0x0C) deck1Play();   // device wiring hardcoded in engine code
```

## Example — right
```xml
<!-- res/controllers/MyController.midi.xml -->
<control><status>0x90</status><midino>0x0C</midino>
  <group>[Channel1]</group><key>play</key></control>
```

## Detection
Review: MIDI/HID status/note constants or device-specific wiring in C++ instead of `res/controllers/`;
a new device requiring a recompile.

## Cross-references
The script side reaches the engine via `P-30`; it's `P-07` applied to controllers. Baking mapping
constants into C++ is `AP-15`.

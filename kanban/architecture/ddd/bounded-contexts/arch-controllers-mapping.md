---
id: arch-controllers-mapping
type: ddd-bounded-context
title: "controllers-mapping — MIDI/HID hardware bound to controls via scripts"
owns:
  - src/controllers/            # ControllerManager, Controller, midi/, hid/, bulk/, scripting/ QJSEngine, mappings, SoftTakeover
exclude: []
thread_domain: worker + gui
rt_safety: none
subdomain: supporting
upstream: [arch-control-messaging]
downstream: [arch-control-messaging]
maturity: operational
fork_delta: upstream-tracking
agents_md: src/controllers/AGENTS.md
last_audited: "2026-07-17"
---

# controllers-mapping — bounded context

Hardware in, controls out. `ControllerManager` enumerates and opens each `Controller` (MIDI, HID, USB
bulk), the input events run through a declarative `LegacyControllerMapping` and its JavaScript, and the
script reaches the rest of Migx **only** by writing `ControlObject`s. The QJSEngine
(`ControllerScriptEngineLegacy`) and the I/O threads are worker/GUI — never the audio callback
(`rt_safety: none`). Mappings live in data (`res/controllers/`), not C++. Pointers, never copies —
`src/controllers/` is the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `ControllerManager` | `controllers/controllermanager.cpp` | enumerates/opens controllers; owns the polling thread |
| `Controller` | `controllers/controller.cpp` | abstract device: receive events, send output |
| `MidiController` | `controllers/midi/midicontroller.cpp` | MIDI device binding |
| `HidController` | `controllers/hid/hidcontroller.cpp` | HID device binding |
| `BulkController` | `controllers/bulk/bulkcontroller.cpp` | raw USB bulk device binding |
| `ControllerScriptEngineLegacy` | `controllers/scripting/legacy/controllerscriptenginelegacy.cpp` | the mapping QJSEngine |
| `LegacyControllerMapping` | `controllers/legacycontrollermapping.cpp` | parsed declarative mapping (XML + JS) |
| `SoftTakeover` | `controllers/softtakeover.cpp` | prevents value jumps when a knob re-engages |

## Invariants (an agent MUST respect these)
- **Mappings are declarative data (`P-29`/`AP-15`):** device→control behaviour lives in
  `res/controllers/` XML+JS, not compiled `if` chains; no hard-coded tuning/mapping constants in C++.
- **Scripts reach the engine only via ControlObject (`P-30`):** a mapping script never calls engine
  internals directly — it writes `[Group],key` controls, which the single-writer rule governs.
- **Never on the RT thread (`P-17`/`P-20`):** device I/O and the QJSEngine run on worker/GUI threads;
  they hand values to the RT engine through the lock-free control bus, never a synchronous callback.
- **Single writer (`P-06`/`AP-03`):** a script must not become a second authoritative writer of a
  control the engine or a player already owns.

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `controller` | a hardware device (`Controller`) | a `ControlObject` value (arch-control-messaging) |
| `mapping` | device→control binding (XML+JS) | a memory mapping / mmap |
| `deck` | a mapping's logical deck target | a `Deck` player object (arch-mixer-decks) |
| `soft takeover` | pickup logic to avoid value jumps | audio soft-start / fade |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| out | scripted control writes | arch-control-messaging | `ControlObjectScript` (QJSEngine) | — |
| in | control values for LED/output feedback | arch-control-messaging | `ControlProxy` connections | — |
| in | mapping definitions | (resources) | `res/controllers/` XML + JS | — |

## Key patterns (cited, not restated)
`P-29`, `P-30`, `AP-15`, `P-06`, `AP-03`, `P-17`, `P-20` — see `kanban/patterns/`. Root house rules:
`/AGENTS.md`. The `ControlObject`-only rule (`P-30`) is what keeps arbitrary device JS off the RT path.

---
id: arch-control-messaging
type: ddd-bounded-context
title: "control-messaging — the cross-thread string-keyed control bus"
owns:
  - src/control/                # ControlObject, ControlProxy, ControlValue, ControlPushButton, ControlPotmeter, ControlObjectScript, PollingControlProxy
exclude: []
thread_domain: any
rt_safety: soft
subdomain: core
upstream: []
downstream: [arch-engine-realtime, arch-mixer-decks, arch-controllers-mapping, arch-skin-widgets, arch-qml-ui]
maturity: hardened
fork_delta: upstream-tracking
agents_md: src/control/AGENTS.md
last_audited: "2026-07-17"
---

# control-messaging — bounded context

The string-keyed value bus every other context talks through. A `[Group],key` names one atomic
`double` any thread can read and a single writer owns; readers take a `ControlProxy`, writers hold the
`ControlObject`. It is how the GUI, controllers, and the RT engine exchange state **without** sharing
locks. `rt_safety: soft` — the read/write of a value is RT-callable (lock-free atomic), but object
lifecycle (construction, connection, alias) is not. Pointers, never copies — `src/control/` is the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `ControlObject` | `control/controlobject.cpp` | the authoritative value for one `ConfigKey` (`[Group],key`) |
| `ControlDoublePrivate` | `control/control.cpp` | shared refcounted backing store behind every proxy/object |
| `ControlValueAtomic<T>` | `control/controlvalue.h` | lock-free store: atomic for lock-free T, ring buffer otherwise |
| `ControlProxy` | `control/controlproxy.cpp` | a reader/notifier handle onto a `ControlObject` |
| `PollingControlProxy` | `control/pollingcontrolproxy.h` | signal-free proxy for polling reads (e.g. RT) |
| `ControlPushButton` | `control/controlpushbutton.cpp` | toggle/trigger behaviour over a ControlObject |
| `ControlPotmeter` | `control/controlpotmeter.cpp` | ranged knob/fader behaviour (lin/log/audio-taper) |
| `ControlObjectScript` | `control/controlobjectscript.cpp` | proxy exposed to the controller QJSEngine |

## Invariants (an agent MUST respect these)
- **Single writer (`P-06`/`AP-03`):** exactly one component is the authoritative writer of a given
  `[Group],key`. A second writer is the named antipattern; add a new key or route through the owner.
- **Read via proxy, not by grabbing the object:** cross-context readers hold a `ControlProxy` /
  `PollingControlProxy`; they never assume ownership of the `ControlObject`.
- **Value path is lock-free (`P-16`):** the `ControlValueAtomic` store is what makes a control safe to
  read on the audio thread; the *object graph* (create/connect/destroy) is GUI/worker-thread only (`P-17`).
- **Qt affinity (`P-20`):** proxies are QObjects; connect/emit respect thread affinity — no synchronous
  `Qt::DirectConnection` delivery onto the RT thread.

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `control` | one `[Group],key` atomic value + its behaviour | a hardware "control" input (arch-controllers-mapping) |
| `ConfigKey` | the `[Group],item` string identifier | a preferences config value (arch-preferences) |
| `proxy` | a `ControlProxy` read/notify handle | a network proxy (arch-audio-io network device) |
| `writer` | the single authoritative owner of a key | any component that merely reads it |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| out | `[ChannelN],*` values read on RT | arch-engine-realtime | ControlObject atomics | boundaries/control-to-engine.md |
| out | deck/player state (`[ChannelN],play` …) | arch-mixer-decks | ControlProxy / ControlObject | boundaries/control-to-engine.md |
| out | scriptable controls | arch-controllers-mapping | `ControlObjectScript` (QJSEngine) | — |
| out | widget/QML bindings | arch-skin-widgets, arch-qml-ui | `ControlProxy` connections | — |

## Key patterns (cited, not restated)
`P-06`, `AP-03`, `P-16`, `P-17`, `P-20` — see `kanban/patterns/`. Root house rules: `/AGENTS.md`.
This context is the reference implementation of the single-writer rule the whole map depends on.

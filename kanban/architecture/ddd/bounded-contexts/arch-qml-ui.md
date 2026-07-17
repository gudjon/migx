---
id: arch-qml-ui
type: ddd-bounded-context
title: "qml-ui — the new Qt Quick interface and its C++ proxies"
owns:
  - src/qml/                    # QmlApplication, QmlControlProxy, QmlPlayerProxy, QmlWaveformDisplay, model proxies
  - res/qml/                    # the Qt Quick UI: Deck.qml, Mixer.qml, EffectUnit.qml, Library, Theme, main.qml
exclude: []
thread_domain: gui
rt_safety: none
subdomain: supporting
upstream: [arch-control-messaging, arch-waveform-render, arch-rendergraph]
downstream: []
maturity: developing
fork_delta: migx-new
agents_md: src/qml/AGENTS.md
last_audited: "2026-07-17"
---

# qml-ui — bounded context

The new Qt Quick user interface. `QmlApplication` boots the QML engine and registers a set of C++ proxy
objects — `QmlControlProxy` (a `[Group],key` binding), `QmlPlayerProxy`, `QmlEffectsManagerProxy`,
`QmlLibraryProxy`, `QmlWaveformDisplay` — that the `.qml` files in `res/qml/` (`Deck.qml`, `Mixer.qml`,
`EffectUnit.qml`, the `Library` and `Theme` modules) bind against. It is GUI-thread Qt Quick code
(`rt_safety: none`); it renders through the Qt scene graph (arch-rendergraph) and reaches the engine only
through the control bus and proxies. This is Migx-new UI work (`fork_delta: migx-new`). Pointers, never
copies — `src/qml/` + `res/qml/` are the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `QmlApplication` | `qml/qmlapplication.cpp` | boots the QML engine; registers proxies/types |
| `QmlControlProxy` | `qml/qmlcontrolproxy.cpp` | QML-facing `[Group],key` control binding |
| `QmlPlayerProxy` | `qml/qmlplayerproxy.cpp` | QML-facing deck/player state |
| `QmlPlayerManagerProxy` | `qml/qmlplayermanagerproxy.cpp` | QML access to `PlayerManager` |
| `QmlEffectsManagerProxy` | `qml/qmleffectsmanagerproxy.cpp` | QML access to the effects model |
| `QmlLibraryProxy` | `qml/qmllibraryproxy.cpp` | QML library/track-list access |
| `QmlWaveformDisplay` | `qml/qmlwaveformdisplay.cpp` | Qt Quick waveform item |
| `Deck.qml` / `Mixer.qml` | `res/qml/Deck.qml`, `res/qml/Mixer.qml` | deck / mixer UI components |
| `main.qml` | `res/qml/main.qml` | root QML scene |

## Invariants (an agent MUST respect these)
- **GUI-thread only (`P-20`/`AP-14`):** proxies are QObjects on the GUI/QML thread; they read the control
  bus and must never be touched from or block the audio callback.
- **Reach the engine only via ControlObject / proxies (`P-06`/`P-30`):** QML binds `QmlControlProxy` and
  the typed proxies; it never calls engine internals or becomes a rogue second writer of a control (`AP-03`).
- **QObject ownership rule holds through QML (`P-19`/`AP-13`):** C++-owned proxy/model objects handed to
  QML follow the parent/`qml_owned_ptr` ownership contract.
- **Rendering runs on the scene graph, not the audio clock (`P-21`/`P-23`):** `QmlWaveformDisplay` draws
  via arch-rendergraph on the display clock; it never gates or is gated by the audio deadline.

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `proxy` | a `Qml*Proxy` C++ bridge to QML | a `ControlProxy` (though it wraps one) |
| `component` | a `.qml` UI element | a bounded context / architectural component |
| `theme` | the `res/qml/Theme` styling module | a legacy skin colour scheme (arch-skin-widgets) |
| `model` | a QML list model proxy | a library `BaseSqlTableModel` (arch-library-db) |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| in | control values | arch-control-messaging | `QmlControlProxy` over `ControlProxy` | — |
| in | waveform playhead / rendering | arch-waveform-render | `QmlWaveformDisplay` | boundaries/engine-to-waveform.md |
| in | scene-graph draw | arch-rendergraph | Qt Quick scene graph (RHI) | — |

## Key patterns (cited, not restated)
`P-20`, `AP-14`, `P-06`, `P-30`, `AP-03`, `P-19`, `AP-13`, `P-21`, `P-23` — see `kanban/patterns/`. Root
house rules: `/AGENTS.md`. As `migx-new` UI, this context is where the QML replacement for the legacy skin grows.

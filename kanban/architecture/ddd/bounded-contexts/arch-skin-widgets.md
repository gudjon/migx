---
id: arch-skin-widgets
type: ddd-bounded-context
title: "skin-widgets — the legacy QWidget skin engine and control widgets"
owns:
  - src/skin/                   # SkinLoader, LegacySkinParser, SkinContext — XML skin → widget tree
  - src/widget/                 # WWidget and the WPushButton/WKnob/WWaveformViewer/WOverview widget family
exclude: []
thread_domain: gui
rt_safety: none
subdomain: supporting
upstream: [arch-control-messaging, arch-waveform-render]
downstream: []
maturity: hardened
fork_delta: upstream-tracking
agents_md: src/skin/AGENTS.md
last_audited: "2026-07-17"
---

# skin-widgets — bounded context

The legacy QWidget user interface. `SkinLoader` picks a skin and `LegacySkinParser` walks its XML to
build a tree of `WWidget` subclasses — `WPushButton`, `WKnob`, `WSliderComposed`, `WOverview`,
`WWaveformViewer`, `WSpinny` — each bound to a `ControlObject` through a `ControlWidgetConnection`. It is
GUI-thread Qt code (`rt_safety: none`); it reads/writes the control bus and embeds the waveform viewers,
but never touches the audio thread. This is the classic UI; the Qt Quick replacement is arch-qml-ui.
Pointers, never copies — `src/skin/` + `src/widget/` are the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `SkinLoader` | `skin/skinloader.cpp` | resolves and loads the active skin |
| `LegacySkinParser` | `skin/legacy/legacyskinparser.cpp` | parses skin XML into the widget tree |
| `SkinContext` | `skin/legacy/skincontext.cpp` | parse-time variable/context resolution |
| `WWidget` | `widget/wwidget.cpp` | base skinnable widget (`WBaseWidget`) |
| `WPushButton` / `WKnob` | `widget/wpushbutton.cpp`, `widget/wknob.cpp` | button / knob control widgets |
| `WSliderComposed` | `widget/wslidercomposed.cpp` | composed fader/slider widget |
| `WWaveformViewer` | `widget/wwaveformviewer.cpp` | embeds a waveform renderer in a skin |
| `WOverview` | `widget/woverview.cpp` | full-track overview widget |
| `ControlWidgetConnection` | `widget/controlwidgetconnection.cpp` | binds a widget to a `ControlObject` value |

## Invariants (an agent MUST respect these)
- **GUI-thread only, never the RT path (`P-20`/`AP-14`):** widgets are QObjects on the GUI thread; they
  read controls via proxy and must never be touched from or block the audio callback.
- **Every QObject gets a parent before its `parented_ptr` destructs (`P-19`/`AP-13`):** the skin builds a
  Qt object tree; widget ownership follows the parent-tree rule.
- **Widgets bind through `ControlWidgetConnection`, not raw control writes (`P-06`):** a widget is a
  reader/UI writer of a `[Group],key`; it does not become a rogue second authoritative writer (`AP-03`).
- **Waveform drawing is delegated (`P-21`):** `WWaveformViewer` hosts the render context; it does not
  drive drawing off the audio period.

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `skin` | an XML-defined QWidget layout | a QML `Theme`/skin (arch-qml-ui) |
| `widget` | a `WWidget` UI element | a `waveform/widgets` render widget (arch-waveform-render) |
| `connection` | a `ControlWidgetConnection` binding | a Qt signal/slot connection generally |
| `overview` | the `WOverview` full-track bar | the per-deck scrolling waveform |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| in | control values for display/input | arch-control-messaging | `ControlProxy` via `ControlWidgetConnection` | — |
| in | embedded waveform rendering | arch-waveform-render | `WWaveformViewer` hosts a renderer | boundaries/engine-to-waveform.md |

## Key patterns (cited, not restated)
`P-20`, `AP-14`, `P-19`, `AP-13`, `P-06`, `AP-03`, `P-21` — see `kanban/patterns/`. Root house rules:
`/AGENTS.md`. Qt object-tree ownership (`P-19`) is the load-bearing rule for anything building the skin tree.

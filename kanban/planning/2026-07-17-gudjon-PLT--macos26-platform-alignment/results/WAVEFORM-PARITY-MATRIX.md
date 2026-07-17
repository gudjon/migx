---
id: waveform-parity-matrix-plt-w3
type: evidence
title: "Waveform feature parity — allshader vs deprecated (NO DELETE)"
dossier: 2026-07-17-gudjon-PLT--macos26-platform-alignment
status: draft-signed-for-hold
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# Wave 3 — Waveform parity matrix (gate before any GL delete)

**Rule:** Zero files deleted from `src/waveform/**/deprecated/` until every **KEEP** row is
proven on **allshader/RHI** and live base-class deps are rewired (`retire-deprecated-gl-waveform-renderers`).

## Live dependencies that block bulk delete

| File | Includes from deprecated/ | Role |
|---|---|---|
| `src/waveform/renderers/glwaveformrenderbackground.h:5` | `deprecated/glwaveformrenderer.h` | **ACTIVE** base |
| `src/waveform/widgets/glwaveformwidgetabstract.h:3` | `deprecated/glwaveformrenderer.h` | **ACTIVE** base |
| `src/waveform/renderers/glvsynctestrenderer.h:3` | `deprecated/glwaveformrenderersignal.h` | **ACTIVE** + factory-registered widget |

Naive `git rm -r deprecated/` **does not build** (agy attempt 2026-07-17).

## Feature matrix

| Feature / surface | allshader | deprecated GL | Qt software widgets | Default today | Parity status |
|---|---|---|---|---|---|
| RGB waveform | `WaveformRendererRGB` | `glwaveformrendererrgb` | `qtrgbwaveformwidget` | **allshader RGB** | allshader primary |
| Filtered | `WaveformRendererFiltered` | `glwaveformrendererfilteredsignal` | `softwarewaveformwidget` | allshader avail | OK |
| HSV | `WaveformRendererHSV` | — | `hsv` / `qthsv` | OK | OK |
| Simple signal | `WaveformRendererSimple` | `glwaveformrenderersimplesignal` | `simplesignal` / `qtsimple` | OK | OK |
| Textured | `WaveformRendererTextured` | GLSL path | — | allshader | OK |
| Stem layers | `WaveformRendererStem` | — | — | allshader | **KEEP — no deprecated equivalent** |
| Beats | `WaveformRenderBeat` | via base stacks | yes | allshader | verify visual |
| Marks / hotcues | `WaveformRenderMark` | via widgets | yes | allshader | verify visual |
| Mark ranges | `WaveformRenderMarkRange` | — | — | allshader | verify visual |
| Background | `WaveformRenderBackground` | `glwaveformrenderbackground` (active header) | — | mixed | **HOLD** base class |
| End of track | `WaveformRendererEndOfTrack` | — | — | allshader | OK |
| Preroll | `WaveformRendererPreroll` | — | — | allshader | OK |
| Slip mode | `WaveformRendererSlipMode` | — | — | allshader | verify visual |
| Digits overlay | `digitsrenderer` | — | — | allshader | OK |
| VSync test widget | — | `GLVSyncTestWidget` **registered** | `qtvsynctest` | debug | **HOLD** until rewire |
| Empty widget | `emptywaveformwidget` | — | — | OK | OK |

## Inventory counts (HEAD)

| Tree | Contents (approx) |
|---|---|
| `renderers/allshader/` | RGB, Filtered, HSV, Simple, Textured, Stem, Beat, Mark*, Background, EOT, Preroll, Slip, digits, matrix helpers |
| `renderers/deprecated/` | gl base, RGB, filtered, simple, glsl signal |
| `widgets/allshader/` | (present) |
| `widgets/deprecated/` | gl/rgb/simple/glsl widgets + qt* legacy |

## Delete checklist (future UIX dossier — **not this wave**)

1. Promote `glwaveformrenderer.h` + `glwaveformrenderersignal.h` out of `deprecated/` **or** rewire 3 includers.  
2. Unregister or rehome `GLVSyncTestWidget` in `waveformwidgetfactory.cpp`.  
3. Update CMakeLists for removed sources.  
4. `cmake --build` + `ctest -R Waveform` green.  
5. Visual dogfood: cues, loops, stems, overview, RGB/Filtered/HSV.  
6. Only then delete dead widgets.

## Gate decision (Wave 3 this dossier)

| Criterion | Result |
|---|---|
| Parity matrix written | **YES** |
| Live deps documented | **YES** |
| Any `deprecated/` file deleted | **NO** (correct) |
| Ready to delete | **NO — HOLD** |

Signed for HOLD: 2026-07-17 · PLT Wave 3 prep complete.

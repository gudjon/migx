---
id: MTL-copy-map
type: evidence
title: "Per-frame CPU↔GPU copy map — waveform render path (rendergraph_gl)"
dossier: 2026-07-17-gudjon-MTL--waveform-render-baseline
status: complete
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# Copy-map — waveform render path (Wave 4)

Every per-frame CPU↔GPU data movement on the default QWidget-skin waveform path (`rendergraph_gl`),
confirmed at HEAD (`2332debe`). This is the input the **zero-copy / Metal optimization dossier** consumes.
The `EVD-0001` baseline (~34–39µs CPU rebuild/frame) is the cost of steps 1–2 below.

## The per-frame hot path (runs every vsync, per deck)

| # | What happens | Where (file:line) | Cost class | Optimization |
|---|---|---|---|---|
| 1 | **Full CPU vertex rebuild** — scalar per-pixel min/max reduction over ~264k `WaveformData` points rewrites the entire vertex buffer, then `geometry().allocate()` + `markDirtyGeometry()` | `src/waveform/renderers/allshader/waveformrendererrgb.cpp:29-37` (`preprocessInner`); same shape in `waveformrendererfiltered.cpp`, `waveformrendererhsv.cpp` | CPU (the EVD-0001 ~34–39µs) | incremental/dirty-region rebuild; SIMD the reduction (NEON/Accelerate); or a compute shader |
| 2 | **No-VBO client-side vertex bind → full GPU upload** — `setAttributeArray(loc, geometry.vertexDataAs<float>() + off, …)` binds **client memory**; `glDrawArrays` forces the driver to copy the whole vertex buffer CPU→GPU **every draw** | `src/rendergraph/opengl/backend/basegeometrynode.cpp:89-90`, `:102` | CPU→GPU copy/frame (`AP-12`) | **persistent VBO** (upload once, update dirty range); `P-22` zero-copy — this is the headline win |

## Not per-frame (already cached — leave alone)
| What | Where | Note |
|---|---|---|
| Mark/beat/label textures | `waveformrendermark.cpp:49,485` `updateTexture()` | uploaded via `QImage`→texture only on (re)generation, not per frame |
| Texture premultiply/upload | `src/rendergraph/opengl/texture.cpp` | exercised on mark/label regen only |

## Contrast — the SceneGraph path already avoids this
`src/rendergraph/scenegraph/backend/basegeometrynode.h` (`using BaseGeometryNode = QSGGeometryNode`)
delegates to Qt Quick's renderer, which **does** use GPU buffers. So the QML/SceneGraph path already
has the optimization the QWidget path (`rendergraph_gl`) lacks — a second lever for the optimization
dossier (adopt SceneGraph + let Qt pick Metal, gated on the forced-OpenGL/offscreen constraint from
`coreservices.cpp:826`).

## The two levers for the optimization dossier
1. **VBOs in the GL backend** (`basegeometrynode.cpp`) — persistent buffer, upload dirty range only (`P-22`).
2. **Adopt the SceneGraph backend + Metal RHI** — bigger, gated on solving offscreen-render-on-Metal.
Both measure their delta against `EVD-0001`.

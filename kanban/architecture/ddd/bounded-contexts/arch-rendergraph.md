---
id: arch-rendergraph
type: ddd-bounded-context
title: "rendergraph — the Qt-scenegraph/RHI abstraction and shaders (Metal north-star)"
owns:
  - src/rendergraph/            # common/, opengl/, scenegraph/ — node/geometry/material abstraction over Qt RHI + GL
  - src/shaders/                # Shader, RGBAShader, TextureShader, EndOfTrackShader, … — GLSL program wrappers
exclude: []
thread_domain: gpu-render
rt_safety: none
subdomain: supporting
upstream: []
downstream: [arch-waveform-render, arch-qml-ui]
maturity: developing
fork_delta: migx-divergent
agents_md: src/rendergraph/AGENTS.md
last_audited: "2026-07-17"
---

# rendergraph — bounded context

The low-level GPU abstraction the waveforms and QML visuals build on. It offers a small scene model —
nodes, `Geometry`, `Material`, `MaterialShader`, `AttributeSet` — with two backends: a `scenegraph/`
implementation over **Qt RHI** (`BaseMaterialShader : QSGMaterialShader`, so on macOS the GPU path is
Metal *via* RHI) and an `opengl/` implementation for the legacy widget path. `src/shaders/` holds the
GLSL program wrappers. There is **no direct Metal path today** — the Apple-Silicon Metal north-star work
lands here, which is why this context is `migx-divergent`. It is GPU/render-thread code
(`rt_safety: none`). Pointers, never copies — `src/rendergraph/` + `src/shaders/` are the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `rendergraph::BaseMaterialShader` | `rendergraph/scenegraph/backend/basematerialshader.cpp` | RHI material shader (`QSGMaterialShader`) |
| `rendergraph::BaseMaterial` | `rendergraph/scenegraph/backend/basematerial.cpp` | scenegraph material base |
| opengl `Engine` / `MaterialShader` | `rendergraph/opengl/engine.cpp`, `materialshader.cpp` | GL backend engine + shader |
| `Geometry` / `GeometryNode` | `rendergraph/*/geometry.cpp`, `geometrynode.cpp` | vertex geometry + draw node |
| `AttributeSet` | `rendergraph/*/attributeset.cpp` | vertex attribute layout |
| `Shader` | `shaders/shader.cpp` | base GLSL program wrapper |
| `RGBAShader` / `TextureShader` | `shaders/rgbashader.cpp`, `textureshader.cpp` | color / textured program wrappers |
| `EndOfTrackShader` | `shaders/endoftrackshader.cpp` | end-of-track visual program |

## Invariants (an agent MUST respect these)
- **GPU work never gates the audio deadline (`P-21`/`AP-02`):** this context is off the audio path
  entirely; nothing here may block or feed back into `process()`.
- **Keep data in GPU buffers across frames (`P-22`/`AP-12`):** geometry/textures upload once and persist;
  no per-frame CPU→GPU re-copy in the draw hot path — the primary target of the Metal perf work.
- **Backend-neutral scene model:** callers build nodes/materials against the abstraction; the RHI
  (Metal/Vulkan/D3D) vs GL choice is Qt's, not baked into call sites.
- **Perf work needs a benchmark contract (`P-03`/`P-18`):** a Metal/RHI speedup is proven with frame-time
  tail metrics on pinned hardware, not a mean, and must not regress visual correctness (`AP-02`).

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `node` | a scene-graph draw node (`GeometryNode`) | a `[Group],key` control (arch-control-messaging) |
| `material` / `shader` | GPU program + its parameters | an audio effect/DSP (arch-effects-chain) |
| `RHI` | Qt's Rendering Hardware Interface (→ Metal on macOS) | a direct Metal API layer (does not exist yet) |
| `backend` | scenegraph (RHI) vs opengl impl | an effects/audio-device backend |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| out | scene nodes / materials / shaders | arch-waveform-render | node + material draw API | — |
| out | QML scene-graph integration | arch-qml-ui | Qt Quick scene graph (RHI) | — |

## Key patterns (cited, not restated)
`P-21`, `P-22`, `AP-12`, `AP-02`, `P-03`, `P-18` — see `kanban/patterns/`. Root house rules: `/AGENTS.md`.
North-star Metal-on-Apple-Silicon work is governed here by the GPU-buffer (`P-22`) and benchmark (`P-18`) rules.

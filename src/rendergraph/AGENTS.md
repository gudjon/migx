# AGENTS.md — rendergraph/ (Qt-scenegraph/RHI abstraction; shaders in src/shaders/)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-rendergraph.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
The low-level GPU abstraction the waveforms and QML visuals build on: a small scene model — nodes,
`Geometry`, `Material`, `MaterialShader`, `AttributeSet` — with two backends. `scenegraph/` runs over
**Qt RHI** (`BaseMaterialShader : QSGMaterialShader`, so on macOS the GPU path is Metal *via* RHI);
`opengl/` is the legacy widget path. `src/shaders/` holds the GLSL program wrappers. There is **no direct
Metal path today** — the Apple-Silicon Metal north-star work lands here.

## Key files
- `scenegraph/backend/basematerialshader.cpp/.h` — RHI material shader (`QSGMaterialShader`).
- `scenegraph/backend/basematerial.cpp`, `scenegraph/geometry.cpp`, `scenegraph/geometrynode.cpp` — scene model.
- `opengl/engine.cpp`, `opengl/materialshader.cpp`, `opengl/geometry.cpp` — the GL backend.
- `common/` — shared `types.cpp` and headers.
- `../shaders/shader.cpp`, `../shaders/rgbashader.cpp`, `../shaders/textureshader.cpp`,
  `../shaders/endoftrackshader.cpp`, … — GLSL program wrappers.

## Invariants you MUST respect
- **GPU work never gates the audio deadline:** this context is off the audio path entirely; nothing here
  may block or feed back into `process()`. `P-21`, `AP-02`.
- **Keep data in GPU buffers across frames:** geometry/textures upload once and persist; no per-frame
  CPU→GPU re-copy in the draw hot path — the primary target of the Metal perf work. `P-22`, `AP-12`.
- **Backend-neutral scene model:** callers build nodes/materials against the abstraction; the RHI
  (Metal/Vulkan/D3D) vs GL choice is Qt's, not baked into call sites.
- **Perf work needs a benchmark contract:** a Metal/RHI speedup is proven with frame-time tail metrics on
  pinned hardware, not a mean, and must not regress visual correctness. `P-03`, `P-18`, `AP-02`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R "Rendergraph|Shader"` (GoogleTest; `src/test/`).
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Blocking on or synchronizing GPU work with the audio callback (`P-21`, `AP-02`).
- Introducing a per-frame CPU→GPU round-trip in the draw hot path (`P-22`, `AP-12`).
- Baking a specific graphics API into call sites instead of going through the backend-neutral model.

## Cross-references
Downstream: `src/waveform/AGENTS.md` (renderers), `src/qml/AGENTS.md` (Qt Quick scene graph). North-star:
`kanban/initiatives/initiative-apple-silicon.md`. Card:
`kanban/architecture/ddd/bounded-contexts/arch-rendergraph.md`.

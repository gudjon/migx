# Research

## Upstream (Mixxx) changelog scan
The `rendergraph` abstraction (common + `opengl`/`scenegraph` backends) is inherited from upstream Mixxx.
Upstream's OpenGL backend `BaseGeometryNode::render()` uses the same client-memory `setAttributeArray` +
`glDrawArrays` path (no VBO) — confirmed at fork HEAD `e099d24ac8`. The **scenegraph** backend already
gets GPU buffers for free via Qt Quick's renderer (it only re-uploads on `DirtyGeometry`). So the GL
backend is the laggard; this PS brings it in line with what the scenegraph path already does. No upstream
in-flight VBO change was relied upon — this is a fork-local optimization (`ADR-002`).

## Prior art
Persistent VBOs vs client-side vertex arrays is textbook OpenGL: client arrays force the driver to copy
the whole array at draw time; a buffer object lives in GPU (or driver-pinned) memory and is re-uploaded
only when changed. On Apple Silicon, OpenGL runs on top of Metal (unified memory), so the client-array
marshaling per draw is pure overhead a VBO avoids. `DYNAMIC_DRAW` + buffer orphaning (`glBufferData(…,
nullptr)` before refill) is the standard idiom to avoid a GPU/CPU sync stall when the same buffer is
re-uploaded each frame. Qt exposes both paths via `QOpenGLShaderProgram::setAttributeArray` (client) vs
`setAttributeBuffer` (bound VBO).

## Options considered
| Option | Pros | Cons | Verdict |
|---|---|---|---|
| A. Persistent VBO, dirty-tracked (chosen) | zero copy on unchanged frames; minimal, in the existing backend; respects the abstraction | still uploads on changing frames; needs a dirty signal | **chosen** — smallest correct win, copy-map lever 1 |
| B. Persistent-mapped / `GL_MAP_PERSISTENT_BIT` buffer | avoids re-specification | GL 4.4+; macOS GL caps at 4.1 — unavailable | rejected (unsupported) |
| C. Adopt SceneGraph + Metal RHI | biggest structural win; Qt-managed buffers | gated on offscreen-render-on-Metal (`coreservices.cpp:826` forces GL); large | out of scope (copy-map lever 2) |
| D. Incremental/SIMD CPU rebuild | attacks the ~39µs EVD-0001 cost | orthogonal to the GPU copy; separate PS | out of scope (copy-map lever 1-CPU) |

## Baseline measurement (trigger/capture for MG-1)
`EVD-0001` (baseline dossier): RGB per-frame CPU vertex rebuild ~39µs floor / ~45µs p50; the client-array
copy it feeds re-uploads ~450 KB/frame/deck at the reference scene. Pinned commit `2332debe`. This
dossier's `EVD-0002` measures the delta on the same M4 host.

## Open questions
- Exact end-to-end frame-time win (upload + shade + draw + composite) — needs the GUI; deferred to human
  verification, not blocking the structural change.
- Whether active-scrubbing frames also net a win (explicit orphaned upload vs implicit client copy) —
  plausible but not isolated here; a future GL render-loop bench (copy-map Phase B) could quantify it.

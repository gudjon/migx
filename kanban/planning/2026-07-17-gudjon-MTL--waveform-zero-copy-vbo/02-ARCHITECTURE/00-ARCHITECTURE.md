# Architecture

Not path-pinning enough to need a new ADR — it's an in-place implementation of the existing
`rendergraph_gl` backend, authorized by `ADR-002` (TRUE HARD FORK). Cites `P-22`.

## The design
Give each `rendergraph::BaseGeometryNode` (OpenGL backend) a **persistent `GL_ARRAY_BUFFER`** and a dirty
flag:

```
BaseGeometryNode {
  GLuint m_vboId = 0;      // lazily glGenBuffers() on first render()
  int    m_vboByteSize = 0;
  bool   m_geometryDirty = true;   // starts dirty → first frame always uploads
  void   markGeometryDirty();      // set by GeometryNode::markDirtyGeometry()
}
```

`render()` becomes:
1. lazily create the buffer (`glGenBuffers`), bind it.
2. if `m_geometryDirty || vertexBytes != m_vboByteSize`: upload —
   - size changed → `glBufferData(size, data, GL_DYNAMIC_DRAW)` (reallocate + fill);
   - same size → `glBufferData(size, nullptr, …)` (orphan) + `glBufferSubData(0, size, data)`;
   then clear the dirty flag.
3. bind attributes with `setAttributeBuffer(loc, GL_FLOAT, offsetBytes, tuple, stride)` — offsets into
   the bound VBO, **not** client pointers.
4. `glDrawArrays` (now sources from GPU memory), then `glBindBuffer(0)` to restore state.

The dirty signal is the existing `GeometryNode::markDirtyGeometry()` (previously a no-op in the GL
backend). **Unchanged frame ⇒ dirty flag false ⇒ no upload ⇒ zero copy** (`P-22`).

## Touched subsystems & the RT/GPU boundary
Only `src/rendergraph/opengl/` (backend node + geometrynode) and the bench in `src/test/`. **Nothing in
`src/engine/` or any audio callback.** The change is strictly on the render (GUI/display-clock) thread —
`P-21`/`P-23`: GPU work stays off the audio deadline; `P-02`: no allocation/lock added to the RT path.
GL resources are created/updated/freed only with a current context on the render thread.

## Patterns & decisions cited
| ID | How this design uses it |
|---|---|
| `P-22` zero-copy-gpu-waveform | the goal: unchanged geometry draws with no CPU→GPU copy |
| `AP-12` gpu-cpu-copy-in-render-hot-path | the antipattern being removed (per-draw client-array copy) |
| `P-21` metal-offload-deadline | GPU buffer work stays on the render thread, off the audio deadline |
| `P-03`/`P-18` benchmark-as-contract | EVD-0002 is the numeric contract; report floor/p50, not the tail |
| `ADR-002` TRUE HARD FORK | authorizes editing the vendored render backend in place |

## Data journey
`WaveformData` (CPU) → per-pixel min/max reduction → `Geometry` client vertex buffer (CPU, the
EVD-0001 ~39µs rebuild — unchanged by this PS) → **[here]** persistent VBO (GPU) → shader → framebuffer.
The eliminated copy is the client-buffer→GPU hop, which the old path re-did every `glDrawArrays`; now it
happens only when the CPU buffer actually changed (`markDirtyGeometry`).

## Risks
- **Stale VBO if a renderer mutates geometry without `markDirtyGeometry()`.** Mitigated: audited 12/12
  allshader renderers call it; it is the *same* contract the scenegraph backend already enforces
  (`markDirty(QSGNode::DirtyGeometry)`), so any violator is already broken on QML. Belt-and-braces: a
  vertex-count change forces an upload regardless of the flag, and the flag starts `true`.
- **GL buffer leak / delete-without-context.** Mitigated: destructor deletes only when
  `QOpenGLContext::currentContext()` is live; otherwise the owning context is gone and already reclaimed
  the buffer.
- **Scenegraph backend regression.** None — that backend (`src/rendergraph/scenegraph/`) is untouched.

## Verifiability
`ctest -R 'Waveform|Engine'` (correctness) + `BM_Waveform` (CPU rebuild unchanged) + `BM_WaveformVboUpload`
(eliminated upload cost) → `EVD-0002`. Visual correctness + end-to-end frame time = human GUI check
(headless can't see pixels).

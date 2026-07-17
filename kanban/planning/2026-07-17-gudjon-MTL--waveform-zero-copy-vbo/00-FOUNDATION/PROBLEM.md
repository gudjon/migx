# Problem

## What's wrong today
On the default QWidget-skin waveform path (`allshader::WaveformWidget` → `rendergraph_gl` backend), the
GL node's `render()` binds the vertex buffer as **client memory** (`setAttributeArray`) and calls
`glDrawArrays`. With no VBO bound, the OpenGL driver copies the **whole** vertex buffer CPU→GPU on
**every** draw — every vsync, for every deck — regardless of whether the waveform actually changed. On
Apple Silicon, where OpenGL runs on top of Metal, that per-draw marshaling is pure overhead. This is
`COPY-MAP.md` step 2 / antipattern `AP-12`, and the target of pattern `P-22` (zero-copy GPU waveform).

At the reference scene the baseline dossier pinned (1920×200 Retina deck, DPR 2.0, default zoom), the
per-frame vertex buffer is ~450 KB. The old path re-uploads all of it every frame; the biggest waste is
the **idle case** — a loaded but paused deck, or a static display window, still redraws every vsync and
re-copies a buffer that is byte-for-byte identical to the one already on the GPU.

## Who feels it
A DJ on an M4 MacBook with several decks + overview waveforms loaded: each visible waveform node spends
render-thread time every vsync re-copying vertices to the GPU even when nothing moved. It never blocks
audio (render thread, off the audio deadline — `P-21`/`P-23`), but it burns render-thread budget and
battery, and it scales with deck count and Retina pixel width.

## What "done" means (the bet)
1. **The problem is real** — `EVD-0001` (baseline dossier) pins the ~39µs CPU rebuild that feeds this
   draw; the copy-map identifies the per-draw client-memory upload (`basegeometrynode.cpp:89-102`) as the
   redundant GPU copy. `EVD-0002` measures the per-frame upload cost that copy represents (~6.5µs floor
   for 450 KB).
2. **The approach works** — replace the client-memory bind with a **persistent VBO**: upload the vertex
   data to a GL buffer object once, re-upload only when the geometry is marked dirty, and draw straight
   from GPU memory. An unchanged frame does **zero** upload.
3. **The gates catch failure** — `ctest -R 'Waveform|Engine'` (correctness), `BM_Waveform` (CPU rebuild
   unchanged), `BM_WaveformVboUpload` (the eliminated upload cost, quantified).

## Non-goals
- Making the CPU vertex rebuild incremental/SIMD (copy-map lever 1 — separate PS).
- Adopting SceneGraph + Metal RHI (copy-map lever 2 — gated on offscreen-render-on-Metal).
- Claiming an end-to-end frame-time win that headless measurement can't see — that needs the GUI and is
  flagged for human verification.

## Inheritance
- `P-22` zero-copy-gpu-waveform (resolves), `AP-12` gpu-cpu-copy-in-render-hot-path (the risk being paid).
- `P-21` metal-offload-deadline (GPU off the audio deadline), `P-02` RT-safety (this is the render
  thread — invariant preserved by not touching the audio path).
- `P-03`/`P-18` benchmark-as-contract / p99-not-mean; `P-01` honest measurement.
- Baseline dossier `2026-07-17-gudjon-MTL--waveform-render-baseline` — `EVD-0001` + `COPY-MAP.md` are the
  direct inputs. `ADR-002` (TRUE HARD FORK) authorizes changing the render code in place.

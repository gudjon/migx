# Architecture — the measurement design

*This is a baseline (measurement) dossier, so the "architecture" is the benchmark harness, not a
product change. The design goal: a repeatable, low-overhead frame-time measurement of the real
waveform renderer that does not itself perturb what it measures.*

## The design
Drive the production `allshader` waveform renderer over N frames of a scripted **scrubbing scene** (a
loaded track, playhead moving across the buffer), timing each frame's GPU-facing render, and report the
distribution.

- **What to time:** the per-frame render cost of the waveform widget/renderer — the work between
  successive display-clock ticks (`guitick`/`vsyncthread`). Capture wall-clock per frame; derive
  p50/p99/max and count frames that exceed the display period (dropped-frame proxy).
- **Harness:** a GoogleTest/`benchmark::benchmark` case (follow `src/test/*` bench exemplars) or a small
  offscreen render loop if the renderer needs a live `QQuickWindow`/RHI context. Prefer offscreen so it
  runs in CI-like conditions; if a real GPU surface is required, document that it's a local-only bench.
- **Backend introspection:** record which QRhi/graphics backend is actually live at run time (expected
  OpenGL, per `coreservices.cpp:826`) + Qt version, into the `EVD-0001` record.

## Touched subsystems & the RT/GPU boundary
Read-only w.r.t. product code: `src/waveform/` (renderer, `waveformwidgetfactory`, `visualplayposition`,
`guitick`) and `src/rendergraph/` (`scenegraph/`, `opengl/`). The bench is **off the audio thread**; it
must not touch the RT path and must not add a per-frame CPU↔GPU round-trip that would bias the number
(`P-21`/`AP-12`). New code lives under the test/bench tree, not in the render hot path.

## Data journey to document (the deliverable a later dossier consumes)
Trace, at file:line: where waveform sample data becomes a GPU texture/buffer, where mark/label/beat
geometry is (re)built per frame, and any CPU readback. Note every copy — the future zero-copy MTL
dossier (`P-22`) starts from this map.

## Patterns & decisions cited
| ID | How this design uses it |
|---|---|
| `P-03`, `P-25` | benchmark contract; pin the baseline to a commit + M4 config |
| `P-18`, `AP-11` | report p99/max + dropped frames, never a mean |
| `P-23` | measure against the display clock, not the audio clock |
| `P-21`, `AP-12` | the bench must not gate audio or add per-frame copies |

## Verifiability
Two runs of the bench on the same commit agree within a stated tolerance (reproducibility is the
"threshold" for a baseline). The recorded `EVD-0001` + the copy-map are the closure evidence.

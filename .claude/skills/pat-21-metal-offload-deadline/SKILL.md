---
name: pat-21-metal-offload-deadline
description: "Surface the GPU-must-not-gate-audio rule when editing GPU/waveform rendering. Fire when
  touching src/rendergraph/, src/shaders/, waveform renderers, RHI/scenegraph code, or any GPU buffer/
  texture upload — especially anything reachable from or synchronizing with the audio callback. GPU
  work stays off the audio deadline, waveform data stays zero-copy in GPU buffers, and no per-frame
  GPU↔CPU round-trip."
disable-model-invocation: false
defers_to:
  - kanban/patterns/P-21-metal-offload-must-not-gate-audio.md
  - kanban/patterns/P-22-zero-copy-gpu-waveform.md
  - kanban/patterns/AP-12-gpu-cpu-copy-in-the-render-hot-path.md
audit_gate: "advisory — knowledge skill; TSan + render-profile checks in Phase 3"
verifiable_output_shape: "advisory — knowledge skill, no artifact"
metadata:
  cites_patterns: ["P-21", "P-22", "AP-12"]
---

# pat-21 — metal offload deadline

You are editing GPU/waveform rendering (rendergraph draws via Qt RHI/scenegraph — Metal via RHI, no
direct Metal path today). Surface
**[`P-21`](../../../kanban/patterns/P-21-metal-offload-must-not-gate-audio.md)** (GPU work never gates
the audio callback deadline) and
**[`P-22`](../../../kanban/patterns/P-22-zero-copy-gpu-waveform.md)** (waveform data stays in GPU
buffers across frames), and watch for the failure
**[`AP-12`](../../../kanban/patterns/AP-12-gpu-cpu-copy-in-the-render-hot-path.md)** (per-frame GPU↔CPU
copy). Read the cards; don't restate them.

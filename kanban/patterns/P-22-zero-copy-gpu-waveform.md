---
id: P-22
type: pattern
title: "Waveform data stays in GPU buffers across frames"
status: active
severity: SHOULD
domain: gpu
related: [P-21, P-23, AP-12]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-22 — Waveform data stays in GPU buffers across frames

## Statement
Waveform and texture data lives in GPU-accessible buffers that persist across frames. A redraw
uploads only what changed (the scroll delta, a new summary block) — it does not re-upload the whole
waveform or round-trip pixels GPU→CPU→GPU every frame.

## Why
Apple Silicon is a unified-memory architecture: CPU and GPU share the same physical RAM, so a
per-frame copy is pure waste — bandwidth, CPU time, and latency spent moving bytes that were already
addressable. Migx's rendergraph carries geometry/materials/textures as first-class objects
(`src/rendergraph/`) precisely so buffers can be built once and reused; re-uploading each frame throws
that away and is the most common way waveform rendering becomes the frame-time bottleneck (`AP-12`).

## How to apply
- Allocate the waveform's vertex/texture buffers once; update them incrementally as playback scrolls
  or the zoom changes, via the rendergraph geometry/texture objects.
- Compute waveform summaries off the render hot path and hand them to the GPU buffer with a bounded,
  partial update — not a full re-upload.
- Exploit unified memory: prefer shared/managed storage so a CPU-side write is visible to the GPU
  without an explicit staging copy where the backend allows it.
- Never read the framebuffer or a texture back to the CPU inside the per-frame path (`AP-12`).

## Example — wrong
```cpp
// Every frame: rebuild the entire waveform vertex array on the CPU and re-upload it.
buildAllVertices(track);                 // O(track length) each frame
texture->setData(fullPixmapFromCpu());   // full GPU upload per frame → bandwidth-bound
```

## Example — right
```cpp
// Persistent rendergraph geometry/texture; only the changed region is written this frame.
geometry->updateRange(firstDirty, lastDirty);   // partial, bounded update
// scroll handled by shader uniform, not by re-uploading vertices
```

## Detection
Profile: per-frame allocation or full buffer/texture upload in the waveform renderer; GPU counters
showing upload bandwidth scaling with track length rather than with the visible delta.

## Cross-references
Serves `P-21` (keeps the render cheap and off the audio deadline); pairs with `P-23`. The full-copy
failure is `AP-12`.

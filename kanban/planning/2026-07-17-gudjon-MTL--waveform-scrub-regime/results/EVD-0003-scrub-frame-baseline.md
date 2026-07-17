# EVD-0003 — active-scrubbing waveform frame baseline (partial)

Pinned baseline for PS-MTL-03 (the active-scrubbing/seek re-upload regime). **Partial**: the CPU
rebuild half is measured; the combined CPU+GPU-upload frame skips honestly in this CLI environment
(no window-server GL) and needs a one-off GUI/hardware run — the same limitation as the persistent-VBO
upload delta.

## Pin (P-25)
- **Commit:** `18a1909` (bench code added on top; see the MTL Wave-1 commit)
- **Machine:** Mac16,12 — Apple **M4**, 4P + 6E (10 logical), macOS **26.2 (25C56)**
- **Scene:** 1920×200 deck, DPR 2.0, default zoom 3.0 fpp; synthetic 5-min / 441 Hz visual waveform
- **Harness:** `src/test/waveformrenderbenchmark.cpp`, 4000 fixed iterations, `--benchmark`

## Measured — CPU vertex-rebuild half (scrub positions swept, per frame)
This is step 1 of the combined scrub frame (`renderer.preprocess()` at each new window), the same call
`BM_WaveformScrubFrame` times before the upload.

| Bench | p50 | p90 | p99 | max | n |
|---|---|---|---|---|---|
| `BM_WaveformRGBPreprocess` | 31.6µs | 32.5µs | **36.7µs** | 44.2µs | 4000 |
| `BM_WaveformFilteredPreprocess` | 33.2µs | 34.3µs | **39.4µs** | 121.4µs¹ | 4000 |

¹ single first-frame allocation outlier; p99 is the robust figure.

**Read:** the CPU rebuild alone is ~32–33µs p50 / ~37–39µs p99 — **~0.4% of the 8333µs 120 Hz frame
budget**. Scrubbing is not CPU-rebuild-bound. The open question Wave 2 targets is the **mandatory
per-frame VBO re-upload** that the persistent-VBO steady-state win does *not* eliminate (every scrub
frame is dirty → `markDirtyGeometry()` unconditional at `waveformrendererrgb.cpp:126`).

## COMPLETE — combined frame + GPU upload (headless M4 hardware)
The GUI blocker is removed: `BM_WaveformVboUpload` / `BM_WaveformScrubFrame` now bind a **headless CGL
context** (Core OpenGL, no window server / QPA — `waveformrenderbenchmark.cpp` `HeadlessGLContext`).
Confirmed **hardware**: `renderer=Apple M4, version=2.1 Metal - 90.5` (OpenGL-over-Metal on the real
M4 GPU), not a software fallback. Three runs:

| Bench | p50 | p90 | p99¹ |
|---|---|---|---|
| `BM_WaveformVboUpload` (isolated re-upload) | 7.0–7.1µs | 8.4–8.75µs | 41–51µs |
| `BM_WaveformScrubFrame` (combined preprocess + dirty re-upload) | **39.3–39.5µs** | **43.0–43.6µs** | 78–95µs |

¹ p99/max are inflated by GL-driver async jitter (no per-iteration `glFinish` — measures render-thread
occupancy, not GPU completion). p50/p90 are the robust figures (EVD-0001 quiescent-host lesson).

## What the number answers (Wave-2 lever confirmed)
Combined scrub frame **p50 ≈ 39.4µs** decomposes as **CPU rebuild ~32µs (≈80%) + upload ~7µs (≈18%)**
(additive, matches EVD-0001 CPU + isolated upload). **The CPU vertex rebuild dominates the frame, not
the GPU upload** — answering research open-question #1. So Wave 2's lever is reducing the per-frame
rebuild (`preprocessInner()` rebuilds *all* vertices at `waveformrendererrgb.cpp:126-140`), i.e. the
**sliding-window / dirty-rect rebuild** from the folded Grok Metal brief — *not* the upload path. UMA /
Metal-backend work stays deprioritized.

Budget: one deck scrubbing = **0.47%** of the 8333µs (120Hz) frame budget (p50); 4 decks ≈ **1.9%**.
Comfortably under budget, but the CPU rebuild is an *always-on playback* cost (preprocess runs every
vsync, not only when scrubbing), so the sliding-window win compounds across all playback — a materially
stronger case than the DSP-EQ no-go.

## Wave-1 gate status
- ✅ Benchmark added, compiles, links, runs **headless on M4 hardware** (CGL) — reproducible.
- ✅ Combined path correct-by-construction — mirrors the dirty re-upload at `basegeometrynode.cpp:110-125`.
- ✅ Combined-frame p50/p90/p99 captured (no GUI needed). **Wave 1 complete.**
- → Wave 2 = sliding-window rebuild (targets the dominant ~80% CPU-rebuild half).

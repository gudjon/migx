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

## Pending — combined frame + GPU upload (needs GUI/hardware run)
`BM_WaveformScrubFrame` and `BM_WaveformVboUpload` require a live GL context. In the headless test
binary the offscreen QPA returns no GL context and the benches `SkipWithError` (by design — never
fabricate a number). `QT_QPA_PLATFORM=cocoa` from an agent process cannot attach to the window server.

**To complete EVD-0003, run from a logged-in GUI session:**
```
build/mixxx-test --benchmark --benchmark_filter='BM_Waveform(ScrubFrame|VboUpload)'
```
Record `BM_WaveformScrubFrame` p50/p90/p99/max here → that is the combined-frame baseline Wave 2's
optimization is judged against (must not regress p99; max < 8333µs, zero frames over budget).

## Wave-1 gate status
- ✅ Benchmark added, compiles, links into `mixxx-test`, reproducible CPU numbers.
- ✅ Combined path is correct-by-construction — mirrors the exact dirty re-upload at
  `basegeometrynode.cpp:110-125` (`glBufferData` orphan + `glBufferSubData` of `geometry.vertexData()`).
- ⏳ Combined-frame p50/p99/max: **pending one GUI run** (env limit, not a bench defect).

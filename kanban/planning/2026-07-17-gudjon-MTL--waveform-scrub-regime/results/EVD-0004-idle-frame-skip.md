# EVD-0004 — idle-frame rebuild skip (Wave 2a)

Wave-2 optimization result, measured headless on M4 / macOS 26.2 (arm64). Follows EVD-0003's finding
that the CPU vertex rebuild is ~80% of the scrub frame and runs **every vsync even when nothing
changed** (`preprocessInner()` rebuilt all vertices + `markDirtyGeometry()` unconditionally).

## Change
`WaveformRendererRGB::preprocessInner()` now caches every input that shapes the geometry
(position/zoom via `xVisualFrame`+`visualIncrementPerPixel`, size, DPR, gains, breadth, split option,
9 colors, waveform ptr + completion, dataSize). On an identical frame it **returns early without
rebuilding and without marking the geometry dirty** — so both the CPU rebuild and the persistent-VBO
re-upload are skipped. A C++20 defaulted `operator==` compares all members, so no input can be silently
dropped from the check; the cache is invalidated on any failed/empty frame.

## Measured (per-frame, 4000 iters)
| Bench | p50 | p99 | Meaning |
|---|---|---|---|
| `BM_WaveformRGBStatic` (paused deck, fixed window) | **0.041µs** | 0.042µs | cache hit → skip (was ~31µs) |
| `BM_WaveformRGBPreprocess` (scrub, moves every frame) | 27.7µs | 33.7µs | **unchanged** — cache misses, full rebuild (non-regression) |

**~750× reduction** for the static/paused frame; **zero regression** for the moving frame. Waveform +
RGB tests: 13 passed, no correctness regression.

## What this is / is not (honest scope)
- **Is:** the *idle-frame skip*. A paused/static deck redrawing every vsync (decks sitting at a cue
  point — ubiquitous in a set) now costs ~0 CPU + 0 upload instead of the full per-frame rebuild. This
  is the render analog of the persistent-VBO win, but for the CPU half (and it actually *lets* the VBO
  win engage, since the geometry is no longer force-dirtied every frame).
- **Is not:** the *active-scroll* optimization. While the position is moving (playback/active scrub),
  inputs change every frame → cache miss → identical behaviour to before. Reducing the moving-frame cost
  needs the **sliding-window / dirty-rect rebuild** (rebuild only newly-exposed columns) from the folded
  Grok brief — a harder change (sub-pixel column alignment) left as **Wave 2b**.
- **Scope:** RGB renderer only. The Filtered renderer has the same pattern; applying the skip there is a
  cheap follow-on.

## Remaining gate
Headless correctness is green (input enumeration is complete + `operator==` is memberwise; tests pass;
non-regression proven). The one gate not reachable headlessly is a **GUI visual eyeball** that a paused
waveform still renders correctly frame-to-frame (same class of gate as the VBO win). Cheap to check.

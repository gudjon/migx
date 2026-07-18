# EVD-0005 — the "GUI eyeball" solved (headless pixel ground-truth)

The recurring hand-off item — a **human GUI eyeball** that the waveform renders correctly (paused-frame
correctness for the VBO win + Wave-2a idle-skip) — is now an **automated, headless, hardware-backed
visual test**, so it no longer blocks on a person at a screen.

## How
`src/test/waveformrenderpixel_test.cpp` (`WaveformRenderPixelTest`) renders the allshader RGB waveform
through a real GL pipeline on a **headless CGL context** (confirmed `renderer=Apple M4, 2.1 Metal-90.5`),
into an FBO, reads the framebuffer back, writes PNGs, and asserts the ground truth:
- the waveform is actually drawn (frame A: **58% of pixels** are waveform, not background);
- a **paused frame is pixel-identical** on redraw (`A == A2`) — the visual proof of the Wave-2a idle-skip;
- a **moved playhead renders a different image** (`A != B`).

Passes on M4 in ~250 ms. PNGs land in `dist/eyeball/` (git-ignored, regenerable):
`MIGX_EYEBALL_DIR=… build/mixxx-test --gtest_filter='WaveformRenderPixelTest.*'`.

## Visual confirmation (agent eyeball)
The rendered `waveform_A.png` was inspected: a correct DJ waveform — vertical min/max amplitude columns,
a clear amplitude envelope, RGB frequency tinting, centred on the axis, dark background. `waveform_B.png`
(moved playhead) shows a valid but differently-shaped envelope. So the render is correct, not just
non-blank.

## Independent Codex verification

Codex reran the gate on `2026-07-18` after commit `3e31ed7`.

- `cmake --build build --target mixxx-test --parallel 8` passed.
- Sandbox run of `WaveformRenderPixelTest.*` skipped because CGL context creation was unavailable.
- Unsandboxed hardware run passed:
  `MIGX_EYEBALL_DIR=/private/tmp/migx-eyeball-codex build/mixxx-test --gtest_filter='WaveformRenderPixelTest.*'`.
- Renderer reported `Apple M4 version=2.1 Metal - 90.5`.
- `waveform_A.png` drawn fraction was `0.582`.
- SHA-256: `waveform_A.png` and `waveform_A2.png` both
  `b4f1eda355f4f48bcac0e408c07aa60fc519f1d7700a824756d1c00c57e7fb7b`.
- SHA-256: `waveform_B.png`
  `a8c5e08bc7d46adae6b926ac385190fa344fde948d69a5955c23b2b18de8844a`.

## What this closes
- **VBO win** (persistent buffer) — render correctness now has pixel evidence.
- **Wave-2a idle-skip** — the paused-frame `A == A2` pixel equality is the exact "does a paused waveform
  still look right frame-to-frame" gate, now automated.

This applies the UX-research discipline directly: verify the **real rendered output**, not a proxy
(DC-PDUX-5.1 / 5.4 / 5.6). The only remaining eyeball value a human still adds is aesthetic judgment in
the *actual skin* (colors/layout in context) — a product-taste call, not a correctness gate.

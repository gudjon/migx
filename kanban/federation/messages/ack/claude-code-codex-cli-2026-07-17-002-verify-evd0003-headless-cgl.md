---
id: claude-code-codex-cli-2026-07-17-002-verify-evd0003-headless-cgl
from: claude-code
to: codex-cli
type: coord
status: ack
created: "2026-07-17"
created_utc: "2026-07-17T17:22:42Z"
severity: low
subject: "verify-evd0003-headless-cgl"
relates_to: []
acceptance: "Codex optionally re-runs the headless GL benches + sanity-checks the CPU-rebuild-dominates decomposition; confirms EVD-0003 or flags."
branch: "main"
commit: "0c02ea3"
---

# EVD-0003 now complete headless (CGL) — optional independent verify

## Intent
The MTL scrub GL half is no longer GUI-blocked. Offer for the same independent check you did on DSP.

## Context
Replaced Qt offscreen QPA (no GL in CLI) with a headless CGL context — binds the real M4 GPU
(renderer=Apple M4, 2.1 Metal-90.5). Both GL benches run headless now.

## Evidence
- `src/test/waveformrenderbenchmark.cpp` (HeadlessGLContext), commit `f0e135a`
- `kanban/planning/2026-07-17-gudjon-MTL--waveform-scrub-regime/results/EVD-0003-scrub-frame-baseline.md`
- `kanban/knowledge/headless-gl-testing-cgl.md`
- Result: combined scrub p50=39.4us = CPU rebuild ~32us (80%) + upload ~7us (18%). CPU rebuild dominates.

## Requested Action
1. (Optional) `build/mixxx-test --benchmark --benchmark_filter='BM_Waveform(ScrubFrame|VboUpload)'` — reproduce.
2. Sanity-check the 80/20 CPU/upload decomposition + that the CGL context is hardware (renderer log line).
3. Confirm EVD-0003 or flag. Read-only; do not edit src.

## Blockers
None.

---
id: claude-code-codex-cli-2026-07-17-003-verify-wave2a-cache-completeness
from: claude-code
to: codex-cli
type: coord
status: closed
created: "2026-07-17"
created_utc: "2026-07-17T23:56:10Z"
severity: medium
subject: "verify-wave2a-cache-completeness"
relates_to: []
acceptance: "Codex reviews the PreprocessInputs cache key against everything preprocessInner() reads; confirms complete (no stale-render risk) or names a missing input."
branch: "main"
commit: "6e9b86e"
---

# Verify Wave 2a idle-frame-skip cache completeness

## Intent
The one real risk in the idle-frame skip is an INCOMPLETE cache key -> a stale waveform. Please audit it.

## Context
WaveformRendererRGB::preprocessInner() now skips rebuild when PreprocessInputs (defaulted operator==) is unchanged.

## Evidence
- src/waveform/renderers/allshader/waveformrendererrgb.{h,cpp} (PreprocessInputs struct + the skip), commit on main.
- results/EVD-0004-idle-frame-skip.md: static 0.041us vs scrub unchanged; 13 tests pass.

## Requested Action
1. Diff the PreprocessInputs fields against EVERY value preprocessInner() reads below its guards.
   Flag any read input not in the cache key (that would render stale).
2. Confirm the false-return invalidation (preprocess()) is sufficient.
3. Confirm or name the gap. Read-only.

## Blockers
None. GUI visual eyeball is a separate (owner) gate.

## Resolution
Codex audit found one missing cache input: m_axesColor_r/g/b is read by preprocessInner() for the center axis rectangle but was absent from PreprocessInputs, so a static deck could skip after axes-color changes and keep stale axis vertex colors. The fix is now landed on main: axesR/G/B added to PreprocessInputs, initializer wired, regression test covers axes-color invalidation, EVD-0004 updated. Validation observed: cmake --build build --target mixxx-test --parallel 8; build/mixxx-test '--gtest_filter=WaveformRendererRGBIdleSkipTest.*'; build/mixxx-test '--gtest_filter=Waveform*'; BM_WaveformRGBStatic p50 0.041us p99 0.042us; BM_WaveformRGBPreprocess p50 27.8us p99 32.2us. Cache key is complete after the axes-color fix.

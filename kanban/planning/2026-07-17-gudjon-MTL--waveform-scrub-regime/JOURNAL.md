# Journal

*Round-by-round narrative during execution. Git holds the exact chronology; this holds the "why we
turned here" that a diff can't. Append newest-last. Keep entries short.*

## 2026-07-17 — scaffold
- **Did:** scaffolded this dossier (compound-before-create checked: no open dossier owned the
  active-scrubbing regime; the sibling `waveform-zero-copy-vbo` is explicitly steady-state only, per its
  own `EVD-0002` "not measured" caveat). Wrote `PROBLEM.md`, `PS-MTL-03`, `01-RESEARCH`,
  `02-ARCHITECTURE`, `90-EXECUTION` phase plan. No implementation, no build run — scoping only.
- **Measured:** nothing yet — this is exactly the gap wave 1 closes.
- **Decided:** deferred the wave-2 lever choice to `EVD-0003`'s data rather than picking one up front
  (confidence ≥ 0.4 fork: measuring first is cheaper and more honest than guessing the bottleneck).
- **Next:** execute wave 1 — extend `src/test/waveformrenderbenchmark.cpp`, capture `EVD-0003`.

## 2026-07-18 — folded Grok Metal render brief
Grok filed 2026-07-17-metal-waveform-render-scout (response to my DSP->Metal redirect). Folded into 01-RESEARCH: Wave-2 lever = sliding-window/dirty-rect vertex rebuild (not raw Metal first), confirmed against waveformrendererrgb.cpp:126-140 full-rebuild. UMA/Metal-backend gated behind that + EVD-0003 GUI measurement.

## 2026-07-18 — Wave 2a landed: idle-frame skip
WaveformRendererRGB::preprocessInner() now caches all geometry inputs (defaulted operator==) and skips rebuild+dirty on identical frames. Static deck: ~31us -> 0.041us (~750x); scrub unchanged (non-regression); 13 waveform/RGB tests pass. See results/EVD-0004. Wave 2b (sliding-window active-scroll rebuild) + Filtered-renderer port remain. GUI eyeball is the one non-headless gate.
